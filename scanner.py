import os, pickle, requests, platform, subprocess

if platform.system() != "Linux":
    print("This code only works on Linux/Debian at the moment.")
    exit()

if os.geteuid() != 0:
    print("Please run as sudo.")
    exit()
else:
    print("Running as sudo.")

username = os.getlogin()

working_dir = "/home/{}/SSH-Blocking-and-Scanning/".format(username)
working_file = "/home/{}/SSH-Blocking-and-Scanning/auth_scanning.pickle".format(username)
ip_tracker_file = "/home/{}/SSH-Blocking-and-Scanning/ip_location.pickle".format(username)
ip_raw_file = "/home/{}/SSH-Blocking-and-Scanning/ip_raw.txt".format(username)

if not os.path.exists(working_dir):
    os.makedirs(working_dir)

try:
    if os.path.exists(working_file):
        with open(working_file, "rb") as pickled:
            ip_list = pickle.load(pickled)
            print("Loaded Auth Pickle")
            print(ip_list)
    else:
        ip_list = []
        print("Loaded Blank IP List File as Pickle did not exist")
except UnicodeDecodeError as UDE:
    print(UDE, ". Loading Blank IP List")
    ip_list = []

try:
    if os.path.exists(ip_tracker_file):
        with open(ip_tracker_file,"rb") as pickled:
            ip_country_stats = pickle.load(pickled)
            print("Loaded IP Tracker Pickle")
    else:
        ip_country_stats = {"Per_Country": {}, "IP_Stats": {}}
        print("Loaded Blank Tracker List as Pickle did not exist.")
except UnicodeDecodeError as UDE:
    print(UDE, ". Loading Blank IP Tracker List")
    ip_country_stats = {"Per_Country": {}, "IP_Stats": {}}

ip_temp_list = []

ip_stats = {}

with open("/var/log/auth.log") as file:
    for line in file:
        # print(line.strip().split())
        line_split = line.strip().split()
        if "Failed password for root from" in line.strip():
            if line_split[8] == "root":

                if line_split[10] not in ip_list or line_split[10] not in ip_temp_list:
                    if line_split[10] != "root" and line_split[10] not in ip_temp_list:
                        print("Adding {} to list".format(line_split[10]))
                        ip_temp_list.append(line_split[10])
                        ip_stats[line_split[10]] = 1
                        print("Saved")
                    else:
                        try:
                            ip_stats[line_split[10]] += 1
                        except KeyError as KE:
                            print(KE, "Defaulting to 0")
                            ip_stats[line_split[10]] = 1
                else:
                    try:
                        ip_stats[line_split[10]] += 1
                    except KeyError as KE:
                        print(KE,"Defaulting to 0")
                        ip_stats[line_split[10]] = 1
                    if ip_stats[line_split[10]] <= 10:
                        print("Failed root from: {}".format(line_split[10]))

        elif "Unable to negotiate with" in line.strip():
            if line_split[9] not in ip_list and line_split[9] not in ip_temp_list:
                print("Adding {} to list from key exchange".format(line_split[9]))
                ip_temp_list.append(line_split[9])
                try:
                    ip_stats[line_split[9]] += 1
                except KeyError as KE:
                    print(KE, "Defaulting to 0")
                    ip_stats[line_split[9]] = 1
            else:
                try:
                    ip_stats[line_split[9]] += 1
                except KeyError as KE:
                    print(KE, "Defaulting to 0")
                    ip_stats[line_split[9]] = 1

print(len(ip_temp_list), "Results to go through")
ip_country_stats_temp = {}

for ip in ip_temp_list:
    if ip not in ip_list and ip not in ip_country_stats["IP_Stats"]:
        r = requests.get("https://www.ipinfo.io/{}/country".format(ip))
        if r.status_code == 200:
            print("This IP came from {} ({})".format(r.text.strip(), ip))

            try:
                ip_country_stats_temp[r.text.strip()] += 1
            except KeyError as KE:
                ip_country_stats_temp[r.text.strip()] = 1

            try:
                ip_country_stats["Per_Country"][r.text.strip()] += 1
            except KeyError as KE:
                ip_country_stats["Per_Country"][r.text.strip()] = 1

            ip_country_stats["IP_Stats"][ip] = r.text.strip()

            ip_list.append(ip)
            with open(working_file, "wb") as pickled:
                pickle.dump(ip_list, pickled)
            with open(ip_tracker_file ,"wb") as pickled:
                pickle.dump(ip_country_stats, pickled)
        elif r.status_code == 429:
            print("Rate limited. Please wait for 24hrs.")
            input(">")
            break

bad_origin = ["CN", "KR", "TR", "VN", "RU"]

git = input("Do you want to push to git? ")
if git.upper().startswith("Y"):
    temp_bad_ip = []
    for IP in ip_country_stats["IP_Stats"]:
        if ip_country_stats["IP_Stats"][IP] in bad_origin and IP not in temp_bad_ip:
            temp_bad_ip.append(IP)

    print(len(temp_bad_ip), "Bad IPs found.")

    if not os.path.exists(ip_raw_file):
        with open(ip_raw_file, "w") as raw_file:
            raw_file.write("\n".join(temp_bad_ip))
    else:
        with open(ip_raw_file, "a") as raw_file:
            raw_file.write("\n".join(temp_bad_ip))

# ##############################To do, use git via subprocess and `git commit -a -m "Added a IP"` and then `git push`

w = input("This code is designed for the author of this as it uses git and push. After this stage it is highly likely it will break for you. Do you want to continue? ").upper()
if w == "Y":
    import shutil
    dst_copy_file = "/home/{}/20fdd6a36582ad545e91485592c8ab4e/ip_raw.txt"
    shutil.copy("/home/{}/SSH-Blocking-and-Scanning/ip_raw.txt".format(username), dst_copy_file.format(username))
    with open(dst_copy_file, "r") as dst_file:
        ip_list = dst_file.read()
    with open("/home/{}/20fdd6a36582ad545e91485592c8ab4e/blocked_IPs", "a") as blocked:
        blocked.write(ip_list)
    os.chdir("/home{}/20fdd6a36582ad545e91485592c8ab4e")
    subprocess.call("git commit -a -m 'Added a large amount of IPs from auth.logs'", shell=True)
    subprocess.call("git push", shell=True)


print("Amount of times the IP was found within the auth.log")
print(ip_stats)
print("Amount of countries found in this scan")
print(ip_country_stats_temp)
print("Total amount of country stats")
print(ip_country_stats)
