title: FogMUD — Building a Modern Telnet MUD From Scratch
description: A text-based multiplayer world built from the ground up in Python. No engines, no libraries, just raw TCP sockets and a lot of JSON.
date: 2026-06-12
---

FogMUD is a Multi-User Dungeon (MUD) — a text-based multiplayer roleplaying game — built entirely from scratch in Python using asyncio. No MUD libraries, no game engines. Just raw TCP sockets, telnet protocol negotiation, and a lot of JSON.

Players connect via telnet, choose from three factions, 18 races, and 4 classes, and explore the frontier town of Drel — a world layered between reality and a mysterious force called the Veil. Over 10,000 lines of Python across ~50 source files, zero runtime dependencies beyond the standard library.

## Origin

The project started as a Python 2 MUD in 2014, using asyncore (the long-deprecated async library). That codebase sat in a Git repository for nearly a decade. In 2025, it was resurrected with a complete rewrite to Python 3.10+ asyncio — preserving the JSON-first architecture and telnet protocol handling while completely rebuilding combat, classes, factions, NPCs, and the world itself.

This rewrite is still ongoing. The project is very much a work in progress, and probably always will be — that's the nature of building a living world.

## How It Works

**Telnet protocol** — Raw RFC 854 telnet with IAC negotiation for echo control. Character-by-character input. Packet-level debugging to get it right. Modern telnet clients are forgiving, but the protocol is from 1983 and it shows.

**asyncio** — Single-process, event-driven concurrency. No threads, no GIL issues, no database. Player sessions are asyncio tasks, the game heartbeat runs on a loop, and everything is non-blocking.

**JSON on disk** — Every piece of game data lives in JSON files. Easy to debug (just open the file), but concurrent access requires asyncio.Lock per file plus atomic writes (write to temp, then rename). The DataManager creates timestamped backups before every save, rotating the last 10.

## Key Systems

**Combat** — Stat-based with multi-defender support. Players can fight multiple NPCs simultaneously. Three NPC aggression tiers: passive, aggressive (attacks on sight with a Charisma saving throw), and protective (defends specific mobs). NPCs that lose their target will *hunt the player through rooms* — tracking their path every heartbeat tick until they catch up.

**The pursuit system** — When combat breaks due to a player leaving the room, each engaged NPC becomes a "hunter" that tracks the player's path. Every 2-second heartbeat, each hunter advances one room. When they catch up, combat resumes with a dramatic "bursts into the room" message. There's even a `hunters` command to see what's chasing you.

**Factions & races** — Three factions (Iron Accord, Verdant Circle, Aether Pact) each with 6 unique races drawn from classic fantasy. Races have stat modifiers that complement different playstyles.

**Class halls** — You don't pick your class at character creation. You start as a blank slate and must find the appropriate class hall in the world — then type `become fighter`. Subclasses unlock at level 20, requiring a return visit. This makes class choice feel meaningful instead of transactional.

**Progression** — A shared XP pool fuels both leveling and stat improvement. A stat gate prevents cheese: `sum(all_stats) >= 60 + level * 2` before you can advance. You can't outrun your stats.

**Trigger engine** — Room triggers execute Python logic from JSON data, but through AST validation — only safe operations (comparisons, attribute access, boolean logic) are allowed. Unsafe code is rejected before execution.

**Game time** — A full calendar with seasons, time of day, and weather that's local to regions and affects gameplay. Seasonal recovery modifiers, dawn through midnight, spring through winter.

## What's Still to Come

This is the part I'm most excited about. The foundations are solid, but the world is still being built:

- Skill system — 15 skills, 3 per class, with subclass-specific training formulas
- Party system with XP sharing and level range limits
- Quest system driven by the trigger engine
- Subclass abilities — the actual unique powers per archetype
- Porting 58+ rooms from the original codebase into Drel
- More NPC types, items, equipment, and crafting
- Building out Drel itself — the frontier town where players arrive, with NPCs that have schedules, shops that stock inventory, and secrets waiting to be found

## A Living Project

FogMUD has been in development on and off since 2014. It sat dormant for years, then came back to life as a complete rewrite. It'll probably go through another rewrite someday — that's how these things go. The beauty of building a MUD from scratch is that there's no finish line. There's always another system to build, another room to describe, another bug to fix. The world grows as you do.

For now, it's telnet, it's Python, it's JSON files, and it's very much a work in progress. And I wouldn't have it any other way.
