import os
import re
import shutil
import socket
import subprocess as sp
from pathlib import Path
from signal import SIGINT
from threading import Thread
from typing import Union

from lumipy import config, get_client
from lumipy.provider.common import get_dll_path, get_latest_local_semver, get_certs_path, find_dotnet_sdks
from lumipy.provider.common import max_version
from ..common import red_print, emph_print


def ensure_directory(
        domain: str,
        sdk_version: Union[str, None],
        dev_path: Union[str, None],
        skip_checks: bool
) -> Path:

    # This is a test where the factory is just constructed and not run.
    if skip_checks:
        return Path('/some/test/path')

    find_dotnet_sdks()

    # We are developing against a locally-compiled version.
    if dev_path:
        return Path(dev_path)

    # Get version if there's a valid one present. Returns None if missing.
    if sdk_version is None:
        sdk_version = get_latest_local_semver()

    c = get_client(domain)

    get_certs = len(list(get_certs_path(domain).glob('*'))) != 2
    get_binaries = sdk_version is None
    if get_certs or get_binaries:
        print('Setting up python providers. 🛠')

    # If certs are missing download them
    if get_certs:
        c.download_certs()

    # If the sdk version is still none download the binaries
    if get_binaries:
        c.download_binary('Python_Providers', str(max_version))

    # Look for a valid version again now it's downloaded.
    # If it's still none here we can't continue. In a state that shouldn't happen.
    sdk_version = get_latest_local_semver()
    if sdk_version is None:
        raise ValueError('No valid dlls after dll setup. An unexpected problem has occurred.')

    return get_dll_path(sdk_version) / 'tools' / 'net6.0' / 'any'


def machine_name():
    if os.name == 'nt':
        return os.environ['COMPUTERNAME']
    else:
        return socket.gethostname().split('.')[0]


class Factory:
    """This class encapsulates a process that manages the python provider factory dotnet application

    """

    def __init__(
            self,
            host: str,
            port: int,
            user: Union[str, None],
            domain: Union[str, None],
            whitelist_me: bool,
            _fbn_run: bool,
            _sdk_version: str = None,
            _skip_checks: bool = False,
            _dev_dll_path: Union[str, None] = None
    ):
        """Constructor of the Factory class

        Args:
            host (str): the host that the target api server is running at
            port (int): the port that the target api server is exposed at
            user (str): who can user the provider. Can be a user ID, 'global' or None (opens a login window).
            domain (str): which finbourne domain to run in such as fbn-ci (internal), fbn-qa (internal) or fbn-prd.
            _fbn_run (bool): finbourne-internal option for an alternative rabbitMQ authentication when running in K8s.
            _sdk_version (str): version number of sdk to use when developing against version other than the default.

        """
        if re.match('^[\w._-]+$', host) is None:
            raise ValueError(f"Invalid value for host: {host}")

        if not isinstance(port, int):
            raise ValueError(f"Port number must be an integer. Was {type(port).__name__} ({port})")

        self.domain = config.domain if domain is None else domain
        if self.domain is None:
            raise ValueError(
                f'Please set the domain by:\n'
                '  ProviderManager(p, domain="your domain")\n'
                'or adding it to lumipy config\n'
                '  import lumipy as lm\n'
                '  lm.config.add("your domain", "your token")'
            )
        if re.match('^[\w_-]+$', domain) is None:
            raise ValueError(f"Invalid value for domain: {domain}")

        self.base_path = ensure_directory(domain, _sdk_version, _dev_dll_path, _skip_checks)

        self.cmd = f'dotnet {self.base_path / "Finbourne.Honeycomb.Host.dll"} --quiet --authClientDomain={domain} ' \
                   f'--config "PythonProvider:BaseUrl=>http://{host}:{port}/api/v1/" '

        if user is not None and user != 'global':
            self.cmd += f'--localRoutingUserId "{user}" '
        elif user is not None and user == 'global':
            if not whitelist_me:
                raise ValueError('You must whitelist yourself by setting whitelist_me = True')

            red_print(f'🚨 Warning: machine name "{machine_name()}" is whitelisted. Providers are running globally 🚨')
            self.cmd += f'--routeAs:Global "DataProvider:RoutingTypeGlobalMachineWhitelist=>{machine_name()}" '

        if _fbn_run:
            self.cmd += '"Metrics:Enabled=>true" '
            self.cmd += '"NameServiceClient:RabbitConfigFile=>honeycomb-rabbit-config-plain.json" '
            self.cmd += '"NameServiceClient:RabbitUserPassword->/usr/app/secrets/service-main" '

        self.starting = True
        self.process = None
        self.print_thread = Thread(target=self.__print_process_output)
        self.errored = False

    def start(self):
        """Start the factory process. This will block the program while the setup is running.

        """
        emph_print(f'Starting python provider factory in {self.domain}')

        for cert in self.base_path.glob('*.pem'):
            cert.unlink()

        os.makedirs(self.base_path, exist_ok=True)
        for cert in get_certs_path(self.domain).glob('*.pem'):
            shutil.copy2(cert, self.base_path / cert.parts[-1])

        print(self.cmd, end='\n\n')

        self.process = sp.Popen(self.cmd.split(), shell=False, stdout=sp.PIPE, stderr=sp.PIPE)

        self.print_thread.start()

        while self.starting:
            pass

        self.errored = self.process.poll() is not None

        if self.errored:
            self.print_thread.join()

    def stop(self):
        """Stop the factory process and shut down the providers. This will block the program while the termination is
        completing.

        """
        if self.process.poll() is not None:
            # no-op
            return

        emph_print('\nStopping python provider factory')

        if os.name == 'nt':
            self.process.terminate()
        else:
            self.process.send_signal(SIGINT)

        while self.process.poll() is None:
            pass

        self.print_thread.join()

    def __print_process_output(self):

        # Set a loop running in another thread that periodically polls the process
        # When there's a new line of output print it
        # If the process is in exit state, set block=False so the stop method stops blocking

        bad_lines = 0
        while self.process.poll() is None:

            output = self.process.stdout.readline().decode('utf-8', errors="replace").rstrip()

            if output:
                print(output)

            if 'RemoteCancellation: ResubscribeAsync failed with' in output:
                bad_lines += 1
            else:
                # reset count in case it's a blip
                bad_lines = 0

            if bad_lines > 50:
                self.errored = True
                break

            if 'Running! Hit Ctrl+C to shut down services' in output:
                self.starting = False
