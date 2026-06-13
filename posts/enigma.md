title: Enigma — A Simulated Enigma Machine in Python
description: A Python simulation of the Enigma machine with 8 rotor wirings, plugboard, ring settings, and a brute-force cracker.
date: 2026-06-12
---

I wanted to understand how the Enigma machine actually worked, so I built one.

This Python implementation simulates a full three-rotor Enigma — the same class of machine used by Germany during WWII. It has everything: rotors with historical wiring, turnover points, a plugboard, and a reflector.

## The signal path

Every time you press a key, the rightmost rotor steps forward. When a rotor reaches its turnover point (a specific letter), it kicks the rotor to its left. It's a mechanical odometer — III clicks through every letter, then II steps once, and so on.

The electrical signal travels through the plugboard first (swapping pairs of letters), then forward through the rotors from right to left, hits the reflector (which bounces it back on a different path), then backward through the rotors left to right, and finally through the plugboard again. The result is the encrypted letter.

Because of the reflector, encryption and decryption are the same operation — feeding the ciphertext back through the machine with the same settings gives you the plaintext. This is historically accurate and surprisingly elegant.

## Rotor wiring

The 8 rotor types and 3 reflectors are modeled from the actual historical specifications. Each rotor has a unique substitution cipher and a turnover point — the letter at which it advances the next rotor. Rotors VI, VII, and VIII have two turnover points instead of one (a late-war feature).

The ring setting offsets the wiring relative to the rotor's alphabet ring, adding another layer of key space.

## Brute-force cracker

The cracker tries all combinations of rotor order (60 permutations of 5 rotors taken 3 at a time) and starting positions (26^3 = 17,576) — about a million combinations total. It uses Python's multiprocessing to parallelize across CPU cores.

Each candidate decryption is scored using a combination of index of coincidence and chi-squared analysis against English letter frequencies. Lower scores are more likely to be correct English text.

There's also a crib mode — if you know a word that appears in the plaintext, the cracker can narrow the search dramatically by only scoring decryptions that contain that word.

## What I Learned

- **Building is the best way to understand** — I could have read Wikipedia articles about the Enigma for hours and not understood it as deeply as one weekend of writing code. The signal path through plugboard → rotors → reflector → rotors → plugboard only clicks when you implement it yourself.
- **Reflector symmetry is beautiful** — The reflector makes encryption and decryption the same operation. Feed ciphertext back through the same settings and you get plaintext. This is historically accurate and mathematically elegant.
- **Index of coincidence is a superpower** — Scoring candidate decryptions by how well they match expected letter frequencies lets you find correct keys among millions of possibilities without reading any of them. It's the same technique that broke the real Enigma.
- **Multiprocessing is free speed** — A million rotor combinations × starting positions is trivially parallel. The cracker scales to all available cores with almost no effort.
- **Historical rotors had quirks** — Late-war rotors VI, VII, and VIII had two turnover points instead of one. Little details like this make simulation fun — you're not just implementing an algorithm, you're recreating a real piece of engineering history.
