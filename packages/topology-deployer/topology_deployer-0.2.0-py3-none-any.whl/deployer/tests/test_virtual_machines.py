import logging
import unittest
from unittest import mock

import deployer
import deployer.topology
from deployer.network import Network
from deployer.virtual_machine import VirtualMachine


class TestVirtualMachine(unittest.TestCase):
    def setUp(self):
        self.vm_ = None
        self.iso_nw_ = Network({
            "name": "iso1",
            "type": "isolated"
        })
        self.mgmt_nw_ = Network({
            "name": "mgmt1",
            "type": "management",
            "subnet4": "10.1.1.0/24",
        })
        self.nat_nw_ = Network({
            "name": "nat1",
            "type": "nat",
            "subnet4": "20.1.1.0/24",
            "subnet6": "1234::20.1.1.0/120",
        })
        self.mgmt_conf_ = {"v4": "10.1.1.1"}
        self.nat_conf_ = {"v4": "20.1.1.1", "v6": "1234::20.1.1.1"}
        self.iso_conf_ = {"v4": "30.1.1.1", "v6": "1234::30.1.1.1"}
        self.vm_conf_ = {
            "name": "vm1",
            "networks": {
                "mgmt1": self.mgmt_conf_,
                "nat1": self.nat_conf_,
                "iso1": self.iso_conf_
            },
            "vnc_port": 5900,
            "flavor": "pe",
            "vcpus": 8,
            "ram": 16384,
            "disk": "80G"
        }
        logging.basicConfig(level="INFO")

        # Mocking os.mkdir() method
        self.mkdir_patcher = mock.patch('pathlib.PosixPath.mkdir')
        self.mock_mkdir = self.mkdir_patcher.start()

        # Mocking the Topology.GetNetwork() method
        def get_network(name):
            if name == "mgmt1":
                return self.mgmt_nw_
            elif name == "nat1":
                return self.nat_nw_
            elif name == "iso1":
                return self.iso_nw_
            else:
                return None
        # end get_network

        self.topo_getnw_patcher = mock.patch.object(deployer.topology.Topology, 'GetNetwork')
        self.mock_topo_getnw = self.topo_getnw_patcher.start()
        self.mock_topo_getnw.side_effect = get_network

    def tearDown(self):
        self.topo_getnw_patcher.stop()
        self.mock_mkdir = self.mkdir_patcher.stop()

    def test_name_validity(self):
        # Test empty name. It should fail
        self.vm_conf_["name"] = ""
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test non string name. It should fail
        self.vm_conf_["name"] = {}
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        self.vm_conf_["name"] = 10
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test valid name. It should pass
        self.vm_conf_["name"] = "vm1"
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

    def test_networks_validity(self):
        # Test empty networks. It should fail
        self.vm_conf_["networks"] = {}
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test non dict networks. It should fail
        self.vm_conf_["networks"] = ""
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test valid networks. It should pass
        self.vm_conf_["networks"] = {"mgmt": {"v4": ""}}
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

    def test_vnc_port_validity(self):
        # Test empty vnc_port. It should fail
        self.vm_conf_["vnc_port"] = ""
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test non int vnc_port. It should fail
        self.vm_conf_["vnc_port"] = "5900"
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test vnc_port < 5900. It should fail
        self.vm_conf_["vnc_port"] = 5899
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test valid vnc_port. It should pass
        self.vm_conf_["vnc_port"] = 5900
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

    def test_flavor_validity(self):
        # Test empty flavor. It should pass as vcpus, ram and disk are not empty
        self.vm_conf_["flavor"] = ""
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

        # Delete vcpus from the dict. Empty flavor should fail
        del self.vm_conf_["vcpus"]
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)
        self.vm_conf_["vcpus"] = 8

        # Test non string flavor. It should fail
        self.vm_conf_["flavor"] = 10
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test flavor not in VM_FLAVORS. It should fail
        self.vm_conf_["flavor"] = "test"
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test valid flavor. It should pass
        self.vm_conf_["flavor"] = "pe"
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

    def test_vcpus_validity(self):
        # Empty vcpu with valid flavor. It should pass
        del self.vm_conf_["vcpus"]
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

        # Test empty vcpus. It should pass
        self.vm_conf_["vcpus"] = ""
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

        # Test non int vcpus. It should fail
        self.vm_conf_["vcpus"] = "8"
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test vcpus < 1. It should fail
        self.vm_conf_["vcpus"] = 0
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test valid vcpus. It should pass
        self.vm_conf_["vcpus"] = 8
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

    def test_ram_validity(self):
        # Empty ram with valid flavor. It should pass
        del self.vm_conf_["ram"]
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

        # Test empty ram. It should pass
        self.vm_conf_["ram"] = ""
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

        # Test non int ram. It should fail
        self.vm_conf_["ram"] = "16384"
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test ram < 1. It should fail
        self.vm_conf_["ram"] = 0
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test valid ram. It should pass
        self.vm_conf_["ram"] = 16384
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

    def test_disk_validity(self):
        # Empty disk with valid flavor. It should pass
        del self.vm_conf_["disk"]
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

        # Test empty disk. It should pass
        self.vm_conf_["disk"] = ""
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test non string disk. It should fail
        self.vm_conf_["disk"] = 80
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertFalse(ok)

        # Test valid disk. It should pass
        self.vm_conf_["disk"] = "80G"
        ok = VirtualMachine._has_valid_vm_fields(self.vm_conf_)
        self.assertTrue(ok)

    def test_add_pe_virtual_machine(self):
        self.vm_ = VirtualMachine(self.vm_conf_)
        self.mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        self.assertEqual(self.vm_.name_, "vm1")
        self.assertEqual(self.vm_.vnc_port_, 5900)
        self.assertEqual(self.vm_.flavor_, "pe")
        self.assertEqual(self.vm_.vcpus_, 8)
        self.assertEqual(self.vm_.ram_, 16384)
        self.assertEqual(self.vm_.root_disk_sz_, "80G")
        self.assertEqual(self.vm_.networks_, {
            "mgmt1": self.mgmt_conf_,
            "nat1": self.nat_conf_,
            "iso1": self.iso_conf_
        })
        self.assertEqual(str(self.vm_.user_data_cfg_),
                         "/var/lib/libvirt/images/vm1/user-data.cfg")
        self.assertEqual(str(self.vm_.network_data_cfg_),
                         "/var/lib/libvirt/images/vm1/nw-data.cfg")
        self.assertEqual(str(self.vm_.root_disk_),
                         "/var/lib/libvirt/images/vm1/root_disk.qcow2")
        self.assertEqual(str(self.vm_.cloud_init_iso_),
                         "/var/lib/libvirt/images/vm1/cloud-init.iso")
        self.assertEqual(str(self.vm_.libvirt_vm_base),
                         "/var/lib/libvirt/images/vm1")

    def test_add_ce_virtual_machine(self):
        self.vm_conf_["flavor"] = "ce"
        del self.vm_conf_["disk"]
        del self.vm_conf_["ram"]
        del self.vm_conf_["vcpus"]
        self.vm_ = VirtualMachine(self.vm_conf_)
        self.mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        self.assertEqual(self.vm_.name_, "vm1")
        self.assertEqual(self.vm_.vnc_port_, 5900)
        self.assertEqual(self.vm_.flavor_, "ce")
        self.assertEqual(self.vm_.vcpus_, 8)
        self.assertEqual(self.vm_.ram_, 8192)
        self.assertEqual(self.vm_.root_disk_sz_, "40G")
        self.assertEqual(self.vm_.networks_, {
            "mgmt1": self.mgmt_conf_,
            "nat1": self.nat_conf_,
            "iso1": self.iso_conf_
        })
        self.assertEqual(str(self.vm_.user_data_cfg_),
                         "/var/lib/libvirt/images/vm1/user-data.cfg")
        self.assertEqual(str(self.vm_.network_data_cfg_),
                         "/var/lib/libvirt/images/vm1/nw-data.cfg")
        self.assertEqual(str(self.vm_.root_disk_),
                         "/var/lib/libvirt/images/vm1/root_disk.qcow2")
        self.assertEqual(str(self.vm_.cloud_init_iso_),
                         "/var/lib/libvirt/images/vm1/cloud-init.iso")
        self.assertEqual(str(self.vm_.libvirt_vm_base),
                         "/var/lib/libvirt/images/vm1")
