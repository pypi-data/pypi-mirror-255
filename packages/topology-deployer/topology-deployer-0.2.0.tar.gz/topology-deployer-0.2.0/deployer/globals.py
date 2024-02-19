from pathlib import Path

OP_CREATE = 1
OP_DELETE = 2
OP = OP_CREATE

DRY_RUN = False
NO_NETWORK = False
NO_VM = False

NETWORK_TYPES = ["nat", "isolated", "management"]
VM_FLAVORS = ["pe", "ce", "dev"]

LIBVIRT_BASE_PATH = Path('/var/lib/libvirt')
LIBVIRT_IMAGES = LIBVIRT_BASE_PATH.joinpath('images')
LIBVIRT_TEMPLATES = LIBVIRT_IMAGES.joinpath('templates')
LIBVIRT_QEMU_BASE = Path('/etc/libvirt/qemu')
LIBVIRT_QEMU_NW = LIBVIRT_QEMU_BASE.joinpath('networks')

BASE_OS = "ubuntu"
UBUNTU_TEMPLATE = LIBVIRT_TEMPLATES.joinpath('ubuntu-22.04-server.qcow2')
ROCKY_TEMPLATE = LIBVIRT_TEMPLATES.joinpath('rocky-8.qcow2')
OS_IMAGE_TEMPLATE = UBUNTU_TEMPLATE

NAT_NW_BASE = Path.home().joinpath('.topology/bridges')
