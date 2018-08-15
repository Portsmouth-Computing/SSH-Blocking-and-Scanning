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
re_ipv4 = re.compile("((?:\d{1,3}\.){3}\d{1,3})")
re_ipv6 = re.compile("((?:\w{1,4}:){7}\w{1,4})")
re_luma = re.compile(r'(?P<address>([a-f\d]{1,4}[\.:]){1,7}[a-f\d]{1,4})\sport')


def main():
    if os.geteuid() != 0:
        print("Not root. Need root perms to access auth.log")
        exit()

    ip_temp_list = []

    with open("/var/log/auth.log") as file:
        for line in file:
            ip = re_ipv4.search(line)
            if ip is None:
                ip = re_ipv6.search(line)
                if ip is not None:
                    ip_temp_list.append(ip.group())
            else:
                ip_temp_list.append(ip.group())

    return ip_temp_list


if __name__ == "__main__":
    ip_temp_list = main()
    print(len(ip_temp_list))
