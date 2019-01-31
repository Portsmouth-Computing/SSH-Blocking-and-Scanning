import re
import subprocess

import requests

import patrol

SAFE_LIST = ["GB"]
UNSAFE_IP_LIST = []
re_luma = re.compile(r'(?P<address>(?:[a-f\d]{1,4}[\.:]){1,7}[a-f\d]{1,4})')
static_info = ["\n", "####### This section was created by a program to block irritating IP's", "\n"]
hosts_file_contents = []
line_counter = 0
info_line = 0
hosts_file_storage = []
BACKED_UP_IP_LIST = []

ip_list = patrol.main()
print("IP LIST")
print(ip_list)
print(len(ip_list))

with open("/etc/hosts.deny") as file:
    for line in file:
        if static_info[1] in line:
            info_line = line_counter
            break
        else:
            hosts_file_storage.append(line)
            line_counter += 1
with open("/etc/hosts.deny") as file:
    line_counter = 0
    for line in file:
        if line_counter > info_line:
            temp_line = line.strip()
            if temp_line != "":
                try:
                    ip = re_luma.search(temp_line)
                    BACKED_UP_IP_LIST.append(ip.group("address"))
                except AttributeError:
                    print(temp_line, re_luma.search(temp_line))
        else:
            line_counter += 1
print("BACKED UP")
print(sorted(BACKED_UP_IP_LIST))
print(len(BACKED_UP_IP_LIST))

improved_ip_list = []
for ip in ip_list:
    if ip not in BACKED_UP_IP_LIST:
        improved_ip_list.append(ip)

process_list = requests.get("https://api.oceanlord.me/ip/info", json={"addresses": improved_ip_list})

if process_list.status_code != 200:
    print(process_list.status_code, process_list.text)
    exit()

for ip_address in list(process_list.json().keys()):
    if ip_address not in UNSAFE_IP_LIST:
        if process_list.json()[ip_address]["country_code"] not in SAFE_LIST and not process_list.json()[ip_address]["private"]:
            UNSAFE_IP_LIST.append(ip_address)

SET_IP_LIST = set(BACKED_UP_IP_LIST + UNSAFE_IP_LIST)
print("SET IP")
print(len(SET_IP_LIST))
temp_ip = []
for ip in ip_list:
    if ip not in BACKED_UP_IP_LIST:
        temp_ip.append(ip)
print(len(temp_ip))
with open("/etc/hosts.deny", "w") as file:
    for line in hosts_file_storage:
        file.write(line)
    for line in static_info:
        file.write(line)
    for ip in SET_IP_LIST:
        file.write("sshd: {}\n".format(ip))

subprocess.call("sudo service sshd restart", shell=True)
