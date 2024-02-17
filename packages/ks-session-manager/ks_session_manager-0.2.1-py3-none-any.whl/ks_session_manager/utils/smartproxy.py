import random

import pydantic

from ks_session_manager.env import env
from ks_session_manager.types import SessionProxy
from .phone import guess_country_by_phone_number


class SmartProxy(pydantic.BaseModel):
    country: str = "random"
    hostname: str = 'gate.smartproxy.com'
    sticky_port_min: int = 10000
    sticky_port_max: int = 10019
    rotating_port: int = 10000
    username: str | None = env.SMART_PROXY_USERNAME
    password: str | None = env.SMART_PROXY_PASSWORD


SMART_PROXY_PROXIES: dict[str, SmartProxy] = {
    "russia": SmartProxy(
        hostname="ru.smartproxy.com",
        sticky_port_min=40001,
        sticky_port_max=40010,
        rotating_port=40000
    ),
    "thailand": SmartProxy(
        hostname="th.smartproxy.com",
        sticky_port_min=30001,
        sticky_port_max=30010,
        rotating_port=30000
    ),
    "iran": SmartProxy(
        hostname="in.smartproxy.com",
        sticky_port_min=10001,
        sticky_port_max=10010,
        rotating_port=10000
    ),
    "pakistan": SmartProxy(
        hostname="pk.smartproxy.com",
        sticky_port_min=10001,
        sticky_port_max=10010,
        rotating_port=10000
    ),
    "malaysia": SmartProxy(
        hostname="my.smartproxy.com",
        sticky_port_min=30001,
        sticky_port_max=30010,
        rotating_port=30000
    ),
    "united_kingdom": SmartProxy(
        hostname="gb.smartproxy.com",
        sticky_port_min=30001,
        sticky_port_max=30010,
        rotating_port=30000
    ),
    # "iran": SmartProxy(
    #     hostname="ir.smartproxy.com",
    #     sticky_port_min=30001,
    #     sticky_port_max=30010,
    #     rotating_port=30000
    # ),
    "indonesia": SmartProxy(
        hostname="id.smartproxy.com",
        sticky_port_min=10001,
        sticky_port_max=10010,
        rotating_port=10000
    ),
    "vietnam": SmartProxy(
        hostname="vn.smartproxy.com",
        sticky_port_min=46001,
        sticky_port_max=46010,
        rotating_port=46000
    ),
    "kazakhstan": SmartProxy(
        hostname="kz.smartproxy.com",
        sticky_port_min=40001,
        sticky_port_max=40010,
        rotating_port=40000
    ),
    "usa": SmartProxy(
        hostname="us.smartproxy.com",
        sticky_port_min=10001,
        sticky_port_max=10010,
        rotating_port=10000
    ),
    "canada": SmartProxy(
        hostname="ca.smartproxy.com",
        sticky_port_min=20001,
        sticky_port_max=20010,
        rotating_port=20000
    ),
    "india": SmartProxy(
        hostname="in.smartproxy.com",
        sticky_port_min=10001,
        sticky_port_max=10010,
        rotating_port=10000
    ),
    "kenya": SmartProxy(
        hostname="ke.smartproxy.com",
        sticky_port_min=45001,
        sticky_port_max=45010,
        rotating_port=45000
    ),
    "philippines": SmartProxy(
        hostname="ph.smartproxy.com",
        sticky_port_min=40001,
        sticky_port_max=40010,
        rotating_port=40000
    ),
    "south_africa": SmartProxy(
        hostname="za.smartproxy.com",
        sticky_port_min=40001,
        sticky_port_max=40010,
        rotating_port=40000
    ),
    "senegal": SmartProxy(
        hostname="sn.smartproxy.com",
        sticky_port_min=49001,
        sticky_port_max=490010,
        rotating_port=49000
    ),
    "romania": SmartProxy(
        hostname="ro.smartproxy.com",
        sticky_port_min=13001,
        sticky_port_max=13010,
        rotating_port=13000
    ),
    "morocco": SmartProxy(
        hostname="ma.smartproxy.com",
        sticky_port_min=40001,
        sticky_port_max=40010,
        rotating_port=40000
    ),
    "algeria": SmartProxy(
        hostname="gate.smartproxy.com",
        sticky_port_min=10001,
        sticky_port_max=10010,
        rotating_port=10000,
        username="user-kservice-country-dz"
    ),
    "tajikistan": SmartProxy(
        hostname="gate.smartproxy.com",
        sticky_port_min=10001,
        sticky_port_max=10010,
        rotating_port=10000,
        username="user-kservice-country-tj"
    ),
    "brazil": SmartProxy(
        hostname="br.smartproxy.com",
        sticky_port_min=10001,
        sticky_port_max=10010,
        rotating_port=10000,
    ),
    "mexico": SmartProxy(
        hostname="mx.smartproxy.com",
        sticky_port_min=20001,
        sticky_port_max=20010,
        rotating_port=20000,
    ),

}
DEFAULT_SMART_PROXY = SmartProxy(
    hostname="gate.smartproxy.com",
    sticky_port_min=10001,
    sticky_port_max=10010,
    rotating_port=7000
)


async def get_proxy_by_country(country: str, *, rotating: bool = False) -> SessionProxy:
    """Fetches a proxy by country.

    Args:
        country (str): The country of the desired proxy.
        rotating (bool, optional): Whether to use a rotating proxy. Defaults to False.

    Returns:
        SessionProxy: The fetched proxy.

    """
    smartproxy_by_country = SMART_PROXY_PROXIES.get(country)

    if not bool(smartproxy_by_country):
        smartproxy_by_country = DEFAULT_SMART_PROXY

    if rotating:
        port = smartproxy_by_country.rotating_port
    else:
        port = random.randint(smartproxy_by_country.sticky_port_min, smartproxy_by_country.sticky_port_max)

    return SessionProxy(
        scheme='http',
        hostname=smartproxy_by_country.hostname,
        port=port,
        username=smartproxy_by_country.username,
        password=smartproxy_by_country.password,
    )


async def get_proxy_by_phone_number(phone_number: str, *, rotating: bool = False) -> SessionProxy:
    """
    Get a proxy based on the given phone number.

    Parameters:
    - phone_number (str): The phone number used to determine the country.
    - rotating (bool, optional): Flag indicating whether to use a rotating proxy. Default is False.

    Returns:
    - SessionProxy: The proxy obtained based on the phone number and country.

    """
    phone_country = guess_country_by_phone_number(phone_number)
    return await get_proxy_by_country(phone_country, rotating=rotating)
