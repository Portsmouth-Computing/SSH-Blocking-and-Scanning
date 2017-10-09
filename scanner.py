import os, time, pickle

if os.geteuid() != 0:
    print("Please run as sudo.")
    exit()
else:
    print("Running as sudo.")

working_dir = "~/SSH-Blocking-and-Scanning/"
working_file = "~/SSH-Blocking-and-Scanning/auth_scanning.pickle"

if not os.path.exists(working_dir):
    os.makedirs(working_dir)

try:
    if os.path.exists(working_file):
        with open(working_file, "rb") as pickled:
            ip_list = pickle.load(pickled)
    else:
        ip_list = []
except UnicodeDecodeError as UDE:
    print(UDE, ". Loading blank IP list")
    ip_list = []


ip_stats = {}

with open("/var/log/auth.log") as file:
    for line in file:
        # print(line.strip().split())
        line_split = line.strip().split()
        if "root" in line.strip():
            if line_split[8] == "root":

                if line_split[10] not in ip_list:
                    ip_stats[line_split[10]] = 0
                    print(ip_stats)
                    print("Adding {} to list".format(line_split[10]))
                    ip_list.append(line_split[10])
                    with open(working_file, "wb")as pickled:
                        pickle.dump(ip_list, pickled)
                    print("Saved")
                else:
                    print(ip_stats)
                    ip_stats[line_split[10]] += 1
                    if ip_stats[line_split[10]] <= 10:
                        print("Failed root from: {}".format(line_split[10]))
                        time.sleep(0.5)

    #        time.sleep(1)
        # Also work on a statement that checks lines like `Oct  8 17:27:33 up857256 sshd[15848]: Unable to negotiate with 27.76.249.209 port 56038: no matching key exchange method found. Their offer: diffie-hellman-group1-sha1 [preauth]`

print(ip_stats)
