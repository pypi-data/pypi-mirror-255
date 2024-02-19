import random

from .utils import ExecuteCommand, ExecuteCommandWithOutput


def CheckForwarding() -> None:
    cmd = "cat /proc/sys/net/ipv4/ip_forward"
    if ExecuteCommandWithOutput(cmd) != "1":
        ExecuteCommand("sudo sh -c 'echo \"net.ipv4.ip_forward=1\" >> /etc/sysctl.conf'")

    cmd = "cat /proc/sys/net/ipv4/conf/all/forwarding"
    if ExecuteCommandWithOutput(cmd) != "1":
        ExecuteCommand("sudo sh -c 'echo \"net.ipv4.conf.all.forwarding=1\" >> /etc/sysctl.conf'")

    cmd = "cat /proc/sys/net/ipv6/conf/all/forwarding"
    if ExecuteCommandWithOutput(cmd) != "1":
        ExecuteCommand("sudo sh -c 'echo \"net.ipv6.conf.all.forwarding=1\" >> /etc/sysctl.conf'")

    ExecuteCommand("sudo sysctl -p")


def GetMacAddress() -> str:
    mac = "52:54:00:%02x:%02x:%02x" % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255))

    return mac


def AddLinuxBridge(name: str, ip4: str, ip6: str, plen4: int, plen6: int) -> None:
    mac_address = GetMacAddress()
    dummy_intf = "{}-nic".format(name)
    ExecuteCommand("sudo ip link add {} address {} type dummy".format(dummy_intf, mac_address))
    ExecuteCommand("sudo brctl addbr {}".format(name))
    ExecuteCommand("sudo brctl stp {} on".format(name))
    ExecuteCommand("sudo brctl addif {} {}".format(name, dummy_intf))
    ExecuteCommand("sudo ip address add {}/{} dev {}".format(ip4, plen4, name))
    if ip6 != "None":
        ExecuteCommand("sudo ip -6 address add {}/{} dev {}".format(ip6, plen6, name))
    ExecuteCommand("sudo ip link set dev {} up".format(dummy_intf))
    ExecuteCommand("sudo ip link set dev {} up".format(name))


def DelLinuxBridge(name):
    dummy_intf = f"{name}-nic"
    ExecuteCommand(f"sudo ip link set dev {dummy_intf} down")
    ExecuteCommand(f"sudo ip link set dev {name} down")
    ExecuteCommand(f"sudo ip link del {dummy_intf}")
    ExecuteCommand(f"sudo ip link del {name}")


def AddDelIptableRules(op, name, nw4):
    ExecuteCommand(f"sudo iptables -t mangle -{op} POSTROUTING -o {name} -p udp "
                   "-m udp --dport 68 -j CHECKSUM --checksum-fill")
    ExecuteCommand(f"sudo iptables -t nat -{op} POSTROUTING -s {nw4} -d 224.0.0.0/24 -j RETURN")
    ExecuteCommand(f"sudo iptables -t nat -{op} POSTROUTING -s {nw4} -d "
                   "255.255.255.255/32 -j RETURN")
    ExecuteCommand(f"sudo iptables -t nat -{op} POSTROUTING -s {nw4} ! -d {nw4} "
                   "-p tcp -j MASQUERADE --to-ports 1024-65535")
    ExecuteCommand(f"sudo iptables -t nat -{op} POSTROUTING -s {nw4} ! -d {nw4} "
                   "-p udp -j MASQUERADE --to-ports 1024-65535")
    ExecuteCommand(f"sudo iptables -t nat -{op} POSTROUTING -s {nw4} ! -d {nw4} -j MASQUERADE")
    ExecuteCommand(f"sudo iptables -t filter -{op} INPUT -i {name} -p udp -m udp "
                   "-m multiport --dports 53,67 -j ACCEPT")
    ExecuteCommand(f"sudo iptables -t filter -{op} INPUT -i {name} -p tcp -m tcp "
                   "-m multiport --dports 53,67 -j ACCEPT")
    ExecuteCommand(f"sudo iptables -t filter -{op} FORWARD -d {nw4} -o {name} -j ACCEPT")
    ExecuteCommand(f"sudo iptables -t filter -{op} FORWARD -s {nw4} -i {name} -j ACCEPT")
    ExecuteCommand(f"sudo iptables -t filter -{op} FORWARD -i {name} -j ACCEPT")
    ExecuteCommand(f"sudo iptables -t filter -{op} FORWARD -o {name} -j ACCEPT")
    ExecuteCommand("sudo sh -c 'iptables-save > /etc/iptables/rules.v4'")
