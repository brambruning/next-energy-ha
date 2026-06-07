# Next Energy – Home Assistant Integratie

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Unofficiële Home Assistant integratie voor [Next Energy](https://mijn.nextenergy.nl) die dynamische stroomprijzen ophaalt en beschikbaar maakt als sensoren.

## Sensoren

| Sensor | Omschrijving | Eenheid |
|--------|-------------|---------|
| **Huidige Prijs** | Stroomprijs voor het huidige uur (incl. btw) | EUR/kWh |
| **Volgende Uur Prijs** | Stroomprijs voor het volgende uur | EUR/kWh |
| **Daggemiddelde Prijs** | Gemiddelde stroomprijs van vandaag | EUR/kWh |

De **Huidige Prijs** sensor bevat ook een attribuut `hourly_prices` met het volledige uurprijzenprofiel van de dag. Handig voor automaties of een energiedashboard.

## Installatie via HACS

1. Ga in Home Assistant naar **HACS → Integraties**.
2. Klik op de drie puntjes rechtsboven → **Aangepaste repositories**.
3. Voeg toe: `https://github.com/brambruning/next-energy-ha` als type **Integratie**.
4. Zoek naar **Next Energy** en klik op **Downloaden**.
5. Herstart Home Assistant.

## Handmatige installatie

1. Kopieer de map `custom_components/nextenergy` naar `<config>/custom_components/nextenergy`.
2. Herstart Home Assistant.

## Configuratie

1. Ga naar **Instellingen → Apparaten & Diensten → Integratie toevoegen**.
2. Zoek op **Next Energy**.
3. Klik op **Instellen** — er zijn geen inloggegevens nodig.

De integratie haalt automatisch de anonieme prijsdata op via de publieke Next Energy website en vernieuwt deze elke **30 minuten**.

## Details

- **Peilinginterval:** 30 minuten  
- **Tijdzone:** Europe/Amsterdam  
- **Bron:** `mijn.nextenergy.nl` (publieke marktprijzenpagina)  
- **Authenticatie:** niet vereist  

## Voorbeeldautomaties

### Schakel apparaat in bij negatieve stroomprijs

Start een apparaat (bijv. een boiler of wasmachine) als de stroomprijs onder nul cent daalt.

```yaml
description: "Apparaat inschakelen bij negatieve stroomprijs"
mode: single
triggers:
  - trigger: numeric_state
    entity_id: sensor.next_energy_huidige_prijs
    attribute: ct_kwh
    below: 0
conditions: []
actions:
  - action: switch.turn_on
    target:
      entity_id: switch.boiler
```

### Melding bij goedkope stroom

Stuur een notificatie als het volgende uur goedkoper is dan een drempelwaarde.

```yaml
description: "Melding als stroom goedkoop is het volgende uur"
mode: single
triggers:
  - trigger: numeric_state
    entity_id: sensor.next_energy_volgende_uur_prijs
    below: 0.10
conditions: []
actions:
  - action: notify.mobile_app
    data:
      message: >
        Stroom is goedkoop het volgende uur:
        {{ states('sensor.next_energy_volgende_uur_prijs') | float | round(4) }} EUR/kWh
```

### Schakel apparaat uit bij dure stroom

Stop een niet-kritieke belasting als de prijs boven een drempel stijgt.

```yaml
description: "Apparaat uitschakelen bij dure stroom"
mode: single
triggers:
  - trigger: numeric_state
    entity_id: sensor.next_energy_huidige_prijs
    attribute: ct_kwh
    above: 40
conditions: []
actions:
  - action: switch.turn_off
    target:
      entity_id: switch.boiler
```

### Stop teruglevering bij negatieve prijs

Stop teruglevering als de prijs negatief is.

```yaml
alias: Bij negatieve prijs zonnepanelen uitschakelen
description: Bij negatieve prijs zonnepanelen uitschakelen
triggers:
  - trigger: numeric_state
    entity_id: sensor.next_energy_huidige_prijs
    attribute: ct_kwh
    below: 0
conditions: []
actions:
  - device_id: 1c8a987be4272930ea33cec7169d6ccf
    domain: number
    entity_id: f29f3b6eeb91c12c3f4b43d844fc8aab
    type: set_value
    value: 0
mode: single



## Licentie

MIT
