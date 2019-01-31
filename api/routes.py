# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2018 Samuel Riches

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import ipaddress
import itertools
import logging

import sanic

from .helpers import fetch_ip_info, fetch_lookup_stats

bp = sanic.Blueprint('API-Routes')
log = logging.getLogger(__name__)


@bp.route('/ip/info', methods=['GET'])
async def get_ip_info(request):
    try:
        addresses = list(itertools.chain.from_iterable(x.split() for x in request.args['ip']))
    except KeyError:
        try:
            addresses = request.json.get('addresses') or [request.json['ip']]
        except (AttributeError, KeyError):
            error = (
                'Please specify one or more IP Addresses under the "ip" query parameter (multiple or space separated) '
                'or as a json body under the "ip" (single) or "addresses" (array) keys.'
            )

            return sanic.response.json({'error': error}, status=400)

    app = request.app

    temp_address = []
    for ip_address in addresses:
        try:
            temp_address.append(ipaddress.ip_address(ip_address))
        except ValueError:
            log.warning(f"ValueError: Issue making \'{ip_address}\' into IPAddress")
    addresses = list(temp_address)
    del temp_address

    return sanic.response.json(
        {x: await fetch_ip_info(x, conn=app.db, session=app.session, token=app.cfg.token) for x in set(addresses)}
    )


@bp.route("/ip/info/me", methods=["GET"])
async def get_own_ip_info(request):
    app = request.app
    address = request.headers.get('CF-Connecting-IP') or request.headers.get('X-Forwarded-For') or request.ip
    return sanic.response.json({address: await fetch_ip_info(address, conn=app.db, session=app.session, token=app.cfg.token)})


@bp.route('/stats', methods=['GET'])
async def get_ip_stats(request):
    try:
        countries = list(itertools.chain.from_iterable(x.split() for x in request.args['country']))
    except KeyError:
        try:
            countries = request.json.get('countries') or [request.json['country']]
        except (AttributeError, KeyError):
            countries = None

    return sanic.response.json(await fetch_lookup_stats(countries, conn=request.app.db),
                               headers={"Access-Control-Allow-Origin": "*"})
