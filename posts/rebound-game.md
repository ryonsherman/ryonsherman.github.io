title: Rebound — A 4-Player Multiplayer Cannon Game
description: A 4-player castle battle game with bouncing projectiles, power-ups, AI, and online multiplayer.
date: 2026-06-12
---

I built a 4-player castle battle game with bouncing projectiles, power-ups, and online multiplayer.

<img src="https://github.com/ryonsherman/pygame-rebound/raw/main/screenshots/menu.png" width="768" alt="Rebound menu">

## The game

Rebound is a real-time arena game where four castles occupy the corners of the arena, each with a rotating cannon that fires ricocheting projectiles. The goal is to destroy every brick in your opponents' castles.

The mechanics are simple to pick up:

- **Mouse** to aim your cannon
- **Click** to fire — projectiles bounce off walls, obstacles, and each other
- **Space** to activate a shield that deflects incoming shots
- Collect **power-ups** that spawn periodically for offensive and defensive abilities

As players are eliminated, the center obstacle spins faster, dynamic obstacles fill the dead zones, and the surviving players get faster projectiles with more bounces. The game escalates until one player remains.

## Technical stack

Built from scratch in Python with **Pygame** for rendering and **NATS** for multiplayer. No game engine — the physics, collision detection, AI pathfinding, and networking are all custom.

The AI uses ray casting to find bounce points off walls and obstacles, with three difficulty settings that tune fire rate, projectile speed, shield timing, and power-up spawn frequency.

Multiplayer uses a server-authoritative architecture: the server runs the physics, clients send only raw inputs. NATS handles message routing with automatic matchmaking.

## Power-ups

There are 12 power-ups in three categories — offensive abilities like piercing and spread shot, defensive abilities like shield pulse and healing shield, and instant pickups like repair kits and cannon boost. Each change adds a layer of tactical depth to the chaos of bouncing projectiles.

## What I Learned

- **Richochet physics is simple arithmetic** — Projectile bouncing off walls is just negating the velocity component. Bouncing off other projectiles requires some vector math. But the core physics fits in about 50 lines of Python.
- **Server-authoritative multiplayer is the right call** — Clients send raw inputs, the server runs the physics. This prevents aimbots, wallhacks, and speed hacks without any client-side trust. NATS handles the routing cleanly.
- **AI via ray casting** — The AI fires virtual rays off walls to find valid bounce paths to targets. It's simple, deterministic, and produces surprisingly human-looking play. Three difficulty levels tune fire rate and accuracy.
- **Power-ups add depth without complexity** — Each power-up is just a timed modifier to an existing game stat. Spread shot sets projectile count to 3. Speed boost multiplies velocity. The core systems don't change; the modifiers just stack.
- **Pygame is enough** — No Unity, no Unreal, no Godot. Pygame with software rendering runs a 4-player game with physics, particles, and AI at 60 FPS. Sometimes the simple tools are all you need.
