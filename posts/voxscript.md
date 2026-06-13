title: Voxscript — A CLI Script-to-Speech Tool with Piper TTS
description: A CLI tool that turns dialog scripts into multi-voice audio using Piper TTS — no DAW or audio editing required.
date: 2026-06-12
---

I needed a way to turn dialog scripts into multi-voice audio without a DAW or audio editing.

Voxscript is a Python CLI that reads a text file of dialog lines and produces a WAV file using [Piper TTS](https://github.com/rhasspy/piper) — a fast neural text-to-speech engine that runs entirely locally on a CPU.

## How it works

You write a script in a simple `SPEAKER: dialog` format with blank lines for pacing. The tool parses each utterance, pipes them through Piper voice models, and concatenates everything into a single WAV with configurable silence between speakers.

## Multi-voice support

You provide a JSON voice map to assign different Piper voices to different speakers. Any speaker not mapped falls back to a default voice.

## Technical bits

- Text is chunked at 500 characters (sentence-aware) before synthesis, keeping audio segments manageable for Piper
- Audio is concatenated as 16-bit PCM WAV, mono
- Blank lines in the script insert longer pauses and reset the current speaker, letting you control pacing
- Rate control via `--length-scale` (1.0 is normal, lower = faster, higher = slower)

## What I Learned

- **Piper TTS is surprisingly good for local CPU** — It runs real-time neural TTS on a laptop CPU with no GPU. Voice quality is decent across multiple models, and switching voices between lines is seamless.
- **Sentence-aware chunking matters** — Piper has a maximum input length. Naively splitting at the character boundary produces broken audio mid-word. Chunking at sentence boundaries (500 chars) keeps segments natural.
- **Audio concatenation is trivial** — Once you have individual WAV segments as 16-bit PCM byte arrays, joining them with silence padding is just array concatenation. Audio programming doesn't have to be complicated.
- **Voice mapping makes scripts flexible** — A JSON voice map decouples the script from the voices. Change the map without touching the script to try different voice combinations.
- **CLI-first design works** — A simple `SPEAKER: dialog` format with blank lines for pacing is intuitive enough to write in any text editor. No markup language to learn, no GUI to fight.
