import patrol
import requests
import subprocess

SAFE_LIST = ["GB"]
UNSAFE_IP_LIST = []

ip_list = patrol.main()
process_list = requests.get("https://api.oceanlord.me/ip/info", json={"addresses": ip_list})

if process_list.status_code != 200:
    print(process_list.status_code, process_list.text)
    exit()

for ip_address in list(process_list.json().keys()):
    if ip_address not in UNSAFE_IP_LIST:
        if process_list.json()[ip_address]["country_code"] not in SAFE_LIST and not process_list.json()[ip_address]["private"]:
            UNSAFE_IP_LIST.append(ip_address)


static_info = ["\n", "####### This section was created by a program to block irritating IP's", "\n"]
hosts_file_contents = []

line_counter = 0
info_line = 0
hosts_file_storage = []
BACKED_UP_IP_LIST = []

with open("/etc/hosts.deny") as file:
    for line in file:
        if static_info[1] in line:
            info_line = line_counter
            break
        else:
            hosts_file_storage.append(line)
            line_counter += 1
    line_counter = 0
    for line in file:
        if line_counter > info_line:
            temp_line = line.strip()
            if temp_line != "":
                BACKED_UP_IP_LIST.append(temp_line)
        else:
            line_counter += 1


with open("/etc/hosts.deny", "w") as file:
    for line in hosts_file_storage:
        file.write(line)
    for line in static_info:
        file.write(line)
    for ip in UNSAFE_IP_LIST:
        file.write("sshd: {}\n".format(ip))
    for ip in BACKED_UP_IP_LIST:
        file.write("{}\n".format(ip))

subprocess.call("sudo service sshd restart", shell=True)
