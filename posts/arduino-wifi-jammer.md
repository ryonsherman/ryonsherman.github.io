title: Arduino Wi-Fi Jammer — A 13-Node Distributed Jamming Swarm
date: 2026-06-12
---

A distributed 13-node Wi-Fi jamming system with an Arduino Nano master and 12 MH-Tiny (ATtiny88) slave boards using NRF24L01+ transceivers. The master controls slaves via I2C to coordinate jamming across Wi-Fi channels 1-13.

[![12-unit jamming array on channel 1 in controlled lab environment](https://github.com/ryonsherman/arduino-wifi-jammer/raw/main/screenshots/ch1-jamming.png)](https://github.com/ryonsherman/arduino-wifi-jammer/)

## Architecture

Each node has an NRF24L01+ module for transmitting noise. The master uses its own NRF24 in RX mode to double as a spectrum analyzer — it scans all 13 channels and visualizes signal activity as bar graphs. Slaves receive commands over a shared I2C bus: set channel, start, stop, change power, or switch patterns.

The key design decision was using I2C for control so the command bus doesn't contend with the 2.4GHz jamming signals. SPI (used by the NRF24 modules) and I2C coexist without interference.

## Fan-out algorithm

Instead of all 12 slaves hitting the same center frequency, they spread across the full 22MHz Wi-Fi channel width at 2MHz intervals:

```
center_freq + (local_idx * 2) - (group_size - 1)
```

On channel 6 (center 2437 MHz), slave 0 transmits at 2426 MHz and slave 11 at 2448 MHz. This completely blankets the channel rather than leaving gaps between overlapping transmissions.

## Operating modes

- **Single channel** — All 12 slaves fan out across one channel for maximum power density
- **Full spectrum** — Slaves spread across 2415-2470 MHz at 5MHz spacing, covering all 13 channels
- **Custom** — Assign any number of slaves to any channels (e.g. `set 4@1,2@6,2@11`)
- **Sweep** — All slaves cycle channels 1-13 together at configurable dwell (default 200ms)
- **Adaptive** — Master scans all channels for 2 seconds, identifies the busiest ones, and assigns slaves dynamically with auto-rescan every 30s

## Patterns

Beyond continuous transmission, the system supports pulsed (alternating on/off), burst (custom duty cycle), and random (per-packet LFSR frequency hopping within the assigned band).

## Hardware control

A 3-position ON-OFF-ON switch on the master provides instant physical control: position 1 triggers full-spectrum jamming, center is off for software control, position 3 starts sweep mode. This works without any PC connection.

## Legal

> ⚠️ Wi-Fi jamming is illegal in most jurisdictions. This is an educational/research project about distributed RF systems and I2C command protocols. Do not operate without proper shielding, licensing, and legal authorization.
