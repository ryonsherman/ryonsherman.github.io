title: Chernobyl Reactor Simulator — Modeling RBMK Physics in Pygame
description: A real-time Pygame simulation of the Chernobyl RBMK reactor disaster — nuclear fission, neutron moderation, xenon poisoning, and the positive void coefficient that caused it all.
date: 2026-06-18
---

Inspired by [Chernobyl Visually Explained](https://www.youtube.com/watch?v=P3oKNE72EzU), I built a real-time Pygame simulation of the Chernobyl RBMK reactor disaster. It models nuclear fission, neutron moderation, control rod mechanics, water cooling, xenon poisoning, and the positive void coefficient — the design flaw that caused the 1986 disaster.

<img src="/img/chernobyl-sim.png" width="768" alt="Chernobyl Reactor Simulator - RBMK reactor simulation with neutrons flying through the core">

The reactor runs at 60fps with hundreds of neutrons flying around in real time. You can control it manually with arrow keys, let a proportional controller manage it, or train a PPO reinforcement learning agent to hold a target power level.

## What's being modeled

The simulation is built on a 40×21 grid of uranium fuel cells. Each cell can be active (blue), depleted (gray), or poisoned by xenon-135 (black). Water sits behind each fuel cell, heating up as neutrons pass through it.

**Fission** — A thermal neutron (slow, black) hits an active uranium cell. The cell depletes, and 3 fast neutrons (white with black outline) fly out at random angles. That's the chain reaction: one neutron becomes three.

**Neutron moderation** — Fast neutrons can't cause fission. They need to be slowed down by bouncing off graphite moderator rods. When a fast neutron hits graphite, its speed drops to thermal and it changes type. This is the role graphite plays in RBMK reactors.

**Control rods** — 10 movable rods in two interleaved groups (A and B), each independently controlled. Each rod has three sections: a black absorber that kills neutrons on contact, a shaft that removes neutrons that pass through, and a graphite tip that moderates fast neutrons into thermal ones. The visual design — black absorber on top, white graphite below — makes it clear which part does what.

**Water cooling** — Each fuel cell has water behind it. Neutrons passing through heat it up (blue → orange → light red gradient). If water exceeds 200°, it evaporates and disappears. Water cools slowly when not being heated and returns after a random delay.

**Positive void coefficient** — The critical flaw of the RBMK reactor. When water evaporates, the collision radius for fission increases by 1.5×. Less water means more reactivity — a positive feedback loop that can cause runaway power excursions. This is the core educational concept of the simulation. Even a modest boost creates a feedback loop that can overwhelm control systems.

**Xenon poisoning** — After fission, depleted uranium becomes iodine-135, which decays into xenon-135. Xenon absorbs neutrons and stalls the reaction — the "xenon pit" that trapped operators during the disaster. Xenon burns away via neutron absorption but also decays naturally (simplified from the real 9.2-hour half-life).

**Delayed neutrons** — Depleted uranium emits neutrons at 0.01% chance per frame. This simplified model represents the delayed neutron precursors that are critical for reactor control in real life.

## The auto-control challenge

This was the hardest part. The goal: keep the reactor at a target neutron count (default 40 = 50% power) using control of two rod groups.

**Attempt 1: Bang-bang controller** — Simple thresholds. Below target raise rods, above target lower rods. Result: constant oscillation around the target. The rods were always moving at max speed in one direction or the other, never settling.

**Attempt 2: Proportional controller** — Scale rod movement by error magnitude: `adjustment = error × gain`. The gain (0.0002) was chosen so that at ±100 error the rods move at max speed, but near target they make small corrections. Problem: the controller was purely reactive — by the time it saw a large error, the reaction had already escalated.

**Attempt 3: Proportional + deadband** — Added a ±3 neutron deadband where rods don't move. This prevented jitter near target but didn't solve the startup burst problem.

**Attempt 4: Proportional with predictive correction (final)** — Instead of reacting to `current_count - target`, the controller reacts to `(current_count + trend) - target`. If neutrons are at 30 but rising fast (+20/frame), it sees a predicted error of +10 and starts inserting immediately — rather than waiting until neutrons actually overshoot.

This was the key insight: predict the future state based on the current trend, and act preemptively. The rod speed is fixed at 0.003 per frame — at 60fps, full travel takes ~5.5 seconds. But a chain reaction can double in a fraction of a second. The predictive controller compensates for this physical limitation by acting early.

## The xenon burnout problem

Early versions suffered from a fatal flaw: after the initial startup burst, xenon would build up faster than it decayed, permanently poisoning the reactor. The reaction would limp along at 15-25 neutrons with rods fully withdrawn, unable to recover.

Root causes: the startup burst was too severe (30% starting fuel × 840 cells = 252 active cells igniting simultaneously), there was no natural xenon decay (xenon could only burn away via neutron absorption, which was too slow at low neutron counts), and the reactivity boost was too high (2.5× made evaporated water cells 2.5× more reactive).

Fixes: lowered the reactivity boost from 2.5 → 1.5, added natural xenon decay at 0.0008 chance per frame, raised the max water temperature from 100 → 200 (water takes longer to boil, reducing positive void feedback during bursts), and raised starting rod insertion from 0.5 → 0.9 (rods start mostly inserted, giving the controller more headroom).

## Log viewer

A separate Pygame app reads the simulation log and displays 6 real-time line graphs: neutrons (total/fast/thermal), power %, rod insertion (group A and B), fuel/iodine/xenon counts, water temperature/evaporation, and error from target. Pan with arrow keys, zoom with scroll, and `--live` mode re-reads the log file every 0.5 seconds for watching runs in real time.

<img src="/img/chernobyl-viewer.png" width="768" alt="Chernobyl reactor log viewer with real-time line graphs">

## RL training

The reactor can also be controlled by a PPO reinforcement learning agent. The Gymnasium environment wraps the headless physics engine (`reactor.py`) with a 9-float observation vector (neutron count, rod positions, water temp, xenon count, target, error, trend) and continuous actions (±1 for each rod group). Reward is scaled by relative error from target, with +10 for on-target and -100 for reactor death.

Training runs at ~200 steps/second on CPU. The model saves to `ppo_reactor.zip` and can be loaded back into the main simulation via `--auto`.

## What I Learned

- **Predictive control beats reactive control** — Acting on the trend rather than the current state is essential when the system has momentum. The reactor doesn't respond instantly to rod movement, so the controller has to anticipate, not react.
- **Physical constraints shape control strategies** — The fixed rod speed meant the controller had to predict the future. A faster rod would've made reactive control viable, but the constraint forced a better algorithm.
- **Xenon poisoning is a death spiral without natural decay** — Low power → xenon accumulates → even lower power → more xenon. The natural decay rate had to be carefully tuned to match the iodine→xenon production rate. Without it, recovery was impossible.
- **The positive void coefficient is terrifying in practice** — Even a 1.5× boost creates a feedback loop that can overwhelm control systems. The real RBMK had this same flaw, and watching it in simulation makes the disaster feel visceral.
- **Tuning is iterative** — The final parameter set (gain, deadband, decay rates, boost factor) was the result of ~15 iterations, each informed by log analysis. The `--log` flag and viewer were essential for diagnosing problems.
- **NumPy vectorization makes real-time particle physics feasible in Python** — Hundreds of neutrons processed per frame at 60fps, with vectorized distance checks between all neutrons and all active fuel cells simultaneously.
- **Separate physics from rendering** — The shared `reactor.py` engine works headless for both the simulation and RL training, but the constants need to stay in sync between files. That divergence is a known issue.
