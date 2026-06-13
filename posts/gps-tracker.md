title: GPS Asset Tracker — An Arduino-Based Logger with EEPROM Storage
description: A battery-powered Arduino GPS tracker that logs positions to EEPROM — no SD card, no cloud, just the chip.
date: 2026-06-12
---

I built a battery-powered GPS tracker on an Arduino Nano that logs positions to internal EEPROM — no SD card, no breakout board, no cloud service. Just the chip and a GPS module.

## How it works

Power up, and the Nano wakes, powers the GPS module via a transistor switch, acquires a fix, logs the position, kills power to the GPS, opens a 5-second serial command window, then goes into watchdog-timer deep sleep. Repeat on the configured interval.

The whole power cycle is controlled by a 2N2222 transistor on D4 — GPS ground is switched so it draws zero current when off. During deep sleep the Nano itself pulls ~5µA.

## Storage in EEPROM

The ATmega328p has 1KB of EEPROM. With 10-byte records (4 bytes lat, 4 bytes lon, 2 bytes dwell counter), that's 67 positions in a ring buffer. Oldest records are overwritten when full.

The dwell counter tracks how many consecutive log cycles the tracker stayed in the same spot, which is useful for inferring parked vs. moving time.

Data is retrieved over serial with a `D` command that dumps CSV. Python scripts then convert to GPX/KML for mapping, or snap to roads using OSRM's free match API.

## Distance threshold

A movement check uses the haversine approximation — lat * 111320 m/°, lon * 111320 * cos(lat) m/° — and compares squared distance against a configurable threshold. If the tracker hasn't moved far enough, it increments the dwell counter instead of writing a new record. This saves storage for only meaningful location changes.

## Battery life

With a 1500mAh 18650, a 60-second GPS acquisition timeout, and deep sleep between cycles:

| Interval | Runtime |
|----------|---------|
| 10 min   | ~23 days |
| 15 min   | ~34 days |
| 30 min   | ~2 months |

The limiting factor is the GPS cold-fix time, not the microcontroller power draw.

## What I Learned

- **Low-power design = control every microamp** — The GPS module draws significant current, so switching its ground with a transistor makes it draw zero when off. During deep sleep the Nano pulls ~5 µA. Every component choice affects battery life.
- **EEPROM is tiny but reliable** — 1 KB holds 67 GPS fix records with no filesystem overhead, no corruption risk from power loss, and no SD card that can shake loose. Sometimes the simplest storage is the best.
- **Haversine distance checks save storage** — Checking whether the tracker actually moved before writing avoids filling the log with "still here" entries. It's a simple optimization that doubles useful recording time.
- **Watchdog timer deep sleep** — The ATmega328p's watchdog timer wakes from deep sleep at configurable intervals without an external RTC. The GPS itself provides the time — no extra chip needed.
- **NMEA parsing from scratch** — GPS sentences like `$GPGGA` are just comma-separated text. Parsing them character-by-character over SoftwareSerial teaches you exactly what information a GPS fix contains and why.
