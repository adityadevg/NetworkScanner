import socket
import netifaces
import subprocess


def ping_ip_address(ip_address):
    command = ['ping', '-c', '1', '-W', '1', ip_address]
    result = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result == 0


def get_hostname(ip_address):
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        return hostname
    except socket.herror:
        return None


def get_local_ip_addresses():
    ip_addresses = []

    # Get a list of network interfaces
    interfaces = netifaces.interfaces()

    for interface in interfaces:
        # Check if the interface is up and not a loopback or virtual interface
        if netifaces.ifaddresses(interface) and netifaces.ifaddresses(interface).get(netifaces.AF_INET):
            addresses = netifaces.ifaddresses(interface)[netifaces.AF_INET]

            for address_info in addresses:
                ip_address = address_info['addr']

                # Exclude loopback and link-local addresses
                if not ip_address.startswith('127.') and not ip_address.startswith('169.254.'):
                    ip_addresses.append((interface, ip_address))

    return ip_addresses


def get_local_subnet_ip_addresses(subnet):
    ip_addresses = []

    subnet_parts = subnet.split('.')
    base_ip = subnet_parts[:3]

    for i in range(1, 256):
        ip_address = '.'.join(base_ip + [str(i)])
        ip_addresses.append(ip_address)

    return ip_addresses


# Usage example
local_ips = get_local_ip_addresses()

for interface, ip in local_ips:
    reachable = ping_ip_address(ip)
    hostname = get_hostname(ip)
    if hostname:
        print(f"Interface: {interface} - IP: {ip} - Hostname: {hostname} - Reachable: {reachable}")
    else:
        print(f"Interface: {interface} - IP: {ip} - Unable to resolve hostname - Reachable: {reachable}")
    subnet = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['netmask']
    subnet = '.'.join(str(int(subnet.split('.')[i]) & int(ip.split('.')[i])) for i in range(4))
    subnet += '/24'

    subnet_ips = get_local_subnet_ip_addresses(subnet)

    for ip in subnet_ips:
        reachable = ping_ip_address(ip)
        hostname = get_hostname(ip)
        if reachable:
            print(f"Interface: {interface} - IP: {ip} - Hostname: {hostname} - Reachable: {reachable}")
