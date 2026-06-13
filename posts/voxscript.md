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

It has no GitHub repo — it was a weekend experiment in turning text into natural-sounding dialog without touching a microphone.
