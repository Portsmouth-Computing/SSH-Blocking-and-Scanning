import os, time, pickle, requests

if os.geteuid() != 0:
    print("Please run as sudo.")
    exit()
else:
    print("Running as sudo.")

username = os.getlogin()

working_dir = "/home/{}/SSH-Blocking-and-Scanning/".format(username)
working_file = "/home/{}/SSH-Blocking-and-Scanning/auth_scanning.pickle".format(username)
ip_tracker_file = "/home/{}/SSH-Blocking-and-Scanning/ip_location.pickle".format(username)

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
                    if line_split[10] not in ip_temp_list:
                        print("Adding {} to list".format(line_split[10]))
                    ip_stats[line_split[10]] = 1
                    if line_split[10] != "root" and line_split[10] not in ip_temp_list:
                        ip_temp_list.append(line_split[10])
                        # with open(working_file, "wb")as pickled:
                        #     pickle.dump(ip_list, pickled)
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
                        time.sleep(0.5)

    #        time.sleep(1)
        elif "Unable to negotiate with" in line.strip():
            if line_split[9] not in ip_list and line_split[9] not in ip_temp_list:
                print("Adding {} to list from key exchange".format(line_split[9]))
                ip_temp_list.append(line_split[9])

print(len(ip_temp_list), "Results to go through")
ip_country_stats_temp = {}

for ip in ip_temp_list:
    if ip not in ip_list:
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

print("Amount of times the IP was found within the auth.log")
print(ip_stats)
print("Amount of countries found in this scan")
print(ip_country_stats_temp)
print("Total amount of country stats")
print(ip_country_stats)
