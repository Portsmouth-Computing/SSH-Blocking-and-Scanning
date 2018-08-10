import patrol
import requests
import subprocess

SAFE_LIST = ["GB"]
UNSAFE_IP_LIST = []

ip_list = patrol.main()
process_list = requests.post("http://178.128.167.133:880/ip/list", json={"ip_list": ip_list})

for item in process_list.json()["ip_list"]:
    if item not in UNSAFE_IP_LIST:
        if item["country"] not in SAFE_LIST:
            UNSAFE_IP_LIST.append(item["ip"]["compressed"])


static_info = ["\n", "####### This section was created by a program to block irritating IP's", "\n"]
hosts_file_contents = []

line_counter = 0
info_line = 0
hosts_file_storage = []

with open("/etc/hosts.deny") as file:
    for line in file:
        if static_info[1] in line:
            info_line = line_counter
            break
        else:
            hosts_file_storage.append(line)
            line_counter += 1

with open("/etc/hosts.deny", "w") as file:
    for line in hosts_file_storage:
        file.write(line)
    for line in static_info:
        file.write(line)
    for ip in UNSAFE_IP_LIST:
        file.write(ip)

subprocess.call("sudo service sshd restart", shell=True)