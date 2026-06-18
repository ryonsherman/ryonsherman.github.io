title: Rebound — Training Neural Network Bots with PPO
description: Replacing hand-coded heuristic AI with PPO-trained neural networks in a castle battle game. Reward shaping, curriculum training, and the bugs that come with running RL in a real game loop.
date: 2026-06-18
---

A follow-up to [Rebound — A 4-Player Multiplayer Cannon Game](/blog/rebound-game.html). The original AI used hand-coded heuristics — pick a target, calculate a bounce angle, fire on a timer, raise shield when threatened. It worked, but it was predictable and capped in skill. I replaced it with PPO-trained neural networks using Stable-Baselines3.

## Observation space

I went with a **112-float vector** over a grid/CNN approach. The game state is already structured data — positions, velocities, health, cooldowns — so encoding it as pixels would add complexity without benefit.

- **Self** (16 floats): health, cannon angle, shield status, powerups, timed effects
- **Enemies** (30): 3 opponents × 10 features each (health, position, shield state)
- **Projectiles** (48): 8 nearest projectiles × 6 features (relative position, velocity, threat level)
- **Powerups** (12): 3 nearest × 4 features
- **Arena** (6): obstacle rotation, wall distances

## Action space

`MultiDiscrete([32, 2, 2])` — 32 aim directions (11.25° each), binary fire, binary shield. That's 128 possible action combinations per step. Small enough for efficient PPO training, granular enough for precise control.

The policy network is a three-layer MLP (256→128→64, ReLU) built by Stable-Baselines3's `MlpPolicy`. No custom PyTorch code — just `policy_kwargs` with `net_arch` and `activation_fn`.

## Reward design

This was the hardest part. The initial reward function produced an agent that plateaued at 70% win rate against Medium AI and never improved.

**What went wrong:** Getting hit is frequent (lots of negative reward), but landing hits is rare (sparse positive reward). The agent learned to avoid damage by doing nothing useful. The fire penalty (-0.01 per shot) seemed minor, but when most shots miss early in training, 100 shots costs -1.0 reward — enough to suppress exploration entirely.

**What fixed it:** A per-step survival bonus of +0.05. Over a full 60-second match, that's +180 reward just for staying alive. This gave the agent a steady positive signal that didn't depend on combat outcomes, letting it learn defensive behaviors (shielding, positioning) without the noise of hit/miss randomness. Once survival was directly rewarded, everything else fell into place.

Final reward weights: damage dealt +0.3 per brick, self damage -0.2, kill +5.0, death -5.0, shield block +2.0, fire penalty -0.001, survival +0.05/step.

## Training pipeline

I wrapped `GameEngine` (the pure-Python game logic, no rendering) as a Gymnasium environment. Each training run is a 1v1 match: the agent versus one heuristic AI, with the other two castles removed.

Four parallel game instances ran via a custom `ThreadedVecEnv` using `ThreadPoolExecutor`. Each instance runs at ~200 steps/second, giving ~800 total steps/second. A 1M-step training run takes about 20 minutes.

### Curriculum

I trained in phases, each loading the previous checkpoint:

1. **vs Easy AI** — 450k steps → 100% win rate
2. **vs Medium AI** — 300k steps → 90-100% win rate
3. **vs Hard AI** — 900k steps → 80-100% win rate

Transfer learning worked well — the Easy-trained model already knew how to aim and fire, so Medium training started at 90% win rate immediately.

## The bugs

### Inference jitter

The trained model flickered in-game — cannon angle changing wildly every frame, shield toggling on and off. The model was trained with `frame_skip=4` (one decision per 4 game frames), but the game loop was running inference at 60fps. Four times more decisions than it was trained for. Fix: match the inference frame skip to training, plus rotation speed limiting and a shield hold timer to smooth outputs.

### Quadrant clamping

The neural network occasionally aimed behind its own castle. Human players and heuristic AI both had mouse-position clamping to prevent this, but the NN controller was setting the angle directly. Fix: clamp the NN's aim point to the player's quadrant using the same function that human players use.

### macOS multiprocessing

Stable-Baselines3's `SubprocVecEnv` uses Python's multiprocessing, which on macOS with Python 3.14 defaults to `forkserver`. This re-imports the main module in child processes, triggering Pygame init and crashing. Fix: replaced `SubprocVecEnv` with a `ThreadedVecEnv` using `ThreadPoolExecutor`. Threads avoid the issue while still providing parallelism for the CPU-bound game engine.

## Results

| Model | Opponent | Win Rate | Steps | Time |
|-------|----------|----------|-------|------|
| Easy | Easy AI | 100% | 450k | ~15 min |
| Medium | Medium AI | 90-100% | 300k | ~10 min |
| Hard | Hard AI | 80-100% | 900k | ~30 min |

The neural AI plays visibly differently from the heuristic AI — it uses the shield proactively instead of reactively, fires more aggressively, survives longer, and adapts to opponent behavior rather than following fixed rules.

The source is on GitHub at [ryonsherman/pygame-rebound](https://github.com/ryonsherman/pygame-rebound).

## What I Learned

- **Survival is the best teacher** — A simple per-step survival bonus outperformed every complex reward shaping attempt. The agent learned to shield and position itself naturally once staying alive was directly rewarded.
- **Match training and inference frequency** — The frame skip mismatch between training (4 frames/decision) and inference (every frame) caused jitter that looked like a bug in the network. Always run inference at the same rate as training.
- **Threads over processes for game RL** — On platforms where multiprocessing is problematic (macOS, Windows), threaded vector environments work surprisingly well for CPU-bound game engines.
- **Curriculum accelerates everything** — Transfer learning from Easy → Medium → Hard meant each stage started with a competent baseline. Medium training began at 90% win rate from the Easy checkpoint.
- **Keep the safety nets** — Even though the NN learned to aim within its quadrant, keeping the clamp as a hard constraint prevented edge cases without affecting performance. Defense in depth applies to RL too.
- **Reward functions are deceptive** — A -0.01 fire penalty seemed trivial but was enough to suppress exploration entirely. Small weights compound over thousands of steps.
