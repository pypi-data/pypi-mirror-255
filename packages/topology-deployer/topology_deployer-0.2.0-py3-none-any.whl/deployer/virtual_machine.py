import sys
import logging
import yaml
import ipaddress

import deployer.globals as G
from deployer.globals import LIBVIRT_IMAGES, VM_FLAVORS
from deployer.topology import Topology
from deployer.utils import ExecuteCommand


class VirtualMachine:
    name_ = ""
    vnc_port_ = -1
    user_data_cfg_ = ""
    network_data_cfg_ = ""
    root_disk_ = ""
    cloud_init_iso_ = ""
    networks_ = {}
    flavor_ = "pe"
    vcpus_ = 8
    ram_ = 16384
    root_disk_sz_ = "80G"
    topology_ = Topology()

    def __new__(cls, conf):
        if not VirtualMachine._validate_vm_config(conf):
            return None
        return super(VirtualMachine, cls).__new__(cls)
    # end __new__

    def __init__(self, conf):
        self.name_ = conf["name"]
        self.flavor_ = conf["flavor"]
        self.vnc_port_ = int(conf["vnc_port"])
        self.libvirt_vm_base = LIBVIRT_IMAGES.joinpath(self.name_)
        self.user_data_cfg_ = self.libvirt_vm_base.joinpath("user-data.cfg")
        self.network_data_cfg_ = self.libvirt_vm_base.joinpath("nw-data.cfg")
        self.root_disk_ = self.libvirt_vm_base.joinpath("root_disk.qcow2")
        self.cloud_init_iso_ = self.libvirt_vm_base.joinpath("cloud-init.iso")

        self.libvirt_vm_base.mkdir(parents=True, exist_ok=True)
        self.networks_ = conf["networks"]

        if self.flavor_ == "ce":
            self.vcpus_ = 8
            self.ram_ = 8192
            self.root_disk_sz_ = "40G"
        elif self.flavor_ == "pe":
            self.vcpus_ = 8
            self.ram_ = 16384
            self.root_disk_sz_ = "80G"
        elif self.flavor_ == "dev":
            self.vcpus_ = 32
            self.ram_ = 65536
            self.root_disk_sz_ = "320G"

        if conf.get("vcpus", None) is not None:
            self.vcpus_ = int(conf["vcpus"])

        if conf.get("ram", None) is not None:
            self.ram_ = int(conf["ram"])

        if conf.get("disk", None) is not None:
            self.root_disk_sz_ = conf["disk"]
    # end __init__

    @staticmethod
    def _has_valid_vm_fields(vm):
        name = vm.get("name", None)
        if not name or not isinstance(name, str):
            logging.critical("'name' is required key in vm config")
            return False

        networks = vm.get("networks", None)
        if not networks or not isinstance(networks, dict):
            logging.critical("'networks' is required key in vm config")
            return False

        vnc_port = vm.get("vnc_port", None)
        if not vnc_port or not isinstance(vnc_port, int) or vnc_port < 5900:
            logging.critical("'vnc_port' is required key in vm config")
            return False

        flavor = vm.get("flavor", None)
        vcpus = vm.get("vcpus", None)
        ram = vm.get("ram", None)
        disk = vm.get("disk", None)

        if not flavor:
            if not vcpus or not ram or not disk:
                logging.critical("'vcpu', 'ram' and 'disk' are mandatory if"
                                 " 'flavor' is not provided")
                return False
        else:
            if flavor not in VM_FLAVORS:
                logging.critical("Invalid VM flavor")
                return False

        if vcpus == 0 or ram == 0:
            logging.critical("'vcpu' or 'ram' is expected to be number >= 1")
            return False

        if disk == "":
            logging.critical("'disk' is expected to be non empty string")
            return False

        if vcpus and (not isinstance(vcpus, int) or vcpus < 1):
            logging.critical("'vcpu' is expected to be number >= 1")
            return False

        if ram and (not isinstance(ram, int) or ram < 1024):
            logging.critical("'ram' is expected to be number >= 1024")
            return False

        if disk and not isinstance(disk, str):
            logging.critical("'disk' is expected to be in str format")
            return False

        return True
    # end _has_valid_vm_fields

    @staticmethod
    def _validate_vm_network_config(nws):
        for name, ips in nws.items():
            network = VirtualMachine.Topology().GetNetwork(name)

            if network is None:
                logging.critical(f"Network {name} not found")
                return False

            if network.IsIsolated():
                return True

            try:
                ip4 = ipaddress.IPv4Address(ips["v4"])
                ip6 = None
                if ips.get("v6", None) is not None:
                    ip6 = ipaddress.ip_address(ips["v6"])
            except Exception as e:
                logging.error("Invalid Subnet(s). Please check again : ", e)
                return False

            # check if IP in IP Network
            if ip4 not in network.network4_:
                logging.error(f"{ip4} is not in {str(network.network4_)}")
                return False
            if ip6 and network.network6_:
                if ip6 not in network.network6_:
                    logging.error(f"{ip6} is not in {str(network.network6_)}")
                    return False

        return True
    # end _validate_vm_network_config

    @staticmethod
    def _validate_vm_config(vm):
        if not VirtualMachine._has_valid_vm_fields(vm):
            return False

        if not VirtualMachine._validate_vm_network_config(vm["networks"]):
            return False

        return True
    # end _validate_vm_config

    @staticmethod
    def Topology():
        return VirtualMachine.topology_
    # end Topology

    def __generate_cloud_init_config(self):
        cloud_init = {
            "system_info": {
                "default_user": {
                    "name": G.BASE_OS,
                    "home": f"/home/{G.BASE_OS}"
                },
            },
            "password": G.BASE_OS,
            "chpasswd": {
                "expire": False
            },
            "hostname": f"{self.name_}-node",
            "ssh_pwauth": True
        }

        with open(self.user_data_cfg_, "w") as cloud_init_f:
            cloud_init_f.write("#cloud-config\n")
            yaml.dump(cloud_init, cloud_init_f, sort_keys=False)
            cloud_init_f.write("")
    # end __generate_cloud_init_config

    def __get_ubuntu_params(self):
        network_config = {
            "network": {
                "version": 2,
                "ethernets": {}
            }
        }
        interface_config = network_config["network"]["ethernets"]
        index = 1
        intf_fmt = "enp{}s0"
        return [network_config, interface_config, intf_fmt, index]
    # end __get_ubuntu_params

    def __get_rocky_params(self):
        network_config = {
            "version": 2,
            "ethernets": {}
        }
        interface_config = network_config["ethernets"]
        index = 0
        intf_fmt = "eth{}"
        return [network_config, interface_config, intf_fmt, index]
    # end __get_rocky_params

    def __get_os_based_params(self):
        if G.BASE_OS == "rocky":
            return self.__get_rocky_params()
        elif G.BASE_OS == "ubuntu":
            return self.__get_ubuntu_params()

        return [None, None, None, None]
    # end __get_os_based_params

    def __generate_netplan_config(self):
        network_config, interface_config, intf_fmt, index = self.__get_os_based_params()

        if ((network_config is None) or
                (interface_config is None) or
                (intf_fmt is None) or
                (index is None)):
            logging.critical("Error fetching os based network params")
            sys.exit(4)

        for nw in self.networks_:
            intf_name = intf_fmt.format(index)
            network = VirtualMachine.Topology().GetNetwork(nw)

            if network is None:
                logging.critical(f"Network {nw} not found")
                sys.exit(4)

            ip4 = self.networks_[nw].get("v4", None)
            ip6 = self.networks_[nw].get("v6", None)

            if network.IsManagement():
                interface_config[intf_name] = self.__generate_mgmt_config(ip4, network)
            elif network.IsNat():
                interface_config[intf_name] = self.__generate_nat_config(ip4, ip6, network)
            elif network.IsIsolated():
                interface_config[intf_name] = self.__generate_iso_config(ip4, ip6)
            index = index + 1

        with open(self.network_data_cfg_, "w") as nw_config_f:
            nw_config_f.write("#network-config\n")
            yaml.dump(network_config, nw_config_f, sort_keys=False)
    # end __generate_netplan_config

    def __generate_mgmt_config(self, ip4, nw):
        addr = ""
        if nw.network4_ is not None:
            addr = "{}/{}".format(ip4, nw.network4_.prefixlen)
        mgmt_nw_config = {
            "addresses": [addr],
            "routes": [{
                "to": str(nw.network4_),
                "via": str(nw.ip4_)
            }]
        }
        return mgmt_nw_config
    # end __generate_mgmt_config

    def __generate_nat_config(self, ip4, ip6, nw):
        addresses = []

        if nw.network4_ is not None:
            addresses.append(f"{ip4}/{nw.network4_.prefixlen}") if ip4 is not None else None

        if nw.network6_ is not None:
            addresses.append(f"{ip6}/{nw.network6_.prefixlen}") if ip6 is not None else None

        nat_nw_config = {
            "addresses": addresses,
            "nameservers": {
                "addresses": ['66.129.233.81', '10.84.5.101', '172.21.200.60'],
                "search": ['jnpr.net', 'juniper.net', 'englab.juniper.net']
            },
            "gateway4": str(nw.ip4_),
        }

        if nw.network6_ is not None:
            nat_nw_config["gateway6"] = str(nw.ip6_)

        return nat_nw_config
    # end __generate_nat_config

    def __generate_iso_config(self, ip4, ip6):
        addresses = []
        routes = []

        if ip4 is not None:
            addresses.append(f"{ip4}/24")
            nw = ipaddress.IPv4Network(f"{ip4}/24", strict=False)
            routes.append({
                "to": str(nw),
                "scope": "link"
            })

        if ip6 is not None:
            addresses.append(f"{ip6}/120")
            nw = ipaddress.IPv6Network(f"{ip6}/120", strict=False)
            routes.append({
                "to": str(nw),
                "scope": "link"
            })

        iso_nw_config = {
            "addresses": addresses,
            "routes": routes
        }
        return iso_nw_config
    # end __generate_iso_config

    def __create_root_disk(self):
        cmd = f"sudo qemu-img convert -f qcow2 -O qcow2 {G.OS_IMAGE_TEMPLATE} {self.root_disk_}"
        ExecuteCommand(cmd)

        cmd = f"sudo qemu-img resize {self.root_disk_} {self.root_disk_sz_}"
        ExecuteCommand(cmd)
    # end __create_root_disk

    def __generate_cloud_init_iso(self):
        cmd = f"sudo cloud-localds -N {self.network_data_cfg_} "\
                f"{self.cloud_init_iso_} {self.user_data_cfg_}"
        ExecuteCommand(cmd)
    # end __generate_cloud_init_iso

    def __execute_virt_install_cmd(self):
        name_arg = f"--name {self.name_}"
        graphic_arg = f"--graphics vnc,listen=0.0.0.0,port={self.vnc_port_}"
        root_disk_arg = f"--disk path={self.root_disk_},bus=virtio,format=qcow2"
        cloud_init_arg = f"--disk {self.cloud_init_iso_},device=cdrom"
        cpu_ram_arg = f"--vcpus {self.vcpus_} --ram {self.ram_}"

        network_args = ""
        for nw in self.networks_:
            tmp_nw_cfg = f"--network bridge={nw},model=virtio "
            network_args += tmp_nw_cfg

        os_var = ""
        if G.BASE_OS == "ubuntu":
            os_var = "ubuntu20.04"
        elif G.BASE_OS == "rocky":
            os_var = "rhel8.0"

        cmd = f"sudo virt-install --virt-type kvm --os-variant {os_var} " \
              f"{name_arg} {cpu_ram_arg} {graphic_arg} " \
              f"{root_disk_arg} {cloud_init_arg} {network_args} " \
              "--noautoconsole --import"
        ExecuteCommand(cmd)
    # end __execute_virt_install_cmd

    def Create(self):
        logging.info(f"Creating Virtual Machine : {self.name_}")

        self.__generate_cloud_init_config()
        self.__generate_netplan_config()
        self.__create_root_disk()
        self.__generate_cloud_init_iso()

        self.__execute_virt_install_cmd()
    # end Create

    def Delete(self):
        logging.info(f"Deleting Virtual Machine : {self.name_}")

        cmd = f"sudo virsh destroy {self.name_}"
        ExecuteCommand(cmd)

        cmd = f"sudo virsh undefine --remove-all-storage {self.name_}"
        ExecuteCommand(cmd)
    # end Delete

    def __str__(self):
        vm_str = ""
        vm_str += f"Flavor : {self.flavor_}\n"
        vm_str += f"VNC : {self.vnc_port_}\n"
        vm_str += "Networks : \n"
        for nw, ips in self.networks_.items():
            ip4 = ips.get("v4", None)
            ip6 = ips.get("v6", None)
            vm_str += f"\t{nw} :\n\t\tv4 : {ip4}\n\t\tv6 : {ip6}\n"
        vm_str += "===================================\n"
        return vm_str
    # end __str__
