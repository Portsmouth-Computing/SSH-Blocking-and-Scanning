import ipaddress
from typing import Union


async def fetch_from_database(conn, ip):
    messages = await conn.fetchrow(
        "SELECT * FROM ip_storage WHERE ip = $1", ip
    )

    return messages


async def fetch_formattor(ip_dict):
    formatted_ip_dict = {"ip": await ip_formattor(ip_dict["ip"]),
                         "country": ip_dict["country_code"],
                         "last_updated": ip_dict["last_updated"],
                         "amount_checked": ip_dict["accessed"]}

    return formatted_ip_dict


async def ip_formattor(ip_address: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]):
    if ip_address.version == 4:
        return await ipv4_formattor(ip_address)
    else:
        return await ipv6_formattor(ip_address)


async def ipv4_formattor(ip_address: ipaddress.IPv4Address):
    formatted_ipv4 = {"version": ip_address.version,
                      "max_prefixlen": ip_address.max_prefixlen,
                      "compressed": ip_address.compressed,
                      "exploded": ip_address.exploded,
                      "reverse_pointer": ip_address.reverse_pointer,
                      "is_multicast": ip_address.is_multicast,
                      "is_private": ip_address.is_private,
                      "is_global": ip_address.is_global,
                      "is_unspecified": ip_address.is_unspecified,
                      "is_reserved": ip_address.is_reserved,
                      "is_loopback": ip_address.is_loopback,
                      "is_link_local": ip_address.is_link_local}
    return formatted_ipv4


async def ipv6_formattor(ip_address: ipaddress.IPv6Address):
    formatted_ipv6 = {"version": ip_address.version,
                      "max_prefixlen": ip_address.max_prefixlen,
                      "compressed": ip_address.compressed,
                      "exploded": ip_address.exploded,

                      "reverse_pointer": ip_address.reverse_pointer,
                      "is_multicast": ip_address.is_multicast,
                      "is_private": ip_address.is_private,
                      "is_global": ip_address.is_global,
                      "is_unspecified": ip_address.is_unspecified,
                      "is_reserved": ip_address.is_reserved,
                      "is_loopback": ip_address.is_loopback,
                      "is_link_local": ip_address.is_link_local,
                      "is_site_local": ip_address.is_site_local,

                      "ipv4_mapped": ip_address.ipv4_mapped,
                      "sixtofour": ip_address.sixtofour,
                      "teredo": ip_address.teredo}

    return formatted_ipv6


async def update_entry(conn, ip, current_total):
    await conn.execute("""
    UPDATE ip_storage
        SET accessed = accessed + 1
    WHERE ip = $1
        AND accessed = $2
    """, ip, current_total)


async def insert_into_database(conn, ip, country):
    await conn.execute("""
    INSERT INTO ip_storage(ip, country_code) VALUES($1, $2)""",
                       ip, country)


async def list_data_into_str(data_list: list):
    base_string = ""
    for item in data_list:
        base_string = f"{base_string}\'{item}\'"
    base_string = base_string[:-2]
    print("BS, ", base_string)
    return base_string


async def country_count_stats(conn, country=None):
    if country is None:
        return await conn.fetch("""
        SELECT COUNT(country_code),country_code
        FROM ip_storage
        GROUP BY country_code
        ORDER BY 1 DESC""")
    else:
        if len(country) == 1:
            return await conn.fetchval("""
            SELECT COUNT(country_code)
            FROM ip_storage
            WHERE country_code = $1""", country[0])
        else:
            return await conn.fetch("""
            SELECT COUNT(country_code), country_code
            FROM ip_storage
            WHERE country_code in ($1)
            GROUP BY country_code
            ORDER BY 1 DESC""", await list_data_into_str(country))
