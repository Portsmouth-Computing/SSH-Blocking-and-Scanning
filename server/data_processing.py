import database_programs


async def single_data_retrieval(ip, app_session):
    async with app_session.get(f"http://www.ipinfo.io/{ip}/country") as resp:
        country = await resp.text()
        country = country.strip()
    print(f"Fetched country ({country}) for {ip}")
    return country


async def single_ip_processing(ip, conn, app_session):
    ip_info = await database_programs.fetch_from_database(conn, ip)
    if ip_info is not None:
        await database_programs.update_entry(conn, ip, ip_info["accessed"])
        # return await database_programs.fetch_formattor(ip_info)
        return dict(ip_info)
    else:
        country = await single_data_retrieval(ip, app_session)
        await database_programs.insert_into_database(conn, ip, country)
        ip_info = await database_programs.fetch_from_database(conn, ip)
        # return await database_programs.fetch_formattor(ip_info)
        return dict(ip_info)


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
