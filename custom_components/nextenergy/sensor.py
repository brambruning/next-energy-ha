from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NextEnergyCoordinator

PRICE_UNIT = f"EUR/{UnitOfEnergy.KILO_WATT_HOUR}"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: NextEnergyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        NextEnergyCurrentPriceSensor(coordinator),
        NextEnergyNextHourPriceSensor(coordinator),
        NextEnergyAveragePriceSensor(coordinator),
    ])


class _NextEnergyBaseSensor(CoordinatorEntity[NextEnergyCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PRICE_UNIT

    def __init__(self, coordinator: NextEnergyCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"nextenergy_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "nextenergy_prices")},
            "name": "Next Energy",
            "manufacturer": "Next Energy",
            "model": "Dynamische Prijzen",
        }


class NextEnergyCurrentPriceSensor(_NextEnergyBaseSensor):
    _attr_name = "Huidige Prijs"
    _attr_icon = "mdi:lightning-bolt"

    def __init__(self, coordinator: NextEnergyCoordinator) -> None:
        super().__init__(coordinator, "current_price")

    @property
    def native_value(self) -> float | None:
        current = self.coordinator.data.get("current") if self.coordinator.data else None
        return current["total_eur_kwh"] if current else None

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        current = data.get("current") or {}
        return {
            "ct_kwh": current.get("total_ct_kwh"),
            "hour": current.get("hour"),
            "start": current.get("start"),
            "end": current.get("end"),
            "date": data.get("date"),
            "fetched_at": data.get("fetched_at"),
            "hourly_prices": [
                {
                    "hour": p["hour"],
                    "eur_kwh": p["total_eur_kwh"],
                    "ct_kwh": p["total_ct_kwh"],
                    "start": p["start"],
                }
                for p in data.get("points", [])
            ],
        }


class NextEnergyNextHourPriceSensor(_NextEnergyBaseSensor):
    _attr_name = "Volgende Uur Prijs"
    _attr_icon = "mdi:lightning-bolt-circle"

    def __init__(self, coordinator: NextEnergyCoordinator) -> None:
        super().__init__(coordinator, "next_hour_price")

    @property
    def native_value(self) -> float | None:
        next_hour = self.coordinator.data.get("next_hour") if self.coordinator.data else None
        return next_hour["total_eur_kwh"] if next_hour else None

    @property
    def extra_state_attributes(self) -> dict:
        next_hour = (self.coordinator.data or {}).get("next_hour") or {}
        return {
            "ct_kwh": next_hour.get("total_ct_kwh"),
            "hour": next_hour.get("hour"),
            "start": next_hour.get("start"),
            "end": next_hour.get("end"),
        }


class NextEnergyAveragePriceSensor(_NextEnergyBaseSensor):
    _attr_name = "Daggemiddelde Prijs"
    _attr_icon = "mdi:chart-line"

    def __init__(self, coordinator: NextEnergyCoordinator) -> None:
        super().__init__(coordinator, "average_price")

    @property
    def native_value(self) -> float | None:
        average = (self.coordinator.data or {}).get("average")
        return average["eur_kwh"] if average else None

    @property
    def extra_state_attributes(self) -> dict:
        average = (self.coordinator.data or {}).get("average") or {}
        return {
            "ct_kwh": average.get("ct_kwh"),
        }
