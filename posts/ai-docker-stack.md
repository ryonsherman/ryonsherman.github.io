title: Running LLMs and Image Generation on Consumer Hardware — A Two-Machine Docker Stack
description: Running LLMs, image generation, TTS, and a multi-agent tool ecosystem on two AMD-powered consumer machines with no dedicated GPU.
date: 2026-06-12
---

Two AMD-powered machines, no dedicated GPU, no CUDA. Just a Ryzen 9 6900HX with a Radeon 680M iGPU (RDNA2, Vulkan-only) and 23 GB of shared RAM on each. This stack runs LLM inference, image generation, text-to-speech, and a multi-agent tool ecosystem — all in Docker, all on consumer hardware.

## Architecture

Two identical workstations on a local LAN. Machine 1 runs the full LLM server stack (llama.cpp with RPC, Open WebUI, LiteLLM, Kokoro TTS, Caddy reverse proxy). Machine 2 acts as a remote RPC worker, contributing its GPU memory for distributed inference. Both machines also run stable-diffusion.cpp for image generation with FLUX.1-dev.

The key insight: llama.cpp's RPC support distributes model layers across GPU workers. With `--tensor-split 0.5,0.5`, each endpoint gets half the model layers. Both iGPUs combined can fit models that neither could run alone — like Qwen3.5-35B-A3B at Q4_K_M (~20 GiB), split roughly 10 GiB per machine.

## Model Inference

The llama-server container itself has no GPU access — it's purely a coordinator. All GPU work is delegated to RPC workers:

```
llama-server ──RPC──► llama-rpc (local, Vulkan0, ~50% of layers)
                │
                └──RPC──► remote:50052 (remote, Vulkan0, ~50% of layers)
```

Three models have been tested:

- **Qwen3.5-35B-A3B Q4_K_M** (~20 GiB) — MoE with 3B active parameters. General chat + coding.
- **Qwen3.6-35B-A3B Q4_K_M** (~20 GiB) — ~14% faster, better coding.
- **DeepSeek-Coder-33B-Instruct Q4_K_M** (~19 GiB) — Dense 33B, all params active. Slower.

The MoE models are ~10x faster than the dense 33B because only 3B parameters activate per token. File size is similar but throughput is vastly different. On memory-constrained hardware, MoE is the clear winner.

Model switching is handled by `llama-docker.sh` — it saves the model path, rewrites LiteLLM config, and restarts services. Vision models are auto-detected via `.mmproj.gguf` files alongside the GGUF.

## Image Generation

stable-diffusion.cpp is built from source with Vulkan support. FLUX.1-dev uses four model files: the diffusion model (6.5 GB), VAE, CLIP-L, and T5-XXL. LoRA support is built in. A separate instance on machine 2 runs FLUX.1-Kontext-dev for instruction-based image editing (remixing).

Only one stack runs at a time — both use port 8000 and share the GPU memory.

## The MCP Tool Ecosystem

Four Model Context Protocol servers run as separate containers, all auto-injected into Open WebUI via a middleware patch:

- **Web Search** — DuckDuckGo + Reddit search (consolidated from separate services)
- **Memory** — Long-term semantic search with fastembed
- **Memory (read-only)** — For temporary chats (`local:*` prefix)
- **Local Assistant** — Weather (NWS API) and traffic (TomTom API), with TTS-friendly speech output

The middleware patch checks whether a chat is temporary and swaps writeable memory for read-only accordingly.

## Text-to-Speech

Kokoro-FastAPI runs on CPU (the GPU is busy with the LLM). The `af_heart` voice is remapped to `af_bella` for a warmer tone. Two patches are applied at container entrypoint: unit normalization ("mph" → "miles per hour") and compass direction expansion ("WNW" → "west-northwest").

## LiteLLM API Proxy

LiteLLM exposes the active model at `/v1/` on port 4000 with authentication. This means any OpenAI-compatible tool can connect — aider, Continue VS Code extension, or anything else:

```
aider --model openai/qwen3.6 --openai-api-base http://workstation1:4000/v1
```

## Slot Monitor

A live terminal UI (`monitor.py`) polls llama-server's `/slots` and `/health` endpoints every 3 seconds. It tracks per-slot activity (prefill/generating/idle), tokens decoded and remaining, instant tok/s, and ETA. Completion history auto-persists to JSONL. Two rendering modes: Rich (color, progress bars) and Plain (ASCII-only) for headless SSH sessions.

## Key Lessons

1. **MoE vs Dense** — 35B MoE (3B active) is ~10x faster than 33B dense. Same file size, vastly different throughput. Always prefer MoE on constrained hardware.

2. **RPC decouples GPU access** — The llama-server container doesn't need `/dev/dri`. All GPU work is delegated to RPC workers. Startup ordering matters: RPC workers need time to initialize Vulkan before llama-server connects.

3. **Startup race conditions** — Docker Compose `--depends-on` only waits for container start, not service readiness. A full stop/start cycle is more reliable than individual restarts.

4. **Context budgeting** — With 23 GB shared RAM and ~20 GiB models, KV cache space is tight. 65k context works for MoE models but would need reduction for dense models.

5. **Two machines, one cluster** — Spreading inference across two consumer laptops over LAN is viable. Network latency adds ~5-10% overhead but doubles the available GPU memory. The same approach could scale to more nodes for larger models.
