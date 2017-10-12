import platform, os

if platform.system() != "Linux":
    print("This code only works on Linux/Debian at the moment.")
    exit()

if os.geteuid() != 0:
    print("Please run as sudo.")
    exit()
else:
    print("Running as sudo.")

username = os.getlogin()

"/home/{}/20fdd6a36582ad545e91485592c8ab4e"
