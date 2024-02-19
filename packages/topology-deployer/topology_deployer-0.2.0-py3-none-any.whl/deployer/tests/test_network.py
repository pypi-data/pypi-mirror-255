import ipaddress
import logging
from socket import AddressFamily
import unittest
from unittest import mock

import deployer
import deployer.topology
import deployer.globals as G
from deployer.network import Network


class TestNetwork(unittest.TestCase):
    def setUp(self):
        G.OP = G.OP_CREATE
        self.nw_ = {"name": "test-nw", "type": "isolated"}
        logging.basicConfig(level="ERROR")

        # Mocking the psutil.net_if_addrs() method
        self.mocked_intf_ = [
            ('em1', AddressFamily.AF_INET, '20.20.1.1', '255.255.255.0', None, None),
            ('em1', AddressFamily.AF_INET6, '1234::1414:101',
                'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ff00', None, None),
            ('em1', AddressFamily.AF_PACKET, '52:54:00:aa:bb:cc', None, None, None)
        ]
        self.net_if_addr_patcher = mock.patch('psutil._psplatform.net_if_addrs')
        self.mock_net_if_addrs = self.net_if_addr_patcher.start()
        self.mock_net_if_addrs.return_value = self.mocked_intf_

        self.dummy_nw_ = Network({
            "name": "dummy-nw",
            "type": "nat",
            "subnet4": "11.11.11.0/24",
            "subnet6": "1234::11.11.11.0/120"
        })

        # Mocking the Topology.Networks() method
        self.mocked_topo_nw_ = {
            "dummy-nw": self.dummy_nw_
        }.items()
        self.topo_nw_patcher = mock.patch.object(deployer.topology.Topology, 'Networks')
        self.mock_topo_nw = self.topo_nw_patcher.start()
        self.mock_topo_nw.return_value = self.mocked_topo_nw_

    def tearDown(self):
        self.net_if_addr_patcher.stop()
        self.topo_nw_patcher.stop()

    def test_network_isolated_type(self):
        ok = Network._validate_network_conf(self.nw_)
        self.assertTrue(ok)

    def test_network_management_type(self):
        self.nw_["type"] = "management"
        self.nw_["subnet4"] = "10.10.1.0/24"

        ok = Network._has_valid_network_fields(self.nw_)
        self.assertTrue(ok)

    def test_network_nat_type(self):
        self.nw_["type"] = "nat"
        self.nw_["subnet4"] = "10.10.1.0/24"

        ok = Network._has_valid_network_fields(self.nw_)
        self.assertTrue(ok)

        self.nw_["subnet6"] = "1234::10.10.1.0/24"
        ok = Network._has_valid_network_fields(self.nw_)
        self.assertTrue(ok)

    def test_network_required_subnet4(self):
        self.nw_["type"] = "nat"
        self.nw_["subnet6"] = "1234::10.10.1.0/24"

        ok = Network._has_valid_network_fields(self.nw_)
        self.assertFalse(ok)

        self.nw_["type"] = "management"
        ok = Network._has_valid_network_fields(self.nw_)
        self.assertFalse(ok)

    def test_validate_non_colliding_network_in_sys_v4(self):
        self.nw_["type"] = "nat"
        self.nw_["subnet4"] = "10.10.1.0/24"

        ok = Network._validate_network_conf(self.nw_)
        self.assertTrue(ok)

    def test_validate_colliding_network_in_sys_v4(self):
        self.nw_["type"] = "nat"
        self.nw_["subnet4"] = "20.20.1.0/24"

        ok = Network._validate_network_conf(self.nw_)
        self.assertFalse(ok)

    def test_validate_non_colliding_network_in_sys_v6(self):
        self.nw_["type"] = "nat"
        self.nw_["subnet4"] = "10.10.1.0/24"
        self.nw_["subnet6"] = "1234::10.10.1.0/120"

        ok = Network._validate_network_conf(self.nw_)
        self.assertTrue(ok)

    def test_validate_colliding_network_in_sys_v6(self):
        self.nw_["type"] = "nat"
        self.nw_["subnet4"] = "10.10.1.0/24"
        self.nw_["subnet6"] = "1234::20.20.1.0/120"

        ok = Network._validate_network_conf(self.nw_)
        self.assertFalse(ok)

    def test_validate_non_colliding_network_in_config_v4(self):
        self.nw_["type"] = "nat"
        self.nw_["subnet4"] = "10.10.1.0/24"

        ok = Network._validate_network_conf(self.nw_)
        self.assertTrue(ok)

    def test_validate_colliding_network_in_config_v4(self):
        self.nw_["type"] = "nat"
        self.nw_["subnet4"] = "11.11.11.0/24"

        ok = Network._validate_network_conf(self.nw_)
        self.assertFalse(ok)

    def test_validate_non_colliding_network_in_config_v6(self):
        self.nw_["type"] = "nat"
        self.nw_["subnet4"] = "10.10.1.0/24"
        self.nw_["subnet6"] = "1234::10.10.1.0/120"

        ok = Network._validate_network_conf(self.nw_)
        self.assertTrue(ok)

    def test_validate_colliding_network_in_config_v6(self):
        self.nw_["type"] = "nat"
        self.nw_["subnet4"] = "11.11.11.0/24"
        self.nw_["subnet6"] = "1234::11.11.11.0/120"

        ok = Network._validate_network_conf(self.nw_)
        self.assertFalse(ok)

    def test_add_v4_network(self):
        v4_nw_conf = {
            "name": "nw1",
            "type": "nat",
            "subnet4": "12.12.12.0/24"
        }
        v4_nw = Network(v4_nw_conf)
        self.assertEqual(v4_nw.network4_, ipaddress.IPv4Network('12.12.12.0/24'))
        self.assertEqual(v4_nw.ip4_, ipaddress.IPv4Network('12.12.12.0/24')[1])
        self.assertEqual(v4_nw.network6_, None)
        self.assertEqual(v4_nw.ip6_, None)

    def test_add_v6_network(self):
        nw_conf = {
            "name": "nw1",
            "type": "nat",
            "subnet4": "12.12.12.0/24",
            "subnet6": "1234::12.12.12.0/120"
        }
        nw1 = Network(nw_conf)
        self.assertEqual(nw1.network4_, ipaddress.IPv4Network('12.12.12.0/24'))
        self.assertEqual(nw1.ip4_, ipaddress.IPv4Network('12.12.12.0/24')[1])
        self.assertEqual(nw1.network6_, ipaddress.IPv6Network('1234::12.12.12.0/120'))
        self.assertEqual(nw1.ip6_, ipaddress.IPv6Network('1234::12.12.12.0/120')[1])
