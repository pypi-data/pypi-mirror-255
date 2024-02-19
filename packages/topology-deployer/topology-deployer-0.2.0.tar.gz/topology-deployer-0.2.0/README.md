![build](https://github.com/vpatel95/topology-deployer/actions/workflows/python-app.yml/badge.svg)

# topology-deployer
Python tool to deploy topologies on Ubuntu from the defined json config files.

## Table of Contents
1. [Prerequisites](#prereq)
2. [User Guide](#usage)
    1. [Create Topology](#create)
    2. [Delete Topology](#delete)
    3. [Verbosity](#verbose)
4. [JSON Topology Config](#json_conf)
    1. [JSON Network Config](#json_nw)
    2. [JSON Virtual Machine Config](#json_vm)

## Prerequisites <a name = "prereq"></a>

Run `./install`

## User Guide <a name = "usage"></a>

### Installation
Install from Python Package Index

```
sudo pip3 install topology-deployer
```

To install from source

```
sudo pip3 install .
```

### Options
Parse topology config

```
optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        JSON Config file that defines the topology
  -o {create,delete,CREATE,DELETE}, --operation {create,delete,CREATE,DELETE}
                        Operation to create or delete topology from the JSON Config
  -i {ubuntu,rocky}, --image {ubuntu,rocky}
                        Choose the base OS image for the VMS
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the log level
  --dry-run             Instead of executing, print the commands
  --skip-network        Skip creating networks. Cannot be used with --skip-vm
  --skip-vm             Skip creating vms. Cannot be used with --skip-network
```

### Creating Topologies <a name = "create"></a>
A JSON cofig is taken as input. Check [here](#json_conf) for guide to define config

```
sudo topology-deployer -c config.json -o create -i ubuntu -l INFO
```

To skip creating networks. It can be used woth delete too. (This is _BETA_ feature. Not fully tested)
```
sudo topology-deployer -c config.json -o create -i ubuntu -l INFO --skip-network
```

To skip creating virtual machines. It can be used woth delete too. (This is _BETA_ feature. Not fully tested)

```
sudo topology-deployer -c config.json -o create -i ubuntu -l INFO --skip-vm
```

### Deleting Topologies <a name = "delete"></a>
Same JSON cofig used to create topology is taken as input.

```
sudo topology-deployer -c config.json -o delete -l INFO
```

### Verbosity <a name = "verbose"></a>
To print verbose output for created networks

```
sudo topology-deployer --print-nw -c config.json -o create
```

To print verbose output for created virtual machines

```
sudo topology-deployer --print-vm -c config.json -o create
```


## JSON Config <a name = "json_conf">
The json config to define topologies comprises of 2 sections.
1. Networks
2. Virtual Machines

```json
{
    "version" : 2,
    "networks" : [],
    "vms" : []
}
```

### JSON Network Config <a name = "json_nw"></a>
The JSON network object comprises of array of networks. A network object skeleton is shown below

```json
{
    "networks" : [
        {
            "name" : "<name>",
            "type" : "<nat | management | isolated>",
            "subnet4" : "<ipv4 subnet>",
            "subnet6" : "<ipv6 subnet>"
        }
    ],
}
```

#### Add NAT network in JSON network object
For nat network, `name` and `subnet4` are mandatory fields. `subnet6` is optional in case you need v6 network in your topology. To have multiple NAT networks, you can add multiple objects in the networks.nat json object.

```json
{
    "networks" : [
        {
            "name" : "<name>",
            "type" : "nat",
            "subnet4" : "<ipv4 subnet>",
            "subnet6" : "<ipv6 subnet>"
        }
    ]
}
```

#### Add Management network in JSON network object
For management network, `name` and `subnet4` are mandatory fields. Currently we do not support v6 management network. To have multiple NAT networks, you can add multiple objects in the networks.management json object.

```json
{
    "networks" : [
        {
            "name" : "<name>",
            "type" : "management",
            "subnet4" : "<ipv4 subnet>"
        }
    ]
}
```

#### Add Isolated network in JSON network object
For isolated network, `name` is mandatory fields. To have multiple NAT networks, you can add multiple objects in the networks.isolated json object.

```json
{
    "networks" : [
        {
            "name" : "<name>",
            "type" : "management"
        }
    ]
}
```

### JSON Virtual Machine Config <a name = "json_vm"></a>
The vms object is array of multiple vm objects. For the vm object on the JSON config, `name`, `flavor`, `vnc_port` and `networks` are mandatory fields. You can optionally use `ram`, `vcpus` and `disk` to override the defaults for the flavor. A vms object skeleton is shown below

```json
{
    "vms" : [{
        "name" : "",
        "flavor" : "",
        "vnc_port" : "",
        "networks" : {
            "<nw_name1>" : {
                "v4" : ""
            },
            "<nw_name2>" : {
                "v4" : "",
                "v6" : ""
            }
        }
    }]
}
```

To define networks for the vm, you have to use the network name as key and provide `v4` address. You can also add a `v6` address if the network type is NAT.

If you want to customize the resources for your VM you can use the `vcpus`, `ram` and `disk` keys. Example
```json
{
    "vms" : [{
        "name" : "",
        "flavor" : "",
        "vcpus" : 10,
        "ram" : 8192,
        "disk" : "128G",
        "vnc_port" : "",
        "networks" : {
            "<nw_name1>" : {
                "v4" : ""
            },
            "<nw_name2>" : {
                "v4" : "",
                "v6" : ""
            }
        }
    }]
}
```
## Sample Topology Configurations

1. [2PE-CE](topologies/evpn-2pe.json)
2. [2PE-2PSWITCH-2CE](topologies/sr-mpls.json)
