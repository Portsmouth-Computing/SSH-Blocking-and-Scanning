from time import time


async def fetch_from_database(conn, ip):
    messages = await conn.fetchrow(
        "SELECT * FROM ip_storage WHERE ip = $1", ip
    )

    return messages


async def fetch_formattor(ip_dict):
    formatted_ip_dict = {"ip": ip_dict["ip"],
                         "country": ip_dict["country"],
                         "last_updated_time": ip_dict["last_updated_time"],
                         "amount_checked": ip_dict["amount_checked"]}

    return formatted_ip_dict


async def update_entry(conn, ip, current_total):
    await conn.execute("""
    UPDATE ip_storage
        SET amount_checked = amount_checked + 1
    WHERE ip = $1
        AND amount_checked = $2
    """, ip, current_total)


async def insert_into_database(conn, ip, country):
    await conn.execute("""
    INSERT INTO ip_storage(ip, country, last_updated_time, amount_checked) VALUES($1, $2, $3, $4)""",
                       ip, country, time(), 1)
