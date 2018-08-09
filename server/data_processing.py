import database_programs
from time import time
from names import names


async def single_data_retrieval(ip, app_session):
    async with app_session.get(f"http://www.ipinfo.io/{ip}/country") as resp:
        country = await resp.text()
        country = country.strip()
        status = resp.status
    if status == 200:
        print(f"Fetched country ({country}) for {ip}")
    return country, status


async def single_ip_processing(ip, conn, app_session, limit_hit=False):
    ip = ip.strip()
    ip_info = await database_programs.fetch_from_database(conn, ip)

    if ip_info is not None:
        await database_programs.update_entry(conn, ip, ip_info["accessed"])
        return await database_programs.fetch_formattor(ip_info)

    else:

        if not limit_hit:
            country, status = await single_data_retrieval(ip, app_session)

            if status == 200:
                await database_programs.insert_into_database(conn, ip, country)
                ip_info = await database_programs.fetch_from_database(conn, ip)
                return await database_programs.fetch_formattor(ip_info)

            else:
                print(f"{status} for {ip}")
                return {"ip": ip, "country": "??", "last_updated": time(), "amount_checked": 1}

        else:
            return {"ip": ip, "country": "??", "last_updated": time(), "amount_checked": 1}


async def raw_country_code_stats_formattor(data_list):
    temp_dict = {}
    for item in data_list:
        temp_dict[names[item["country_code"]]] = item["count"]
    return temp_dict


async def ip_statistics(conn, country=None):
    raw_country_code_data = await database_programs.country_count_stats(conn, country)
    print("RCCD, ", raw_country_code_data)
    if country is None:
        formatted_country_codes = await raw_country_code_stats_formattor(raw_country_code_data)
        return formatted_country_codes
    else:
        print("LEN, ", len(country))
        if len(country) == 1:
            return {country[0]: raw_country_code_data}
        else:
            formatted_country_codes = await raw_country_code_stats_formattor(raw_country_code_data)
            return formatted_country_codes


async def processing_list(ip_list, conn, app_session):
    processed_ip_list = []
    limit_hit = False

    for ip in ip_list:
        ip_info = await single_ip_processing(ip, conn, app_session, limit_hit)
        if ip_info["country"] == "??":
            limit_hit = True
        processed_ip_list.append(ip_info)

    return processed_ip_list

"""
        ip_info = await database_programs.fetch_from_database(conn, ip)

        if ip_info is not None:
            await database_programs.update_entry(conn, ip, ip_info["accessed"])
            processed_ip_list.append(await database_programs.fetch_formattor(ip_info))

        else:
            country = await single_data_retrieval(ip, app_session)
            await database_programs.insert_into_database(conn, ip, country)
            ip_info = await database_programs.fetch_from_database(conn, ip)
            processed_ip_list.append(await database_programs.fetch_formattor(ip_info))

    return processed_ip_list
    """

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
