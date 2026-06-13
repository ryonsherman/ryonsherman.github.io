title: Modernizing Noise
date: 2026-06-11
---

I recently updated my old static site generator, Noise, from Python 2 to Python 3.

Key changes:
- Ported to Python 3.8+
- Replaced insecure import with `importlib.util`
- Added proper test suite
- Modern packaging with `pyproject.toml`
