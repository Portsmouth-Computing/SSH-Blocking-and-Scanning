import database_programs
from time import time
from names import names
import itertools
from config import API_KEY
import logging


async def single_data_retrieval(ip, app_session):
    async with app_session.get(f"http://www.ipinfo.io/{ip}/json?token={API_KEY}") as resp:
        json = await resp.json()
        status = resp.status
    try:
        country = json["country"].strip()
    except KeyError:
        country = "??"
    try:
        city = json["city"].strip()
    except KeyError:
        print("KE City", ip)
        city = "??"
    try:
        org = json["org"].strip()
    except KeyError:
        print("KE org", ip)
        org = "??"
    try:
        region = json["region"].strip()
    except KeyError:
        print("KE region", ip)
        region = "??"
    if status == 200:
        logging.info(f"Fetched country ({country}) for {ip}")
    return country, city, org, region, status


async def single_ip_processing(ip, conn, app_session, limit_hit=False):
    ip = ip.strip()
    ip_info = await database_programs.fetch_from_database(conn, ip)

    if ip_info is not None:
        await database_programs.update_entry(conn, ip, ip_info["accessed"])
        return await database_programs.fetch_formattor(ip_info)

    else:

        if not limit_hit:
            country, city, org, region, status = await single_data_retrieval(ip, app_session)

            if status == 200:
                await database_programs.insert_into_database(conn, ip, country, city, org, region)
                ip_info = await database_programs.fetch_from_database(conn, ip)
                return await database_programs.fetch_formattor(ip_info)

            else:
                logging.warning(f"{status} for {ip}")
                return {"ip": ip,
                        "country": "??",
                        "city": "??",
                        "region": "??",
                        "org": "??",
                        "last_updated": time(),
                        "amount_checked": 1}

        else:
            return {"ip": ip,
                    "country": "??",
                    "city": "??",
                    "region": "??",
                    "org": "??",
                    "last_updated": time(),
                    "amount_checked": 1}


async def raw_country_code_stats_formattor(data_list):
    temp_dict = {}
    for item in data_list:
        temp_dict[names[item["country_code"]]] = item["count"]
    return temp_dict


async def ip_statistics(conn, country=None):
    if country is None:
        raw_country_code_data = await database_programs.country_count_stats(conn, country)
        formatted_country_codes = await raw_country_code_stats_formattor(raw_country_code_data)

        return formatted_country_codes

    else:
        checked_list = []
        erred_codes = []

        country = list(itertools.chain.from_iterable(x.split() for x in country))

        for code in country:
            if code in names:
                checked_list.append(code)
            else:
                erred_codes.append(code)

        if checked_list:
            raw_country_code_data = await database_programs.country_count_stats(conn, checked_list)
            if len(checked_list) == 1:
                if len(country) == 1:
                    return {names[checked_list[0]]: raw_country_code_data}
                else:
                    return {"country_data": {names[checked_list[0]]: raw_country_code_data},
                            "invalid_country_codes": erred_codes}
            else:
                formatted_country_codes = await raw_country_code_stats_formattor(raw_country_code_data)
                return {"country_data": formatted_country_codes, "invalid_country_codes": erred_codes}
        else:
            if len(country) == 1:
                return {"Error": f"\'{erred_codes[0]}\' was not found in the database. "
                                 f"Please refer to ISO2 standard for Country Codes."}
            else:
                return {"Error": f"{', '.join(erred_codes)} were not found in the database. "
                                 f"Please refer to the ISO2 standard for Country Codes."}


async def processing_list(ip_list, conn, app_session):
    processed_ip_list = []
    limit_hit = False

    for ip in ip_list:
        ip_info = await single_ip_processing(ip, conn, app_session, limit_hit)
        if ip_info["country"] == "??":
            limit_hit = True
        processed_ip_list.append(ip_info)

    return processed_ip_list

