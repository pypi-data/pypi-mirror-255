import logging
import unittest

from deployer.deployer import Deployer


class TestDeployer(unittest.TestCase):
    def setUp(self):
        self.config_ = {"version": 2, "networks": [], "vms": []}
        self.deployer_ = Deployer(self.config_)
        logging.basicConfig(level='CRITICAL')

    def tearDown(self):
        del self.deployer_

    def test_valid_version(self):
        ok = self.deployer_._is_valid_version()
        self.assertTrue(ok)

    def test_invalid_version(self):
        self.deployer_.config_ = {"version": 3, "networks": [], "vms": []}
        ok = self.deployer_._is_valid_version()
        self.assertFalse(ok)

    def test_missing_version(self):
        self.deployer_.config_ = {"networks": [], "vms": []}
        ok = self.deployer_._is_valid_version()
        self.assertFalse(ok)

    def test_parse_empty_networks(self):
        ok = self.deployer_._parse_networks()
        self.assertFalse(ok)

    def test_parse_non_list_networks(self):
        self.deployer_.config_['networks'] = {}
        ok = self.deployer_._parse_networks()
        self.assertFalse(ok)

    def test_parse_missing_networks(self):
        del self.deployer_.config_['networks']
        ok = self.deployer_._parse_networks()
        self.assertFalse(ok)

    def test_parse_vms(self):
        ok = self.deployer_._parse_vms()
        self.assertFalse(ok)

    def test_parse_non_list_vms(self):
        self.deployer_.config_['vms'] = {}
        ok = self.deployer_._parse_vms()
        self.assertFalse(ok)

    def test_parse_missing_vms(self):
        del self.deployer_.config_['vms']
        ok = self.deployer_._parse_vms()
        self.assertFalse(ok)
