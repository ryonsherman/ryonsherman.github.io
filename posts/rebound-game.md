title: Rebound — A 4-Player Multiplayer Cannon Game
date: 2026-06-12
---

I built a 4-player castle battle game with bouncing projectiles, power-ups, and online multiplayer.

![Rebound menu](https://github.com/ryonsherman/pygame-rebound/raw/main/screenshots/menu.png)

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

The source is on GitHub at [ryonsherman/pygame-rebound](https://github.com/ryonsherman/pygame-rebound/).
