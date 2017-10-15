import os, pickle, requests, subprocess

if os.geteuid() != 0:
    exit()

username = os.getlogin()

working_dir = "/root/SSH-Blocking-and-Scanning/".format(username)
working_file = "/root/SSH-Blocking-and-Scanning/auth_scanning.pickle".format(username)
ip_tracker_file = "/root/SSH-Blocking-and-Scanning/ip_location.pickle".format(username)
ip_raw_file = "/root/SSH-Blocking-and-Scanning/ip_raw.txt".format(username)

if not os.path.exists(working_dir):
    os.makedirs(working_dir)

try:
    if os.path.exists(working_file):
        with open(working_file, "rb") as pickled:
            ip_list = pickle.load(pickled)
    else:
        ip_list = []
except UnicodeDecodeError as UDE:
    ip_list = []

try:
    if os.path.exists(ip_tracker_file):
        with open(ip_tracker_file, "rb") as pickled:
            ip_country_stats = pickle.load(pickled)
    else:
        ip_country_stats = {"Per_Country": {}, "IP_Stats": {}}
except UnicodeDecodeError as UDE:
    ip_country_stats = {"Per_Country": {}, "IP_Stats": {}}

ip_temp_list = []

with open("/var/log/auth.log") as file:
    for line in file:
        line_split = line.strip().split()
        if "Failed password for" in line.strip():
            if not line_split[8].lower().startswith("up"):
                if line_split[10] not in ip_list or line_split[10] not in ip_temp_list:
                    if line_split[10] != "root" and line_split[10] not in ip_temp_list:
                        ip_temp_list.append(line_split[10])
        elif "Unable to negotiate with" in line.strip():
            if line_split[9] not in ip_list and line_split[9] not in ip_temp_list:
                ip_temp_list.append(line_split[9])
        elif "Did not receive identification string from" in line.strip():
            if line_split[11] not in ip_list and line_split[11] not in ip_temp_list:
                ip_temp_list.append(line_split[11])

for ip in ip_temp_list:
    if ip not in ip_list and ip not in ip_country_stats["IP_Stats"]:
        r = requests.get("https://www.ipinfo.io/{}/country".format(ip))
        if r.status_code == 200:

            try:
                ip_country_stats["Per_Country"][r.text.strip()] += 1
            except KeyError as KE:
                ip_country_stats["Per_Country"][r.text.strip()] = 1

            ip_country_stats["IP_Stats"][ip] = r.text.strip()

            ip_list.append(ip)
            with open(working_file, "wb") as pickled:
                pickle.dump(ip_list, pickled)
            with open(ip_tracker_file, "wb") as pickled:
                pickle.dump(ip_country_stats, pickled)
        elif r.status_code == 429:
            break

bad_origin = ["CN", "KR", "TR", "VN", "RU", "BR", "undefined", "MX", "ID", "IT", "HK"]

git_check = input("Do you want to push to git? ")
if git_check.upper().startswith("Y"):
    temp_bad_ip = []
    for IP in ip_country_stats["IP_Stats"]:
        if ip_country_stats["IP_Stats"][IP] in bad_origin and IP not in temp_bad_ip:
            temp_bad_ip.append(IP)

    temp_bad_ip.sort()
    if not os.path.exists(ip_raw_file):
        with open(ip_raw_file, "w") as raw_file:
            raw_file.write("\n".join(temp_bad_ip))
    else:
        with open(ip_raw_file, "w") as raw_file:
            raw_file.write("\n".join(temp_bad_ip))

# ##### Appending

static_info = ["\n", "####### This section was created by a program to block irritating IP's", "\n"]

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
with open(ip_raw_file) as rawIPs:
    for line in rawIPs:
        sshd_ip_list.append("sshd: {}\n".format(line.strip()))

temp_list = []

for line in hosts_file:
    temp_list.append(line)
for line in static_info:
    temp_list.append(line)
for line in sshd_ip_list:
    temp_list.append(line)

with open("/etc/hosts.deny", "w") as hosts_filea:
    for line in temp_list:
        hosts_filea.write(line)

subprocess.call("sudo service sshd restart", shell=True)
