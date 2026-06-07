from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    NEXTENERGY_ANONYMOUS_CSRF_TOKEN,
    NEXTENERGY_BASE_URL,
    NEXTENERGY_BLOCK_SCRIPT_PATH,
    NEXTENERGY_MARKET_PRICES_URL,
    NEXTENERGY_MODULE_INFO_URL,
    NEXTENERGY_MODULE_VERSION_URL,
    NEXTENERGY_SCREENSERVICE_URL,
    NEXTENERGY_VIEW_NAME,
    TIMEZONE,
    UPDATE_INTERVAL_MINUTES,
    VERSION_CACHE_HOURS,
)

_LOGGER = logging.getLogger(__name__)

_API_VERSION_RE = re.compile(
    r'callDataAction\("DataActionGetDataPoints",\s*'
    r'"screenservices/Website_CW/Blocks/WB_EnergyPrices/DataActionGetDataPoints",\s*'
    r'"([^"]+)"'
)
_HOUR_TOOLTIP_RE = re.compile(r"(\d{1,2})u")
_STRIP_NON_NUMERIC_RE = re.compile(r"[^0-9,.\-]")


def _parse_decimal(value) -> float | None:
    if value is None or value == "":
        return None
    normalized = _STRIP_NON_NUMERIC_RE.sub("", str(value))
    if not normalized:
        return None
    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    else:
        normalized = normalized.replace(",", ".")
    try:
        result = float(normalized)
        return result if result == result and abs(result) != float("inf") else None
    except ValueError:
        return None


class NextEnergyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )
        self._version_info: dict | None = None
        self._version_fetched_at: float = 0.0

    async def _async_update_data(self) -> dict:
        try:
            return await self._fetch_prices()
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Next Energy fout: {err}") from err

    async def _get_version_info(self, session: aiohttp.ClientSession) -> dict:
        now = time.monotonic()
        if self._version_info and (now - self._version_fetched_at) < VERSION_CACHE_HOURS * 3600:
            return self._version_info

        _LOGGER.debug("Next Energy: versie-info ophalen")

        async with session.get(
            f"{NEXTENERGY_MODULE_VERSION_URL}?{int(time.time())}",
            headers={"Accept": "application/json"},
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

        module_version = data.get("versionToken")
        if not module_version:
            raise UpdateFailed("Next Energy: moduleVersion niet gevonden")

        async with session.get(
            NEXTENERGY_MODULE_INFO_URL,
            headers={"Accept": "application/json"},
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

        script_version = (
            data.get("manifest", {})
            .get("urlVersions", {})
            .get(NEXTENERGY_BLOCK_SCRIPT_PATH)
        )
        if not script_version:
            raise UpdateFailed("Next Energy: block script versie niet gevonden")

        script_url = (
            f"{NEXTENERGY_BASE_URL}/scripts/"
            f"Website_CW.Blocks.WB_EnergyPrices.mvc.js{script_version}"
        )
        async with session.get(script_url, headers={"Accept": "*/*"}) as resp:
            resp.raise_for_status()
            script_text = await resp.text()

        match = _API_VERSION_RE.search(script_text)
        if not match:
            raise UpdateFailed("Next Energy: apiVersion niet gevonden in block script")

        self._version_info = {
            "moduleVersion": module_version,
            "apiVersion": match.group(1),
        }
        self._version_fetched_at = now
        _LOGGER.debug("Next Energy: versie-info geladen: %s", self._version_info)
        return self._version_info

    async def _fetch_prices(self) -> dict:
        tz = ZoneInfo(TIMEZONE)
        now = datetime.now(tz=tz)
        today = now.date()
        current_hour = now.hour

        cookie_jar = aiohttp.CookieJar()
        default_headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; HomeAssistant-NextEnergy/1.0; "
                "+https://mijn.nextenergy.nl/Website_CW/MarketPrices)"
            ),
        }

        async with aiohttp.ClientSession(
            cookie_jar=cookie_jar, headers=default_headers
        ) as session:
            version_info = await self._get_version_info(session)

            async with session.get(
                NEXTENERGY_MARKET_PRICES_URL,
                headers={"Accept": "text/html"},
            ) as resp:
                resp.raise_for_status()

            payload = {
                "versionInfo": {
                    "moduleVersion": version_info["moduleVersion"],
                    "apiVersion": version_info["apiVersion"],
                },
                "viewName": NEXTENERGY_VIEW_NAME,
                "screenData": {
                    "variables": {
                        "Graphsize": 235,
                        "IsOpenPopup": False,
                        "HighchartsJSON": "",
                        "DistributionId": 3,
                        "IsDesktop": False,
                        "IsTablet": False,
                        "IsLoading": True,
                        "NE_StartDate": "2022-07-01",
                        "Filter": {
                            "PriceIncludingVAT": True,
                            "PriceDate": today.isoformat(),
                            "CostsLevel": "TotalPrice",
                            "CurrentHour": current_hour,
                        },
                    }
                },
            }

            async with session.post(
                NEXTENERGY_SCREENSERVICE_URL,
                json=payload,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Origin": "https://mijn.nextenergy.nl",
                    "Referer": NEXTENERGY_MARKET_PRICES_URL,
                    "OutSystems-locale": "nl-NL",
                    "X-CSRFToken": NEXTENERGY_ANONYMOUS_CSRF_TOKEN,
                },
            ) as resp:
                resp.raise_for_status()
                result = await resp.json(content_type=None)

        version_changed = result.get("versionInfo", {})
        if version_changed.get("hasModuleVersionChanged") or version_changed.get("hasApiVersionChanged"):
            self._version_info = None
            self._version_fetched_at = 0.0
            raise UpdateFailed("Next Energy: build-versie gewijzigd, wordt opnieuw geprobeerd")

        data = result.get("data", {})
        point_list = data.get("DataPoints", {}).get("List", [])

        day_start = datetime(today.year, today.month, today.day, tzinfo=tz)
        points = []

        for index, point in enumerate(point_list):
            tooltip = point.get("Tooltip") or ""
            label = point.get("Label")

            if m := _HOUR_TOOLTIP_RE.search(tooltip):
                hour = int(m.group(1))
            elif label is not None and str(label).isdigit():
                hour = int(label)
            else:
                hour = index

            price_eur_kwh = _parse_decimal(point.get("Value"))
            if price_eur_kwh is None:
                continue

            start = day_start + timedelta(hours=hour)
            end = start + timedelta(hours=1)

            points.append({
                "start": start.isoformat(),
                "end": end.isoformat(),
                "hour": hour,
                "label": str(label if label is not None else hour),
                "tooltip": tooltip or None,
                "series_name": point.get("SeriesName", "Stroom"),
                "color": point.get("Color"),
                "total_eur_kwh": round(price_eur_kwh, 4),
                "total_ct_kwh": round(price_eur_kwh * 100, 3),
            })

        points.sort(key=lambda p: p["hour"])

        avg_eur = _parse_decimal(data.get("AvgElectricityPrice"))
        average = (
            {"eur_kwh": round(avg_eur, 4), "ct_kwh": round(avg_eur * 100, 3)}
            if avg_eur is not None
            else None
        )

        current = next((p for p in points if p["hour"] == current_hour), None)
        if current is None and points:
            current = points[0]

        next_hour_point = next((p for p in points if p["hour"] == current_hour + 1), None)

        return {
            "date": today.isoformat(),
            "current": current,
            "next_hour": next_hour_point,
            "average": average,
            "points": points,
            "fetched_at": now.isoformat(),
        }
