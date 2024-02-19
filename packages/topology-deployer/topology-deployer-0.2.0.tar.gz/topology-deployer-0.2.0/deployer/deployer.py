import logging
import sys

import deployer.globals as G
from deployer.network import Network
from deployer.topology import Topology
from deployer.utils import ProcessArguments
from deployer.virtual_machine import VirtualMachine


class Deployer:
    config_ = {}
    topology_ = Topology()

    def __init__(self, config):
        self.config_ = config
    # end __init__

    def _is_valid_version(self):
        if self.config_ is None:
            logging.error(f"Empty config : {self.config_}")
            return False

        if self.config_.get("version", None) is None:
            logging.error("This looks like older version of config which is "
                          " supported only by 0.0.x version")
            return False

        if self.config_["version"] != 2:
            logging.error("This version supports only version 2 of config")
            return False

        return True
    # end _is_valid_version

    def _parse_networks(self):
        nw_configs = self.config_.get("networks", None)

        if nw_configs is None:
            logging.error("No network config found. Exiting")
            return False

        if not isinstance(nw_configs, list):
            logging.error("'network' config should be a list")
            return False

        if len(nw_configs) == 0:
            logging.error("'network' config cannot be empty list")
            return False

        for nw_conf in nw_configs:
            name = nw_conf["name"]
            nw = Network(nw_conf)
            if nw is None:
                return False
            self.Topology().AddNetwork(name, nw)

        return True
    # end _parse_networks

    def _parse_vms(self):
        vm_configs = self.config_.get("vms", None)

        if vm_configs is None:
            logging.error("No VMs config found. Exiting")
            return False

        if not isinstance(vm_configs, list):
            logging.error("'vms' config should be a list")
            return False

        if len(vm_configs) == 0:
            logging.error("'vms' config cannot be empty list")
            return False

        for vm_conf in vm_configs:
            name = vm_conf["name"]
            vm = VirtualMachine(vm_conf)
            if vm is None:
                return False
            self.Topology().AddVm(name, vm)

        return True
    # end _parse_vms

    def ParseConfig(self):
        if not self._is_valid_version():
            return False

        if not self._parse_networks():
            return False

        if not self._parse_vms():
            return False

        return True
    # end ParseConfig

    def Topology(self):
        return self.topology_
    # end Topology

# end Deployer


def topology_deployer():
    config = ProcessArguments(sys.argv[1:])
    tDeployer = Deployer(config)
    if not tDeployer.ParseConfig():
        sys.exit(1)

    topology = tDeployer.Topology()

    if G.OP == G.OP_CREATE:
        topology.Create()
    elif G.OP == G.OP_DELETE:
        topology.Delete()
    else:
        logging.error(f"Invalid operation {G.OP}")
        sys.exit(1)
