from sanic import Sanic
import sanic.response
import asyncpg
import requests
import data_processing
import aiohttp
from time import time
print("Imported")

app = Sanic("ssh-server")
print("Setup App")


@app.listener("before_server_start")
async def before_server_starts_handler(app, loop):
    app.pool = await asyncpg.create_pool(host="ssh-postgres", user="postgres")
    print("Connected to database")
    app.session = aiohttp.ClientSession()
    print("Created session")


@app.route("/ip/single", methods=["POST"])
async def ip_info(request):
    async with request.app.pool.acquire() as conn:
        ip_info = await data_processing.single_ip_processing(request.json["ip"], conn, app.session)
    if ip_info["country"] == "??":
        return sanic.response.json(ip_info, status=429)
    else:
        return sanic.response.json(ip_info)


@app.route("/ip/list", methods=["POST"])
async def ip_submit_handler(request):

    try:
        ip_list = request.json["ip_list"]
    except KeyError:
        return sanic.response.json({"Error": "KeyError. Please send your JSON POST request with the JSON key being 'ip_list'"}, status=400)
    else:
        print('''f"From {request.ip} Len: {assert isinstance(ip_list, )len(ip_list)}"''')

        start_time = time()
        async with request.app.pool.acquire() as conn:
            ip_list = await data_processing.processing_list(ip_list, conn, app.session)

        errored_list_count = 0
        for ip in ip_list:
            if ip["country"] == "??":
                errored_list_count += 1

        return sanic.response.json({"ip_list": ip_list, "time_taken": time()-start_time, "total_failed_amount": errored_list_count})


if __name__ == "__main__":
    ip = requests.get("http://api.ipify.org")
    print(f"Running on {ip.text}")
    app.run(host="0.0.0.0", port=80, access_log=True)
