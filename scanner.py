import os, sys, time

with open("/var/log/auth.log") as file:
    for line in file:
        print(line)
        time.sleep(1)
