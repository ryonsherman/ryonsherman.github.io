title: Canary — A Cryptographic Proof-of-Life Android App
description: An Android app that turns NFC tags into tamper-evident, Bitcoin-anchored daily check-in proofs.
date: 2026-06-12
---

I built an Android app that turns an NFC tag into a tamper-evident daily check-in system. Tap your phone to a sticker, and it generates a signed, chained, Bitcoin-anchored proof that you're alive.

## How it works

The app runs on Android 9+ with Jetpack Compose and uses:

- **NFC** — reads/writes a secret key to an NTAG RFID tag
- **Android Keystore** — ECDSA P-256 signing key stored in hardware-backed storage
- **BIP39** — 12-word recovery phrase generated from 128 bits of entropy
- **AES-GCM** — encrypted backup of the GitHub token, recoverable via QR code

When you tap your phone to the tag, the app signs a canary file containing the current timestamp, a monotonic counter, and the SHA-256 hash of the previous canary. It pushes the file to a public GitHub repo via the Contents API.

A GitHub Action then GPG-clearsigns the file, submits it to the OpenTimestamps calendar (anchored to the Bitcoin blockchain), and creates a signed git tag.

The result is a publicly verifiable chain of life signals — anyone can check the repo and confirm you were alive on a given day.

## Chain integrity

Each canary chains to the previous one via SHA-256. Breaking the chain would require either:

- Forging a valid ECDSA signature without access to the private key
- Rewriting every subsequent canary's hash reference
- Tampering with the OpenTimestamps proofs anchored in the Bitcoin blockchain

The source is on GitHub at [ryonsherman/canary](https://github.com/ryonsherman/canary/), with a public dashboard at `ryonsherman.github.io/canary/` that verifies chain integrity client-side using the Web Crypto API — no server needed.

## What I Learned

- **Hash chaining is elegant** — Each canary links to the previous one via SHA-256, creating a tamper-evident chain. Breaking it requires either forging an ECDSA signature or rewriting every subsequent block — the same principle that makes blockchains work.
- **OpenTimestamps is magical** — Anchoring a hash to the Bitcoin blockchain costs essentially nothing and provides a permanent, publicly verifiable timestamp that anyone can check without trusting a third party.
- **Android Keystore hardware backing** — The ECDSA signing key never leaves the device's secure enclave. Even if the app is compromised, the key can't be extracted. This is the right way to handle secrets on mobile.
- **NFC for key transport** — Storing the recovery seed on an NTAG tag means the key is physically bound to a token. No cloud backup, no server compromise, no sync issues. You have the tag or you don't.
- **GitHub Actions as build/deploy pipeline** — Using CI to clearsign, timestamp, and tag each canary turned GitHub into a free public notary with built-in verification.
