title: cryptboard — Public Encrypted Dead Drops Over GitHub
description: Public encrypted dead drops over GitHub — anyone can see the files, but only the intended recipient can read them.
date: 2026-06-12
---

Post encrypted messages to a public GitHub repo. Anyone can see the files exist, but without the right ID they're just random noise. Since every message is tried by brute force during receive, there's no way to tell which message belongs to which recipient — or even if any given message is real at all.

[cryptboard on GitHub](https://github.com/ryonsherman/cryptboard)

## How it works

A single Python script using AES-256-CBC. The ID is a 64-character hex string — SHA-256 hashed into an AES key. Each message is a JSON file in `messages/` with two fields: `h` (encrypted header, plaintext is always `CRYPTBOARD`) and `b` (encrypted body). Random IV per message. No sender info, no timestamps, no metadata of any kind.

Sending forks the repo, commits a new message file, and opens a pull request. A GitHub Actions workflow validates it's an additive-only change to `messages/` with valid base64 — then auto-merges. Receiving does a shallow clone and brute-force decrypts every header. Header decrypts are microseconds, so scanning thousands of messages is fast.

## The header trick

The fixed header plaintext is key to the design. Instead of deriving per-message metadata (which would leak information), every message includes an encrypted `CRYPTBOARD` string. When you receive, you try decrypting each header with your key. Only yours succeed. This means the receiver knows nothing about which blobs are theirs until they try — and an attacker with the full repo can't distinguish real messages from noise without every possible key.

## No metadata

No timestamps in the message body. No encryption metadata beyond the IV. No sender identity. The UUID filenames are random. The CI workflow rejects any PR that modifies or deletes existing files — the repo is append-only. This means even GitHub itself can't tell you which user sent which message, since all sends go through PRs from forks.

## Plausible deniability

Since any message can be decrypted by any ID (the header just won't match), there's no way to prove a given blob is intended for a given recipient. Combined with random filenames and no metadata, every message in the repo is indistinguishable from noise to anyone without the right key.

## Usage

```
cryptboard gen-id                      # generate a 64-char hex ID
cryptboard send <id> "message"         # encrypt and post
cryptboard receive <id>                # brute-force decrypt all messages
cryptboard receive <id> --since 2026-01-01  # narrow the window
```

Requires `gh` (GitHub CLI) for sending, nothing but Python for receiving.
