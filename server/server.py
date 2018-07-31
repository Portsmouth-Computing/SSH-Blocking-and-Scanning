from sanic import Sanic
import sanic.response
import asyncpg
import requests
print("Imported")

app = Sanic("ssh-server")
print("Setup App")


@app.listener("before_server_start")
async def setup_db_connection(app, loop):
    app.pool = await asyncpg.create_pool(host="postgres", user="postgres")
    print("Connected to database")


if __name__ == "__main__":
    ip = requests.get("http://api.ipify.org")
    print(f"Running on {ip.text}")
    app.run(host="0.0.0.0", port=80, access_log=True)
