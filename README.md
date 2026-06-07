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

## Licentie

MIT
