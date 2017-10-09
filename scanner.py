import os, sys, time

if os.geteuid() != 0:
    print("Please run as sudo.")
    exit()


with open("/var/log/auth.log") as file:
    for line in file:
        print(line)
        time.sleep(1)

