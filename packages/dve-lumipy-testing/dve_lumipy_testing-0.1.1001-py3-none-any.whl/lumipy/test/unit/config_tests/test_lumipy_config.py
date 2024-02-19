import unittest
from lumipy._config_manager import ConfigManager
from pathlib import Path
import tempfile
import shutil


class TestLumipyConfig(unittest.TestCase):

    test_base_dir = Path(tempfile.gettempdir()) / 'lumipy_cfg_tests'

    @classmethod
    def setUpClass(cls) -> None:
        if cls.test_base_dir.exists():
            shutil.rmtree(cls.test_base_dir)
        cls.test_base_dir.mkdir()

    def test_top_level_config_object(self):
        import lumipy as lm

        cfg = lm.config
        self.assertIsInstance(cfg, ConfigManager)

        self.assertEqual('.lumipy', cfg.hidden_dir)
        self.assertEqual('auth', cfg.filename)

        expected = Path.home() / cfg.hidden_dir / cfg.filename
        self.assertEqual(expected, cfg.cfg_file)

    def test_empty_file_creation_on_obj_creation(self):

        test_dir = self.test_base_dir / 'config0'
        cfg_path = test_dir / ConfigManager.hidden_dir / ConfigManager.filename

        # Make sure it's not there
        cfg_path.unlink(missing_ok=True)

        cfg = ConfigManager(test_dir)
        self.assertTrue(cfg_path.exists())
        self.assertEqual(0, len(cfg._read()))

        self.assertIn('No domain PATs configured. Add one with the config.add() method.', str(cfg))
        self.assertIn('Call config.show() to peek at part of the PATs', str(cfg))
        self.assertIn('No domain PATs configured. Add one with the config.add() method.', repr(cfg))
        self.assertIn('Call config.show() to peek at part of the PATs', repr(cfg))

    def test_add_domain_happy(self):

        test_dir = self.test_base_dir / 'config1'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))

        cfg.add('fbn-fake', 'token1')

        self.assertEqual(1, len(cfg._read()))
        self.assertEqual(cfg.creds('fbn-fake')['token'], 'token1')

        for s in ['fbn-fake', '[PAT hidden]', '(active)']:
            self.assertIn(s, str(cfg))
            self.assertIn(s, repr(cfg))

        cfg.add('fbn-fake', 'token2', overwrite=True)
        self.assertEqual(cfg.creds('fbn-fake')['token'], 'token2')

    def test_add_domain_unhappy(self):

        test_dir = self.test_base_dir / 'config9'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))

        cfg.add('fbn-fake', 'token1')

        with self.assertRaises(ValueError) as ve:
            cfg.add('fbn-fake', 'token2')
            s = str(ve.exception)
            self.assertIn('Set overwrite=True to overwrite it.', s)

    def test_switch_domain_happy(self):

        test_dir = self.test_base_dir / 'config2'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))

        cfg.add('fbn-dom1', 'token1')
        cfg.add('fbn-dom2', 'token2')

        self.assertEqual(2, len(cfg._read()))
        self.assertEqual('fbn-dom1', cfg.domain)
        cfg.domain = 'fbn-dom2'
        self.assertEqual('fbn-dom2', cfg.domain)

    def test_switch_domain_unhappy(self):

        test_dir = self.test_base_dir / 'config3'
        cfg = ConfigManager(test_dir)

        with self.assertRaises(ValueError) as ve:
            cfg.domain = 'fbn-bad'
            s = str(ve.exception)
            self.assertIn('fbn-bad', s)
            self.assertEqual('not found in config. You can add it with', s)
            self.assertEqual('config.add("fbn-bad", <PAT>)', s)

    def test_get_domain(self):

        test_dir = self.test_base_dir / 'config4'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))
        self.assertIsNone(cfg.domain)

        cfg.add('fbn-dom1', 'token1')
        self.assertEqual('fbn-dom1', cfg.domain)

    def test_get_creds_happy(self):

        test_dir = self.test_base_dir / 'config5'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))
        c0 = cfg.creds()
        self.assertIsInstance(c0, dict)
        self.assertEqual(0, len(c0))

        cfg.add('fbn-dom1', 'token1')
        cfg.add('fbn-dom2', 'token2')

        c1 = cfg.creds()
        self.assertEqual('https://fbn-dom1.lusid.com/honeycomb', c1['api_url'])
        self.assertEqual('token1', c1['token'])

        c2 = cfg.creds('fbn-dom2')
        self.assertEqual('https://fbn-dom2.lusid.com/honeycomb', c2['api_url'])
        self.assertEqual('token2', c2['token'])

    def test_get_creds_unhappy(self):

        test_dir = self.test_base_dir / 'config6'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))

        with self.assertRaises(ValueError) as ve:
            cfg.creds('fbn-bad')
            s = str(ve.exception)
            self.assertIn('fbn-bad', s)
            self.assertEqual('not found in config. You can add it with', s)
            self.assertEqual('config.add("fbn-bad", <PAT>)', s)

    def test_delete_domain_happy(self):

        test_dir = self.test_base_dir / 'config7'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))
        c0 = cfg.creds()
        self.assertIsInstance(c0, dict)
        self.assertEqual(0, len(c0))

        cfg.add('fbn-dom1', 'token1')
        cfg.add('fbn-dom2', 'token2')
        self.assertEqual(2, len(cfg._read()))

        cfg.delete('fbn-dom2')
        self.assertEqual(1, len(cfg._read()))

    def test_delete_domain_unhappy(self):

        test_dir = self.test_base_dir / 'config8'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))
        c0 = cfg.creds()
        self.assertIsInstance(c0, dict)
        self.assertEqual(0, len(c0))

        cfg.add('fbn-dom1', 'token1')

        with self.assertRaises(ValueError) as ve:
            cfg.delete('fbn-dom1')
            s = str(ve.exception)
            self.assertIn(
                "fbn-dom1 is the current active domain. Please switch to a different one before deleting.",
                s
            )

        with self.assertRaises(ValueError) as ve:
            cfg.delete('fbn-bad')
            s = str(ve.exception)
            self.assertIn('fbn-bad', s)
            self.assertEqual('not found in config. You can add it with', s)
            self.assertEqual('config.add("fbn-bad", <PAT>)', s)

    def test_deactivate(self):

        test_dir = self.test_base_dir / 'config10'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))

        cfg.deactivate()
        self.assertEqual(0, len(cfg._read()))

        cfg.add('fbn-dom1', 'abcdefg')
        cfg.add('fbn-dom2', 'hijklmn')

        self.assertEqual('fbn-dom1', cfg.domain)

        cfg.deactivate()
        self.assertIsNone(cfg.domain)
