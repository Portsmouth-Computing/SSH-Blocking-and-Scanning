import database_programs


async def single_ip_processing(ip, conn):
    ip_info = await database_programs.fetch_from_database(conn, ip)
    print(ip_info)


async def processing_list(ip_list, conn):
    for ip in ip_list:
        ip_info = await database_programs.fetch_from_database(conn, ip)
        print(ip_info)
"""
    for ip in ip_list:
        if ip not in ip_list and ip not in ip_country_stats["IP_Stats"]:
            r = requests.get("https://www.ipinfo.io/{}/country".format(ip))
            if r.status_code == 200:

                ip_country_stats["IP_Stats"][ip] = r.text.strip()

                ip_list.append(ip)
                with open(working_file, "wb") as pickled:
                    pickle.dump(ip_list, pickled)
                with open(ip_tracker_file, "wb") as pickled:
                    pickle.dump(ip_country_stats, pickled)
            elif r.status_code == 429:
                break
"""
