import os, sys, time

if os.geteuid() != 0:
    print("Please run as sudo.")
    exit()
else:
    print("Running as sudo.")


with open("/var/log/auth.log") as file:
    for line in file:
        print(line.strip())
        time.sleep(1)

