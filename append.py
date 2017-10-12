import platform, os

if platform.system() != "Linux":
    print("This code only works on Linux/Debian at the moment.")
    exit()

if os.geteuid() != 0:
    print("Please run as sudo.")
    exit()
else:
    print("Running as sudo.")

staticInfo = ["\n","####### This section was created by a program to block irritating IP's","\n"]

username = os.getlogin()

hosts_file = []
hosts_counter = 0
with open("/etc/hosts.deny") as hosts_filea:
    for line in hosts_filea:
        if hosts_counter != 17:
            hosts_file.append("{}\n".format(line.strip()))
            hosts_counter += 1
        else:
            break

sshd_ip_list = []
with open("./ip_raw.txt") as rawIPs:
    for line in rawIPs:
        sshd_ip_list.append("{}\n".format(line.strip()))

tempList = []

for line in hosts_file:
    tempList.append(line)
for line in staticInfo:
    tempList.append(line)
for line in sshd_ip_list:
    tempList.append(line)

with open("/etc/hosts.deny", "w") as hosts_filea:
    for line in tempList:
        hosts_filea.write(line)
