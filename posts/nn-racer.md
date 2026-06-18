title: NN Racer — Teaching a Neural Network to Drive with Evolution
description: A 2D car racing simulation where a neural-network-controlled AI learns to navigate tracks using a genetic algorithm. No ML frameworks, no pre-trained models.
date: 2026-06-12
---

A 2D car racing simulation where a neural-network-controlled AI learns to drive using a genetic algorithm. Built from scratch in Python with Pygame and NumPy. No ML frameworks, no pre-trained models — just a feedforward network, ray sensors, and evolution.

<a href="https://github.com/ryonsherman/nn-racer"><img src="/img/nn-racer.png" width="768" alt="NN Racer with evolved cars driving on a generated track"></a>

## The core loop

A car with 5 distance sensors drives around a procedurally-generated track. A neural network — 6 inputs (5 sensor distances + speed), 8 hidden neurons with tanh activation, 2 outputs (steering and acceleration) — controls the car. A genetic algorithm evolves a population of 60 brains over generations, with fitness based on angular progress around the track. The best brains are saved and can be replayed as colored overlay trails.

## Ray sensors

Five sensors at -90°, -45°, 0°, +45°, +90° relative to the car's heading march outward in 3-pixel steps up to 200px range, checking if each point is on the track. Sensor readings are normalized to 0-1 and fed to the neural network. A coarse spatial grid makes these lookups O(1) instead of iterating through thousands of centerline points.

## Car physics

Position/velocity/heading with forward acceleration and braking (no reversing). Speed-dependent steering — less effective at high speed. Lateral grip prevents sliding. Drag tuned so equilibrium equals top speed. The car is 23×9 pixels (~4.5m × 1.8m).

## Genetic algorithm

Standard tournament-selection GA with a population of 50-60. Top 2 brains are kept as elites (unchanged). Tournament size 3 for parent selection. Weight-averaging crossover with random blending factor 0.3-0.7. Gaussian mutation with configurable standard deviation. Multiprocessing evaluation across all CPU cores using the dummy SDL video driver for headless rendering.

## Procedural track generation

Tracks use Gustavo Maciel's algorithm: random points → convex hull (Andrew's Monotone Chain) → add displaced midpoints on each edge → enforce minimum 100° angle between adjacent control points → interpolate with centripetal Catmull-Rom splines (alpha=0.5) → reject tracks with self-intersecting boundaries.

The fundamental insight: offsetting a centerline to create boundary polygons always risks self-intersection on tight curves. The fix is to stop using polygon boundaries for collision and instead use point-to-centerline distance. This is guaranteed correct for any centerline shape.

## The GA convergence problem

The GA kept plateauing at 2-3 checkpoints. Weight-averaging crossover converges toward mediocrity by blending all individuals toward the mean. Combined with a flat fitness landscape (no gradient until the first checkpoint was crossed), the GA was stuck.

The fix was replacing checkpoint line-crossing with angular progress tracking around the track centroid. Every pixel of forward movement increases fitness. This smooth, continuous signal was the key breakthrough that made learning possible.

## Brain transfer learning

Brains trained on one track transfer surprisingly well to others. An oval-trained brain can navigate raceway, hairpin, and technical tracks after just a few generations of fine-tuning. This enabled chain training: train on oval → seed next track → fine-tune → save champion → repeat through all 30 curated seeds. Every single seed reached 1+ laps, most within 1-5 generations.

The final experiment: train on randomly generated tracks, chaining the champion forward and discarding tracks that can't be solved within 20 generations. Over 400 random tracks, the brain learned a remarkably general driving policy — it could navigate almost any valid track the generator produced, often completing 5-8 laps in the allotted 5000 steps.

## 74 parameters

The entire network has only 74 parameters (6×8 + 8 + 8×2 + 2 = 74). That's fewer weights than a single linear layer in a modern neural network. Yet with a well-designed fitness function and enough generations, this tiny network learns to drive complex tracks at speed, handle tight hairpins, and generalize to tracks it's never seen before.

The source is on GitHub at [ryonsherman/nn-racer](https://github.com/ryonsherman/nn-racer).

## What I Learned

- **Fitness function design is everything** — A flat fitness landscape kills GAs. Angular progress (continuous, smooth) vs. checkpoint crossing (binary, sparse) was the difference between stalling at 2 checkpoints and completing 8 laps.
- **Weight-averaging crossover converges to mediocrity** — It works for simple problems but tends toward the mean. Uniform crossover or approaches like NEAT or CMA-ES would maintain more diversity.
- **Distance-based collision is more robust than polygon offset** — Offset boundary polygons self-intersect on tight curves. Point-to-centerline distance is simpler and always correct.
- **Centripetal Catmull-Rom prevents cusps** — The centripetal parameterization (alpha=0.5) prevents self-intersections where uniform Catmull-Rom fails, making it ideal for generating track centerlines.
- **Brain transfer is surprisingly powerful** — A general driving policy emerges from training on diverse tracks. Fine-tuning to a new track takes 1-5 generations vs. 20-50 from scratch.
- **74 parameters is enough** — A tiny feedforward network with fewer weights than a single modern linear layer can learn complex driving behavior given the right training signal and enough iterations.
