from sanic import Sanic
import sanic.response
import asyncpg
import requests
import data_processing
import aiohttp
from time import time
import sanic_logging
import logging
print("Imported")

if __name__ != "__main__":
    exit()


sanic_logging.fix_logging()
app = Sanic("ssh-server", configure_logging=False)

print("Setup App")

app.static("/favicon.ico", "./favicon.ico", name="favicon")


@app.listener("before_server_start")
async def before_server_starts_handler(app, loop):
    app.pool = await asyncpg.create_pool(host="ssh-postgres", user="postgres")
    logging.info("Connected to database")
    app.session = aiohttp.ClientSession()
    logging.info("Created session")


@app.route("/")
async def home_handler(request):
    return sanic.response.text("There is no 127.0.0.1 for you. Please refer to the docs for the endpoints")


@app.route("/ip/single", methods=["GET"])
async def ip_info(request):
    if request.json is not None:
        try:
            ip = request.json["ip"]
        except KeyError:
            return sanic.response.json({"Error",
                                        "GET Request needs to come in the form of `{\"ip\": \"127.0.0.1\"}"},
                                       status=400)
    elif request.args != {}:
        try:
            ip = request.args["ip"][0]
        except KeyError:
            return sanic.response.json({"Error",
                                        "GET Request needs to come in the form of `{\"ip\": \"127.0.0.1\"}"},
                                       status=400)
    else:
        return sanic.response.json({"Error",
                                    "GET Request needs to come in the form of `{\"ip\": \"127.0.0.1\"}"},
                                   status=400)

    async with request.app.pool.acquire() as conn:
        ip_info = await data_processing.single_ip_processing(ip, conn, app.session)
    if ip_info["country"] == "??":
        return sanic.response.json(ip_info, status=429)
    else:
        return sanic.response.json(ip_info)


@app.route("/ip/list", methods=["GET"])
async def ip_submit_handler(request):

    try:
        ip_list = request.json["ip_list"]
    except KeyError:
        return sanic.response.json({"Error": "KeyError. Please send your JSON POST request with the JSON key being 'ip_list'"}, status=400)
    else:
        logging.info(f"From {request.ip} Len: {len(ip_list)}")

        start_time = time()
        async with request.app.pool.acquire() as conn:
            ip_list = await data_processing.processing_list(ip_list, conn, app.session)

        errored_list_count = 0
        for ip in ip_list:
            if ip["country"] == "??":
                errored_list_count += 1

        return sanic.response.json({"ip_list": ip_list, "time_taken": time()-start_time, "total_failed_amount": errored_list_count})


@app.route("/ip/stats", methods=["GET"])
async def ip_stats_handler(request):
    if request.args == {}:
        async with request.app.pool.acquire() as conn:
            return sanic.response.json(await data_processing.ip_statistics(conn))
    else:
        async with request.app.pool.acquire() as conn:
            processed_data = await data_processing.ip_statistics(conn, country=request.args["country"])
            if "Error" not in processed_data.keys():
                return sanic.response.json(processed_data)
            else:
                return sanic.response.json(processed_data, status=400)


with sanic_logging.setup_logging():
    ip = requests.get("http://api.ipify.org")
    logging.info(f"Running on {ip.text}")
    app.run(host="0.0.0.0", port=80, access_log=True)
