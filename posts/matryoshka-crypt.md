title: Matryoshka Crypt — Nested Encryption Layers Like a Russian Doll
description: A Python CLI that encrypts files through multiple nested encryption layers with different algorithms, interleaved with junk layers for obfuscation.
date: 2026-06-17
---

Encrypt a file with one password, and behind the scenes your data passes through a stack of cryptographic primitives in a structure inspired by Russian nesting dolls.

```
 plaintext
    ↓
 ChaCha20-Poly1305  ← real layer
    ↓
 AES-256-GCM        ← real layer
    ↓
 ChaCha20-Poly1305  ← real layer
    ↓
 ChaCha20-Poly1305  ← junk layer (wraps everything below)
    ↓
 ChaCha20-Poly1305  ← junk layer (wraps everything below)
    ↓
 encrypted file (looks like random noise)
```

## How it works

By default, the tool uses 5 layers: 2 junk layers on the outside wrapping 3 real layers on the inside. Junk layers encrypt random data (they're real encryption — the plaintext just happens to be ciphertext from the layer below). Real layers encrypt your actual payload. An attacker can't tell which layers are real without decrypting them all.

The container is **nested**, not flat. Each layer wraps the next inside its ciphertext. The file on disk contains only the outermost chunk's metadata — inner layers are hidden inside ciphertext. An attacker can't determine the layer count or structure without sequential decryption.

```
[salt][nonce][length][ciphertext containing...]
  [salt][nonce][length][ciphertext containing...]
    [salt][nonce][length][ciphertext containing...]
      ...
```

Decryption peels layers iteratively: parse the outermost chunk, decrypt it, parse the next chunk from the result, and so on. Each layer must be decrypted in sequence — you can't skip ahead.

## Algorithm diversity

The real layers alternate between ChaCha20-Poly1305 and AES-256-GCM. Two different cryptographic primitives protect your data — breaking one doesn't expose the plaintext. Junk layers always use ChaCha20 (cheaper, since their output is discarded anyway).

## Key derivation

All keys are derived from a single password using HKDF-SHA256 with per-layer context strings ("junk-0", "junk-1", "real-0", "real-1", "real-2"). No salt is stored in the file. Everything is deterministic from the password. Layer count is also derived from the password (actually from the user's parameter), meaning an attacker doesn't even know how many layers to peel.

## No metadata

The output file has no header, no magic bytes, no indication of how many layers exist or what algorithms were used. It looks like random bytes. A wrong password fails at the first layer with a clear error — no partial or garbled output.

## Usage

```
python -m matryoshka encrypt -i secret.txt -o secret.mryo -p "passphrase"
python -m matryoshka decrypt -i secret.mryo -o secret.txt -p "passphrase"
```

Custom layer counts (odd, minimum 3):

```
python -m matryoshka encrypt -i secret.txt -o secret.mryo -p "passphrase" --layers 9
```

## The bugs that made it real

The initial implementation had three bugs that the test suite caught:

**Junk layers overwrote data instead of wrapping it.** The junk layer loop created independent encrypted random data and assigned it to `data`, discarding the real layers entirely. Fixed by having junk layers encrypt the accumulated data (which contains the real layers) instead of random bytes separately.

**Decryption assumed flat format but encryption was nested.** The original decrypt tried to parse all five chunks upfront from the file. But in the nested format, only chunk_0's metadata is in the file — inner chunks are embedded inside ciphertext. Fixed by changing decryption to iterative peeling.

**InvalidTag exceptions weren't caught.** The cryptography library raises `InvalidTag` (not `ValueError`) on wrong password or corrupted data. Had to import and catch it explicitly.

## What I Learned

- **Nested encryption is a natural fit** for layered crypto. Each layer wrapping the previous creates a clean, iterative decrypt loop.
- **Algorithm diversity is cheap.** Alternating ChaCha20 and AES-GCM adds real security with minimal code complexity.
- **HKDF with context strings is elegant.** Deriving independent keys from one password with different context strings is clean and well-supported by the cryptography library.
- **Design docs diverge from implementation.** The initial plan described a flat format, but the code naturally produced a nested one. Always update docs after implementation changes.
- **Testing catches real bugs.** All three bugs were caught by the test suite before any manual testing.
- **Minimal dependencies are achievable.** The entire project runs on one external package (`cryptography`). The rest is stdlib.
