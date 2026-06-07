DOMAIN = "nextenergy"

NEXTENERGY_BASE_URL = "https://mijn.nextenergy.nl/Website_CW"
NEXTENERGY_MARKET_PRICES_URL = f"{NEXTENERGY_BASE_URL}/MarketPrices"
NEXTENERGY_SCREENSERVICE_URL = (
    f"{NEXTENERGY_BASE_URL}/screenservices/Website_CW/Blocks"
    "/WB_EnergyPrices/DataActionGetDataPoints"
)
NEXTENERGY_MODULE_VERSION_URL = f"{NEXTENERGY_BASE_URL}/moduleservices/moduleversioninfo"
NEXTENERGY_MODULE_INFO_URL = f"{NEXTENERGY_BASE_URL}/moduleservices/moduleinfo?cached"
NEXTENERGY_BLOCK_SCRIPT_PATH = "/Website_CW/scripts/Website_CW.Blocks.WB_EnergyPrices.mvc.js"
NEXTENERGY_ANONYMOUS_CSRF_TOKEN = "T6C+9iB49TLra4jEsMeSckDMNhQ="
NEXTENERGY_VIEW_NAME = "MainFlow.MarketPrices"

UPDATE_INTERVAL_MINUTES = 30
VERSION_CACHE_HOURS = 6

TIMEZONE = "Europe/Amsterdam"
