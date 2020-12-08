import asyncio
import logging

import httpx
import san
from san.error import SanError

from aiocache import cached, Cache
from starlette.applications import Starlette
from starlette.config import Config
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

log = logging.getLogger()
logging.basicConfig(
    format="%(asctime)s %(levelname)-6s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Configuration from environment variables or '.env' file.
config = Config(".env")
DEBUG = config("DEBUG")
DEFAULT_SAN_FIELDS = config("DEFAULT_SAN_FIELDS").split(",")
FIAT = config("FIAT").split(",")
ERC20 = config("ERC20").split(",")
OER = config("OER")
SAN = config("SAN")

app = Starlette(debug=DEBUG)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.route("/ticker")
async def ticker(request):
    data = await get_data()
    if not data:
        return HTMLResponse(content="<html><body></body</html>", status_code=424)
    return templates.TemplateResponse("ticker.html", {"request": request, "data": data})


@app.route("/sidebar")
async def sidebar(request):
    data = await get_data()
    if not data:
        return HTMLResponse(content="<html><body></body</html>", status_code=424)
    return templates.TemplateResponse("sidebar.html", {"request": request, "data": data})


async def get_data():
    """Get data from relevant APIs using internal functions.

    Returns:
        dict -- Ticker data, field as key, data as value.
    """
    fx = await get_fx()
    san = await get_san()
    try:
        eth = san["ETH"]
    except KeyError:
        logging.warn(f"SAN data failure: {san}")
        return None
    eth["price_fiat"] = {f: "%.2f" % (float(eth["price_usd"]) * fx[f]) for f in FIAT}
    data = {
        "eth": eth,
        "erc20": {e: san[e] for e in ERC20},
    }
    log.info(data)
    return data


@cached(ttl=3597, cache=Cache.MEMORY, key="get_fx", namespace="main")
async def get_fx():
    """Get data from OpenExchangeRates API.

    Returns:
        dict -- Symbol code as key, data as value.
    """
    log.info("Fetching live FX")
    url = f"https://openexchangerates.org/api/latest.json?app_id={OER}"
    client = httpx.AsyncClient()
    resp = await client.get(url)
    if resp.status_code != 200:
        log.warn(f"FX HTTP {resp.status_code}")
        return {}
    return resp.json()["rates"]


@cached(ttl=30, cache=Cache.MEMORY, key="get_san", namespace="main")
async def get_san(default_san_fields: list = DEFAULT_SAN_FIELDS):
    """Get data from Santiment API.

    Returns:
        dict -- Symbol code as key, data as value.
    """
    log.info("Fetching live SAN")
    try:
        resp = san.get("projects/all", return_fields=default_san_fields)
        from pprint import pprint
        pprint(resp.to_dict('records'))
        return {item["ticker"]: item for item in resp.to_dict('records')}
    except SanError as se:
        print(se)
