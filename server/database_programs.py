async def fetch_from_database(conn):
    messages = await conn.fetch(
        "SELECT * FROM messages ORDER BY id DESC LIMIT 50"
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
