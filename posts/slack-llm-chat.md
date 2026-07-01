title: Slack LLM Chat — Persistent AI Conversations Inside Slack
description: A Slack bot that bridges conversations to OpenAI-compatible LLM backends. Each chat is a private channel with persistent history.
date: 2026-07-01
---

I wanted to chat with LLMs inside Slack without switching to a web browser. Existing solutions either didn't persist history, didn't support multiple providers, or made me leave the app I already live in. So I built a Slack bot that turns private channels into persistent AI conversations.

## The problem

Chatting with LLMs usually means opening a browser, going to ChatGPT or Claude, and losing context when you close the tab. I wanted conversations that live where I already work — with history that survives restarts, multiple concurrent chats, and the ability to switch between cloud and local models.

## Architecture

```
User ↔ Slack (Socket Mode) ↔ Python App (Bolt) ↔ LLM Backend (OpenAI compat)
                                    ↓
                               SQLite (persistent)
```

The bot uses Socket Mode — a WebSocket connection instead of a public HTTP endpoint. No reverse proxy, no firewall rules, no port forwarding. It works behind any network.

Each chat is a private channel. Only you and the bot can see it. No AI conversations exposed to the workspace.

## The thread-to-channel pivot

I started with threads in a single `#llm-chats` channel. `/new` creates a thread, users reply in threads to continue. Simple.

Then I discovered Slack blocks slash commands in threads. Users couldn't use `/model`, `/delete`, or `/provider` inside their chats. The entire UX broke.

The fix was a complete architectural shift: `/new` now creates a private channel. Each channel IS the chat. Slash commands work, each conversation is visually separate, and the bot invites itself automatically. More channels in the workspace, but the tradeoff was worth it.

## How it works

Thirteen slash commands control the bot:

| Command | What it does |
|---------|-------------|
| `/new [name]` | Create a private channel for a new chat |
| `/chats` | List your recent chats |
| `/delete` | Archive the current chat |
| `/provider` | Show or switch LLM provider |
| `/provider models` | List available models |
| `/model` | Switch models within the current provider |
| `/clear` | Wipe conversation history |
| `/title <name>` | Rename the chat |

Every chat stores its own provider and model in the database. You can use OpenCode Zen for one conversation and a local Qwen model for another. Switch mid-conversation with `/provider local`.

When you send a message, the bot shows a typing indicator, streams the response token-by-token using Slack's native `say_stream()` API, and saves the full exchange to SQLite. The first message auto-generates a title — the bot asks the LLM to name the conversation in under 5 words, then updates the channel topic.

Channel names are slugified from your input (`/new my project` → `llm-my-project`). Duplicates get a 6-character hash suffix to prevent collisions.

## Docker integration

The bot runs alongside my existing [LLM Docker stack](/blog/ai-docker-stack.html). It connects to the LiteLLM proxy at `workstation1:8000/v1` — the same endpoint that powers Open WebUI and aider.

```yaml
# docker-compose.yml
services:
  slack-llm-bot:
    build: .
    volumes:
      - ./data:/app/data
    env_file: .env
    restart: unless-stopped
```

The `.env` file points to both providers:

```bash
# Cloud — OpenCode Zen
LLM_OPENCODE_API_BASE=https://opencode.ai/zen/go/v1
LLM_OPENCODE_API_KEY=...

# Local — LiteLLM from the Docker stack
LLM_OPENAI_API_BASE=http://workstation1:8000/v1
LLM_OPENAI_API_KEY=
```

Socket Mode means the bot needs no inbound HTTP connection. It connects outbound to Slack's WebSocket gateway, so it runs on any machine behind any firewall. The SQLite database lives in a mounted volume (`./data/chat.db`) with WAL mode for safe concurrent access.

## Testing

Two-tier approach with pytest markers:

```bash
make test-fast     # 32 tests, ~0.5s — no LLM calls
make test-llm      # 14 tests, ~37s — real LLM endpoints
make test          # All 46 tests
```

The fast tests cover utilities, database operations, and provider configuration. The LLM tests hit real endpoints — OpenCode Zen or the local model — to validate message handling, model fetching, and provider switching. Both tiers have value: fast tests catch regressions instantly, slow tests confirm the integration actually works.

## What I Learned

- **Platform limitations drive architecture** — Slack's thread limitation forced a complete redesign. Always verify platform constraints early. What seems like a minor UI detail (threads vs channels) can force a total architectural change.

- **Socket Mode eliminates infrastructure** — No public endpoint, no reverse proxy, no firewall configuration. The bot connects outbound via WebSocket and works from anywhere. This is the right choice for personal tools.

- **SQLite with WAL mode works fine in Docker** — With a mounted volume and proper pragmas (`PRAGMA journal_mode=WAL`, `PRAGMA busy_timeout=5000`), SQLite handles concurrent access without issues. Don't reach for PostgreSQL unless you actually need it.

- **Per-chat provider switching is worth the complexity** — Each chat storing its own provider and model feels natural. Using different models for different tasks — cloud for quick questions, local for sensitive code — is the default workflow.

- **Slack's `say_stream()` is purpose-built for AI** — Don't simulate streaming with `chat.update` loops. Accumulate tokens in a buffer, flush every ~50 characters, and let Slack handle the rendering. The native API does exactly what you need.

- **Two-tier testing catches different things** — Mocked fast tests verify logic. Real LLM tests verify the integration actually works. The 37-second penalty for LLM tests is worth the confidence.
