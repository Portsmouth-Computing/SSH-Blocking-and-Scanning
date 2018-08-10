import os


def main():
    if os.geteuid() != 0:
        print("Not root. Need root perms to access auth.log")
        exit()

    ip_temp_list = []

    with open("/var/log/auth.log") as file:
        for line in file:
            line_split = line.strip().split()
            if "Accepted publickey for kopeckyj from" in line:
                continue
            elif " sshd[" not in line:
                continue

            if "Failed password for invalid user" in line.strip():
                if not line_split[10].lower().startswith("up"):
                    failed_user_ip = line_split[12]
                    if failed_user_ip not in ip_temp_list:
                        ip_temp_list.append(failed_user_ip)

            if "Failed password for" in line.strip():
                if not line_split[8].lower().startswith("up"):
                    failed_ip = line_split[10]
                    if failed_ip not in ip_temp_list:
                        ip_temp_list.append(failed_ip)

            elif "Unable to negotiate with" in line.strip():
                negotiate_ip = line_split[9]
                if negotiate_ip not in ip_temp_list:
                    ip_temp_list.append(negotiate_ip)

            elif "Did not receive identification string from" in line.strip():
                identification_ip = line_split[11]
                if identification_ip not in ip_temp_list:
                    ip_temp_list.append(identification_ip)

    return ip_temp_list


if __name__ == "__main__":
    ip_temp_list = main()
    print(len(ip_temp_list))
