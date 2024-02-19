import unittest
from lumipy.provider.factory import Factory


class TestProviderFactory(unittest.TestCase):

    def test_provider_factory_ctor_happy(self):
        fact = Factory(
            host='localhost',
            port=5464,
            user='TESTUSER',
            domain='test-domain',
            whitelist_me=True,
            _skip_checks=True,
            _fbn_run=False,
        )

        self.assertEqual('test-domain', fact.domain)
        self.assertFalse(fact.errored)
        self.assertIsNone(fact.process)
        self.assertTrue(fact.starting)

        self.assertIn('--authClientDomain=test-domain', fact.cmd)
        self.assertIn('--localRoutingUserId "TESTUSER"', fact.cmd)
        self.assertIn('--config "PythonProvider:BaseUrl=>http://localhost:5464/api/v1/"', fact.cmd)

    def test_provider_factory_ctor_unhappy(self):
        with self.assertRaises(ValueError):
            Factory(host='$(bad stuff)', port=1234, user='user', domain='dom', whitelist_me=False, _fbn_run=False)

        with self.assertRaises(ValueError):
            Factory(host='127.0.0.1', port="ABC", user='user', domain='dom', whitelist_me=False, _fbn_run=False)
