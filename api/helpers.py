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

import datetime
import ipaddress
import logging

from .country_codes import codes


log = logging.getLogger(__name__)


# single IP lookup

async def fetch_ip_info(address, *, conn, session, token):
    """
    Fetch information about a single IP Address from the database.
    If the entry exists it's lookup counter will be increased.

    Parameters
    ----------
    address : str
        The IP Address to look up.
    conn : Union[asyncpg.Connection, asyncpg.pool.Pool]
        The connection to the database.
    session : aiohttp.ClientSession
        The session to fetch address info with if it's not cached.
    token : str
        The API token to look up addresses.
    """

    info = await fetch_cached_info(address, conn=conn)

    if info is not None:
        log.info(f'IP info for address "{address}" cached.')
    else:
        log.info(f'IP info for address "{address}" not cached, fetching ..')
        info = await fetch_address_info(address, conn=conn, session=session, token=token)

    return format_response(info)


async def fetch_cached_info(address, *, conn):
    record = await conn.fetchrow(
        'SELECT ip, country_code, accessed, city, region, org, last_updated FROM ip_storage WHERE ip = $1', address
    )

    if record is None:
        return

    await conn.execute('UPDATE ip_storage SET accessed = ip_storage.accessed + 1 WHERE ip = $1', address)
    return dict(record)


async def fetch_address_info(address, *, conn, session, token):
    async with session.get(f'https://www.ipinfo.io/{address}/json?token={token}') as resp:
        data = await resp.json()

    city = data.get('city', '??')
    country_code = data.get('country', '??')
    org = data.get('org', '??')
    region = data.get('region', '??')
    loc = data.get('loc', '??')

    await conn.execute(
        'INSERT INTO ip_storage(ip, country_code, city, region, org, loc) VALUES ($1, $2, $3, $4, $5, $6)',
        address,
        country_code,
        city,
        region,
        org,
        loc
    )

    result = {
        'ip': ipaddress.ip_address(address),
        'country_code': country_code,
        'accessed': 1,
        'city': city,
        'region': region,
        'org': org,
        'loc': loc,
        'last_updated': datetime.datetime.utcnow()
    }

    return result


def format_response(info):
    ip = info['ip']
    country_code = info['country_code']

    response = {
        'global': ip.is_global,
        'loopback': ip.is_loopback,
        'max_prefixlen': ip.max_prefixlen,
        'multicast': ip.is_multicast,
        'link_local': ip.is_link_local,
        'private': ip.is_private,
        'reserved': ip.is_reserved,
        'reverse_pointer': ip.reverse_pointer,
        'unspecified': ip.is_unspecified,
        'version': ip.version,

        'city': info['city'],
        'country': codes.get(country_code, '??'),
        'country_code': country_code,
        'region': info['region'],
        'org': info['org'],
        'loc': info['loc']
    }

    if isinstance(ip, ipaddress.IPv6Address):
        response.update({
            'ipv4_mapped': ip.ipv4_mapped,
            'site_local': ip.is_site_local,
            'sixtofour': ip.sixtofour,
            'teredo': ip.teredo,
        })

    return response

# API statistics


async def fetch_lookup_stats(countries, *, conn):
    """
    Fetch how many times all, a single or multiple countries have been looked up via the API.

    Parameters
    ----------
    countries : Optional[List[str]]
        The countries to look up. If None all countries will be looked up.
    conn : Union[asyncpg.Connection, asyncpg.pool.Pool]
        The connection to the database.
    """

    if countries is not None:
        records = await conn.fetch(
            """
            SELECT count(*) AS stored_ips, CAST (sum(accessed) AS INTEGER) AS lookups, country_code
            FROM ip_storage
            WHERE country_code = ANY($1::TEXT[])
            GROUP BY country_code
            """,
            countries,
        )
    else:
        records = await conn.fetch(
            """
            SELECT count(*) AS stored_ips, CAST (sum(accessed) AS INTEGER) AS lookups, country_code
            FROM ip_storage
            GROUP BY country_code
            """
        )

    results = {
        x['country_code']: {
            'country': codes.get(x['country_code'], '??'), 'lookups': x['lookups'], 'stored_ips': x['stored_ips']
        } for x in records
    }

    return results
