import logging
import sys

import deployer.globals as globals


class Topology:
    networks_ = {}
    vms_ = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Topology, cls).__new__(cls)
        return cls.instance

    def AddNetwork(self, name, nw):
        if self.__is_existing_network(name):
            logging.error(f"Network {name} already exists")
            sys.exit(2)

        self.networks_[name] = nw
    # end AddNetwork

    def AddVm(self, name, vm):
        if self.__is_existing_vm(name):
            logging.error(f"Virtual Machine {name} already exists")
            sys.exit(2)

        self.vms_[name] = vm
    # end AddVm

    def Delete(self):
        if not globals.NO_VM:
            self.__delete_vms()

        if not globals.NO_NETWORK:
            self.__delete_networks()
    # end Delete

    def Create(self):
        if not globals.NO_NETWORK:
            self.__create_networks()

        if not globals.NO_VM:
            self.__create_vms()

        # Add Print Topology here
    # end __create

    def GetNetwork(self, name):
        return self.networks_.get(name, None)
    # end GetNetwork

    def Networks(self):
        return self.networks_.items()
    # end Networks

    def Vms(self):
        return self.vms_.items()
    # end Vms

    def __create_networks(self):
        for _, nw in self.networks_.items():
            nw.Create()
    # end __create_networks

    def __create_vms(self):
        for _, vm in self.vms_.items():
            vm.Create()
    # end __create_vms

    def __delete_networks(self):
        for _, nw in self.networks_.items():
            nw.Delete()
    # end __delete_networks

    def __delete_vms(self):
        for _, vm in self.vms_.items():
            vm.Delete()
    # end __delete_vms

    def __is_existing_network(self, name):
        nw = self.networks_.get(name, None)
        if nw is None:
            return False
        return True
    # end __is_existing_network

    def __is_existing_vm(self, name):
        vm = self.vms_.get(name, None)
        if vm is None:
            return False
        return True
    # end __is_existing_vm
