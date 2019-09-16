import asyncio
import logging

import backoff
import httpx

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
FIAT = config("FIAT").split(",")
ERC20 = config("ERC20").split(",")
OER = config("OER")
CMC = config("CMC")

app = Starlette(debug=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.route("/ticker")
async def ticker(request):
    data = await get_data()
    if not data:
        return HTMLResponse(content="<html><body></body</html>", status_code=424)
    return templates.TemplateResponse("ticker.html", {"request": request, "data": data})


async def get_data():
    """Get data from relevant APIs using internal functions.
    
    Returns:
        dict -- Ticker data, field as key, data as value.
    """
    fx = await get_fx()
    cmc = await get_cmc()
    try:
        eth = cmc["ETH"]
    except KeyError:
        logging.warn(f"CMC data failure: {cmc}")
        return None
    data = {
        "vol": "%.2fM" % (float(eth["quote"]["USD"]["volume_24h"]) / 1000000),
        "supply": "%.2fM" % (float(eth["circulating_supply"]) / 1000000),
        "fiat": {f: "%.2f" % (float(eth["quote"]["USD"]["price"]) * fx[f]) for f in FIAT},
        "erc20": {e: "%.2f" % (float(cmc[e]["quote"]["USD"]["price"])) for e in ERC20},
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


@cached(ttl=297, cache=Cache.MEMORY, key="get_cmc", namespace="main")
async def get_cmc(num: int = 300):
    """Get data from CoinMarketCap API.
    
    Keyword Arguments:
        num {int} -- Limit API return to this many tokens (default: {300})
    
    Returns:
        dict -- Symbol code as key, data as value.
    """
    log.info("Fetching live CMC")
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": CMC}
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit={num}"
    client = httpx.AsyncClient()
    resp = await client.get(url, headers=headers)
    if resp.status_code != 200 or resp.json()["status"]["error_code"] != 0:
        log.warn(f"CMC HTTP {resp.status_code} {resp.json()['status']['error_code']}")
        return {}
    return {item["symbol"]: item for item in resp.json()["data"]}
