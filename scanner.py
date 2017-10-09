import os, time, pathlib, pickle

if os.geteuid() != 0:
    print("Please run as sudo.")
    exit()
else:
    print("Running as sudo.")


if not os.path.exists("~/SSH-Blocking-and-Scanning/"):
    os.makedirs("~/SSH-Blocking-and-Scanning/")


if os.path.exists("~/SSH-Blocking-and-Scanning/auth_scanning.pickle"):
    with open("~/SSH-Blocking-and-Scanning/auth_scanning.pickle") as pickled:
        ip_list = pickle.load(pickled)
else:
    ip_list = []

with open("/var/log/auth.log") as file:
    for line in file:
        # print(line.strip().split())
        was = line.strip().split()

        if was[8] == "root":
            print("Failed root from: {}".format(was[10]))

            if was[10] not in ip_list:
                print("Adding {} to list".format(was[10]))
                ip_list.append(was[10])
                with open("~/SSH-Blocking-and-Scanning/auth_scanning.pickle")as pickled:
                    pickle.dump(ip_list, pickled)
                print("Saved")

            time.sleep(0.5)
#        time.sleep(1)

