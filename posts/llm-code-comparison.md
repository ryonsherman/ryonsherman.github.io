title: LLM Code Comparison — Pitting 3 Coding Models Against the Same Spec
description: We gave MiMo-V2.5, DeepSeek V4 Flash, and Big Pickle the same project spec and compared what they built across automated metrics, Playwright testing, and human visual ranking.
date: 2026-07-02
---

I gave three different coding LLMs the exact same project specification and compared what they built. Two rounds, two project types, three models, six projects. The goal wasn't to test whether they can reverse a linked list — it was to find out which one builds better software.

## The setup

Each model received the same spec verbatim in a fresh session. Build a single `index.html` with vanilla HTML/CSS/JS, zero external dependencies, must work from `file://`. After building, each model acted as its own code reviewer for 2-3 iterative self-review cycles. Then I evaluated everything across automated metrics, Playwright browser testing, and human visual ranking.

Two rounds, each with its own spec:

- **Round 1:** Sorting Algorithm Visualizer — animate sorting algorithms as colored bars with controls and stats
- **Round 2:** System Monitor Dashboard — simulated real-time system metrics with gauge, bar, sparkline, and numeric panels

Scoring was weighted: Correctness (3x), Feature Breadth (2x), Code Quality (2x), UI Polish (1x).

## The models

| Model | Config | R1 Algorithms | R2 Cycles |
|-------|--------|---------------|-----------|
| MiMo-V2.5 | `opencode-go/mimo-v2.5` | 4 | 2 |
| DeepSeek V4 Flash | `opencode-go/deepseek-v4-flash` | 5 | 3 |
| Big Pickle | `opencode/big-pickle` | 6 | 3 |

## Round 1: Sorting Algorithm Visualizer

The spec called for at least 4 sorting algorithms (Bubble, Selection, Merge, Quick), an array of adjustable-size bars, and controls for sorting, speed, and stats.

Every model delivered something that worked. The differences were in the details.

**Big Pickle** shipped 6 algorithms including Heap Sort — a bonus beyond the spec. A "Status" line showed Idle → Sorting... → Complete/Stopped with real-time feedback. Turbomode instantly completed the sort while still counting operations. The Stop button disabled at rest and enabled during sort — a clean UX pattern. Its CSS was remarkably compact at 63 lines. The only blemish: sorting a single-element array showed "Stopped" instead of "Complete."

**DeepSeek V4 Flash** was the only model to use an IIFE module pattern for scope isolation. It had the cleanest visual design of the three despite fewer UI features — no Stop button, no live time counter. An "Instant" button bypassed animation but showed 0 comparisons and 0 writes, effectively bypassing its own instrumentation. Its CSS was 121 lines.

**MiMo-V2.5** had the most features — order presets (Random, Nearly Sorted, Reversed), manual array entry with a toggle, a size slider with live numeric readout. The Stop button existed but was CSS-hidden at rest (`display: none`), appearing only during a sort. It also had the most code: 222 lines of CSS, 708 lines total. The visual design was functional but busier.

| Metric | MiMo | DeepSeek | Big Pickle |
|--------|------|----------|------------|
| Algorithms | 4 | 5 | 6 |
| CSS lines | 222 | 121 | 63 |
| JS errors | 0 | 0 | 0 |

Scores: Big Pickle 36, DeepSeek 35, MiMo 32.

## Round 2: System Monitor Dashboard

The spec called for a dashboard with CPU, Memory, Disk, and Network panels — each with a different visual style (gauge, bar, sparkline, numeric) — plus pause/resume, speed control, a spike button, and data export.

**DeepSeek** took Round 2 decisively. Zero JS errors. The most compact CSS at 116 lines. Export functionality that downloaded a clean CSV. A status indicator showing "Paused" vs "Live." Speed and history window dropdowns instead of sliders. A last-update timestamp. Clean function separation throughout.

**Big Pickle** used SVG for the CPU gauge instead of a canvas arc — a different technical approach that worked. Toast notifications appeared on spike events. But it was missing Export entirely and had no visible clock or timestamp. Pause may not have fully frozen the simulation data.

**MiMo** had the most UI chrome — a live clock, gauge plus trend chart in every panel, a footer, speed slider (0.5x to 4x), and export. But it also had 13 recurring JS errors: `addColorStop('var(--green)')`. CSS custom properties don't resolve in the Canvas API — they pass through as literal strings. The canvas gradients were silently broken. The bug was documented in MiMo's own self-review as "Low risk" and shipped anyway.

| Metric | MiMo | DeepSeek | Big Pickle |
|--------|------|----------|------------|
| File size | 26,146 B | 25,981 B | 23,848 B |
| CSS lines | 403 | 116 | 283 |
| JS errors | 13 | 0 | 0 |

Scores: DeepSeek 37, Big Pickle 31, MiMo 27.

## The self-review paradox

One of the most interesting findings: models acting as their own code reviewers.

| Model | Cycles | Issues Found | Shipped Bugs |
|-------|--------|-------------|-------------|
| DeepSeek | 3 | 52 | 0 |
| Big Pickle | 3 | 12 | 0 (minor edge case) |
| MiMo | 2 | 10 | 1 |

DeepSeek's 3 review cycles caught and fixed everything, including edge cases in spike simulation and canvas DPR scaling. Big Pickle's review caught the CSS-var-in-Canvas bug before it shipped. MiMo's review documented the same bug and labelled it "low risk."

Review thoroughness correlated strongly with final quality. More cycles meant fewer bugs. But the real insight: acceptance criteria matter more than cycle count. If the model decides a bug is acceptable, it ships — even when the model itself found and documented the bug.

## The CSS-vars-in-Canvas trap

Both MiMo and Big Pickle independently tried using CSS custom properties in Canvas API calls. CSS variables like `var(--green)` are incredibly useful, and it's intuitive to try using them everywhere. But Canvas 2D context doesn't resolve CSS custom properties — they pass as literal strings. The gradient code compiled without errors and produced no output.

Only Big Pickle caught it in review. Two out of three models made the same mistake, which suggests this isn't random — it's a systematic blind spot in how these models reason about web platform APIs.

## Final rankings

| Rank | Model | R1 Score | R2 Score | Combined |
|------|-------|----------|----------|----------|
| 1 | DeepSeek V4 Flash | 35 | 37 | **72** |
| 2 | Big Pickle | 36 | 31 | **67** |
| 3 | MiMo-V2.5 | 32 | 27 | **59** |

**DeepSeek V4 Flash** was the most consistent performer across both rounds — zero JS errors in either project, the best architecture discipline (IIFE module pattern), and the most compact CSS. Not the most feature-rich in either round, but everything it shipped worked perfectly. The minimalist approach paid off.

**Big Pickle** was the feature leader in Round 1 (6 algorithms including bonus Heap Sort) but fell behind in Round 2 by omitting Export and a clock. Its self-review caught the CSS-var-in-Canvas bug before it shipped. Edge cases were the weak spot — sorting a single-element array showed "Stopped" instead of "Complete."

**MiMo-V2.5** had the most UI chrome and the most ambitious feature set in both rounds. Order presets, manual array entry, live clock, export, speed control — it shipped everything. But preventable bugs (CSS vars in Canvas) and code bloat (312 average CSS lines) held it back. Its own review documented the Canvas bug as "low risk" and shipped it anyway.

## What I Learned

- **Architecture discipline is the clearest signal of code quality** — The only model that used an IIFE module pattern (DeepSeek) was also the cleanest overall. Scope isolation correlated perfectly with every other quality metric.

- **AI self-review is only as good as its acceptance criteria** — MiMo's review documented the CSS-var-in-Canvas bug as "low risk" and shipped it. A known, documented bug in production code. The model decided it was acceptable, not that it missed it.

- **Canvas and CSS are separate rendering systems** — Two of three models independently tried using CSS custom properties in Canvas API calls. The platforms look similar but aren't. This is a systematic blind spot, not random chance.

- **Feature breadth has a real cost** — The model with the most features (MiMo) also had the only shipped bugs. The model with the fewest features (DeepSeek) had zero errors across both rounds. More code means more surface area for bugs.

- **More CSS didn't mean better-looking UI** — DeepSeek's 118 average CSS lines outranked MiMo's 312 visually. Clean layout and good spacing beat decoration and chrome every time.

- **Review cycles matter more than model architecture** — DeepSeek's 3 cycles caught every edge case. MiMo's 2 cycles let a visible bug through. The process of reviewing and correcting is as important as the model's ability to generate code in the first place.

- **Benchmarks don't measure what matters** — Every model could implement Quick Sort. None of them would fail an isolated algorithm test. But real-world software engineering is about edge cases, cross-feature interaction, code organization, and knowing when to use — and when not to use — CSS custom properties in Canvas API calls.
