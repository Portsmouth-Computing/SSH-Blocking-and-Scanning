from sanic import Sanic
import sanic.response
import asyncpg
import requests
import data_processing
print("Imported")

app = Sanic("ssh-server")
print("Setup App")


@app.listener("before_server_start")
async def setup_db_connection(app, loop):
    app.pool = await asyncpg.create_pool(host="ssh-postgres", user="postgres")
    print("Connected to database")


@app.route("/ip/info", methods=["POST"])
async def ip_info(request):
    async with request.app.pool.acquire() as conn:
        ip_info = await data_processing.single_ip_processing(request.json["ip"], conn)
    return sanic.response.json(ip_info)



@app.route("/ip/submit", methods=["POST"])
async def ip_submit_handler(request):
    print("Len: ", len(request.json))

    async with request.app.pool.acquire() as conn:
        bad_ip_list = await data_processing.processing_list(request.json, conn)


if __name__ == "__main__":
    ip = requests.get("http://api.ipify.org")
    print(f"Running on {ip.text}")
    app.run(host="0.0.0.0", port=80, access_log=True)
