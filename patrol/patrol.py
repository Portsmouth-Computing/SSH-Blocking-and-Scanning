# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2018 Samuel Riches

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import re
import time

re_ipv4 = re.compile(r"(?P<address>(?:\d{1,3}\.){3}\d{1,3})")
re_ipv6 = re.compile(r"(?P<address>(?:\w{1,4}:){7}\w{1,4})")
re_luma = re.compile(r'(?P<address>([a-f\d]{1,4}[\.:]){1,7}[a-f\d]{1,4})\sport')

IGNORED_LINE_CONTENTS = [" CRON[",
                         "refused connect from ",
                         "input_userauth_request",
                         "check pass; user unknown",
                         "Too many authentication failures",
                         "Connection closed by",
                         "pam_unix(sshd:auth): authentication failure",
                         "Disconnected from ",
                         "maximum authentication attempts exceeded",
                         "more authentication failure"]

LINES_TO_TEST = ["Failed password for invalid user",
                 "Unable to negotiate with",
                 "Bad protocol version identification",
                 "Service not available",
                 "Received disconnect from"]


def regex_check(string):
    ip = re_ipv4.search(string)
    if ip is None:
        ip = re_ipv6.search(string)
        if ip is not None:
            ip = ip.group("address")
            return ip
    else:
        ip = ip.group("address")
        return ip


def alt_main():
    ip_templist = []
    not_found_lines = []

    with open("/var/log/auth.log") as file:
        for line in file:
            if any(line_part in line for line_part in LINES_TO_TEST):
                ip = regex_check(line.strip())
                if ip is not None:
                    ip_templist.append(ip)
            else:
                not_found_lines.append(line.strip())
    return set(ip_templist), not_found_lines


def sshd_config_scan():
    if os.getuid() != 0:
        print("Not root. Need root perms to access auth.log")
        exit()

    with open("/etc/ssh/sshd_config") as file:
        for line in file:
            if "PermitRootLogin" in line:
                line = line.strip().split(" ")
                print(line)
                if line[1].lower() == "no":
                    return True
                else:
                    return False
        else:
            return False


def main():
    if os.geteuid() != 0:
        print("Not root. Need root perms to access auth.log")
        exit()

    ip_templist = []

    with open("/var/log/auth.log") as file:
        for line in file:
            ip = re_ipv4.search(line)
            if ip is None:
                ip = re_ipv6.search(line)
                if ip is not None:
                    ip = ip.group("address")
                    ip_templist.append(ip)
            else:
                ip = ip.group("address")
                ip_templist.append(ip)

    return list(set(ip_templist))


if sshd_config_scan():
    LINES_TO_TEST.append("Failed password for root from")
    print("Enabled 'Failed password for root'")


if __name__ == "__main__":
    ip_temp_list, not_found_lines = alt_main()
    print(len(ip_temp_list))
    for line in not_found_lines:
        if not any(line_part in line for line_part in IGNORED_LINE_CONTENTS):
            print(line, "\t"*4, regex_check(line) in ip_temp_list)
            time.sleep(0.25)
