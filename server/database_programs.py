async def fetch_from_database(conn, ip):
    messages = await conn.fetch(
        "SELECT * FROM ip_storage WHERE ip = $1", ip
    )

    return messages


async def fetch_formattor(messages):
    formatted_list = []
    for message in messages:
        formatted_list.append({"id": message["id"], "message": message["message"]})

    return formatted_list


async def insert_into_database(conn, message):
    await conn.execute("""
    INSERT INTO messages(message) VALUES($1)""",
                       message)
