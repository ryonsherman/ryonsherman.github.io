title: Hardware RNG — SRAM PUF True Random Number Generator
description: A true hardware random number generator using SRAM PUF — exploiting random power-up states of cheap I2C memory chips.
date: 2026-06-12
---

I built a true hardware random number generator using an Arduino Nano and some dirt-cheap I2C SRAM chips. It exploits the random power-up state of uninitialized static RAM to generate entropy — the same physical phenomenon used in SRAM Physical Unclonable Functions (PUFs) for device fingerprinting and cryptographic key generation.

## The physics

Each SRAM cell is a cross-coupled inverter pair forming a bi-stable latch. When power is first applied, the circuit settles into either `0` or `1` depending on atomic-level manufacturing variations — random dopant fluctuations, oxide thickness differences, and threshold voltage mismatches between the two transistors. These variations are physically unpredictable, stable per-cell, uncorrelated between chips, and fresh each power cycle.

Holcomb, Burleson, and Fu first characterized this at UMass in 2009. I'm exploiting their exact finding on a breadboard.

## The circuit

Up to 8 PCF8570P I2C SRAM chips (256 bytes each, DIP-8, ~$2) share a common Vcc rail switched by a single 2N7000 N-channel MOSFET on Arduino D2. A 10kΩ pull-down holds the gate low during boot so the SRAMs stay off while the Arduino's GPIOs are tri-state. Two more 10kΩ resistors pull up the I2C bus, and each chip gets a 100nF decoupling cap.

The sequence: power all chips off → wait 20ms (+ `micros()` jitter for extra entropy) → power on → wait 10ms → read each chip sequentially over I2C at 400kHz → repeat. The jitter in the timing itself adds entropy since `micros()` depends on unpredictable interrupt timing.

## The sketch

The loop reads 256 bytes raw from each chip, applies debiasing, runs a health check, and streams the result over Serial at 115200 baud.

Three debiasing methods are configurable at compile time:

- **XOR-fold** (default) — XOR each byte with the previous. No throughput loss, removes additive bias.
- **Von Neumann** — pair consecutive bits: `01` → `1`, `10` → `0`, discard `00`/`11`. Eliminates per-bit bias but ~25% throughput.
- **SHA-256** — cryptographic whitening via `avr-crypto-lib`. Full NIST SP 800-90B conditioning.

The health check is a repetition count test: if the same byte appears more than 32 times consecutively, the cycle is discarded. This catches stuck bits, dead chips, or wiring faults.

Raw SRAM power-up data has a per-cell zeros rate of 45–55% and min-entropy of ~2–4 bits per byte — definitely needs conditioning before cryptographic use.

## Performance

With 3 chips and XOR-fold: ~5.9 KB/s. With 8 chips and SHA-256: ~900 B/s conditioned. Throughput is limited more by I2C read speed than by SRAM settle time.

## What I Learned

- **Entropy is everywhere if you know where to look** — Every SRAM cell has a random power-up state determined by atomic-scale manufacturing variations. This is the same physics used in PUFs for cryptographic key generation, chip fingerprinting, and anti-counterfeiting.
- **Debiasing is essential** — Raw SRAM data has 45-55% zeros rate with 2-4 bits of min-entropy per byte. Using XOR-fold preserves throughput while removing bias, and SHA-256 conditioning brings it to full cryptographic quality.
- **Timing jitter adds entropy** — Simply adding `micros()` jitter between power-off and power-on introduces entropy from unpredictable interrupt timing — a free bonus source.
- **Health checks prevent silent failure** — The repetition count test catches stuck bits, dead chips, and wiring faults before the bad data reaches the output. In cryptographic hardware, failing loudly is better than producing subtly biased output.
- **The circuit is dead simple** — An N-channel MOSFET, two pull-up resistors, and a handful of decoupling caps is all it takes to turn $2 I2C SRAM chips into a true random number generator. The hardware is trivial; the understanding of what's happening at the physical level is not.
