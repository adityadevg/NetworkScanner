import subnet_util
import concurrent.futures
import netifaces
import os
import ipaddress

local_ip, local_interface = netifaces.gateways()['default'][netifaces.AF_INET]
local_address_info = [netifaces.ifaddresses(local_interface)[addr][0]
                      for addr in netifaces.ifaddresses(local_interface)]


def ping_host(host_ip):
    response = os.system(f"ping -c 1 {host_ip} >/dev/null 2>&1")
    if response == 0:
        print(f"{host_ip} is up")
        return host_ip
    return


for entry in local_address_info:
    try:
        addr = ipaddress.ip_address(entry.get('addr', '').split("%")[0])
    except ValueError:
        continue
    netmask = entry.get('netmask', '')
    if netmask:
        cidr = int(subnet_util.convert_subnet(netmask, subnet_util.SubnetNotation.CIDR))
        print(f"[+] Starting Ping Sweeper using {addr}/{cidr} on {local_interface} interface")
        with concurrent.futures.ThreadPoolExecutor(max_workers=255) as executor:
            future_results = {executor.submit(ping_host, ip): ip
                              for ip in ipaddress.ip_network(f"{addr}/{cidr}", False)}
