title: QRVid — Store Binary Data in QR Code Videos
description: Encode arbitrary binary data into QR code videos for YouTube storage and decode it back. Yes, it works.
date: 2026-06-12
---

Encode arbitrary binary data into QR code videos for YouTube storage, and decode it back from a downloaded video. Yes, it works.

<a href="https://github.com/ryonsherman/qrvid"><img src="https://github.com/ryonsherman/qrvid/raw/main/screenshots/preview.gif" width="768" alt="QR code video preview"></a>

[QRVid on GitHub](https://github.com/ryonsherman/qrvid)

## How it works

Input data is split into 300-byte chunks with a 20-byte header (magic, format version, flags, total chunks, chunk index, chunk length, total data length, CRC32). Each chunk is rendered as a QR code with error correction H (30%). QRs are laid out on a 1920×1080 H.264 video frame in a configurable grid — default 6×5 = 30 QRs per frame. Each layout is held for N frames (default 3 at 30 fps = 0.1s), then the next layout plays. YouTube's 33-second minimum duration is enforced with trailing black frames.

## Reading from a video

The decoder scans every frame in parallel using a process pool. Each frame is checked against a black threshold (skipping padding frames), then QR codes are detected with pyzbar (falling back to OpenCV's built-in detector). Duplicate payloads are discarded by hash. Chunks are re-ordered by index, concatenated, and CRC32 is verified.

It handles YouTube download natively — yt-dlp with Firefox cookies and bun JS runtime for YouTube's bot challenge.

## Optional features

**Compression** — gzip level 9 before encoding. **Encryption** — AES-256-GCM with PBKDF2 key derivation (600k iterations). **Recovery** — XOR parity chunks in configurable group sizes; if chunks are lost to YouTube re-encoding artifacts, missing data can be repaired. **Integrity check** — `--verify` decodes the output right after encoding to confirm everything survives.

## Capacity

With defaults (6×5 = 30 QPF, 3 hold at 30 fps, 300 bytes/chunk):

| Duration | QRs     | Raw data  |
|----------|---------|-----------|
| 4 min    | 77,400  | ~22 MB    |
| 15 min   | 324,000 | ~82 MB    |
| 12 hours | 15M+    | ~3.9 GB   |

Tune `--cols`, `--rows`, `--hold`, and `--box-size` to trade density for readability. The `--max-duration` flag splits across multiple files for YouTube's upload limits.

## Usage

```
qrvid enc myfile.bin -o myfile.mp4                          # basic
qrvid enc myfile.bin -o myfile.mp4 --compress --password "hunter2"   # compress + encrypt
qrvid enc myfile.bin -o myfile.mp4 --recovery 1             # loss protection
qrvid dec myfile.mp4 -o restored.bin                        # decode local
qrvid dec "https://youtu.be/..." -o restored.bin            # decode from YouTube
```

Parallel frame generation (process pool) makes encoding practical — for a 1MB test file, a 6×5 layout encodes in seconds and all layouts pass verify.
