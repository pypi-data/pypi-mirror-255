import argparse
import json
import logging
import shlex
import subprocess
import sys

import deployer.globals as G
from .globals import OP_CREATE, OP_DELETE, ROCKY_TEMPLATE, UBUNTU_TEMPLATE


def ProcessArguments(cli_args):
    parser = argparse.ArgumentParser(description="Parse topology config")

    parser.add_argument("-c", "--config", required=True,
                        help="JSON Config file that defines the topology")

    parser.add_argument("-o", "--operation", type=str, required=True,
                        choices=["create", "delete", "CREATE", "DELETE"], default="create",
                        help="Operation to create or delete topology from the JSON Config")

    parser.add_argument("-i", "--image", type=str, required=True,
                        choices=["ubuntu", "rocky"], default="ubuntu",
                        help="Choose the base OS image for the VMS")

    parser.add_argument("-l", "--log", type=str, default="ERROR",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the log level")
    parser.add_argument("--dry-run", action="store_true",
                        help="Instead of executing, print the commands")

    skip_operation = parser.add_mutually_exclusive_group()
    skip_operation.add_argument("--skip-network", action="store_true",
                                help="Skip creating networks. Cannot be used with --skip-vm")
    skip_operation.add_argument("--skip-vm", action="store_true",
                                help="Skip creating vms. Cannot be used with --skip-network")

    args = parser.parse_args(cli_args)

    if args.log:
        log_level = getattr(logging, args.log.upper(), None)
        if not isinstance(log_level, int):
            raise ValueError(f"Invalid log level: {args.log}")
        logging.basicConfig(level=log_level)

    if args.dry_run:
        G.DRY_RUN = args.dry_run

    if args.operation.upper() == "CREATE":
        G.OP = OP_CREATE
    else:
        G.OP = OP_DELETE

    if args.skip_network:
        G.NO_NETWORK = args.skip_network

    if args.skip_vm:
        G.NO_VM = args.skip_vm

    if args.image.lower() == "ubuntu":
        G.BASE_OS = "ubuntu"
        G.OS_IMAGE_TEMPLATE = UBUNTU_TEMPLATE
    elif args.image.lower() == "rocky":
        G.BASE_OS = "rocky"
        G.OS_IMAGE_TEMPLATE = ROCKY_TEMPLATE
    else:
        logging.critical("Invalid image argument")
        sys.exit(1)

    with open(args.config) as conf_file:
        config = json.load(conf_file)

    return config


def ExecuteCommand(cmd):
    if not G.DRY_RUN:
        logging.info(f"Executing command : {cmd}")
        ret = subprocess.call(shlex.split(cmd))
        if ret != 0:
            logging.error(f"Command {cmd} failed wih return code : {ret}")
            sys.exit(ret)
    else:
        logging.debug(f"Dry Run enabled. Command : {cmd}")


def ExecuteCommandWithOutput(cmd):
    logging.info(f"Executing command : {cmd}")
    res = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        logging.error(f"Command {cmd} failed wih return code : {res.returncode}")
        logging.error(f"Error message : {res.stderr}")
        sys.exit(res.returncode)
    return res.stdout.decode('utf-8').strip()
