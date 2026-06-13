title: GPS Asset Tracker — An Arduino-Based Logger with EEPROM Storage
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

## No GitHub repo

This was a hardware hacking project to understand low-power GPS logging from scratch — no libraries for the GPS parsing (NMEA sentences are parsed character-by-character over SoftwareSerial), no RTC (time comes from the GPS fix), and no external storage.
