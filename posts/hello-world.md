title: Hello World — Noise, a Minimal Static Site Generator
description: Noise is a minimal static site generator written in Python. This post introduces the project and its features.
date: 2026-06-12
---

This site is built with [Noise](https://github.com/ryonsherman/noise), a minimal static site generator I wrote in Python.

It takes Markdown content and Jinja2 templates and produces flat HTML files. Routes are declared with a decorator, much like Flask:

```python
@app.route('/blog')
def blog_index(page):
    page.data.update({
        'title': "Blog",
        'posts': posts,
    })
```

Noise handles the rest — finding the template, rendering the page, and writing the output file.

I recently modernized it from the original Python 2 to 3.8+. Key changes:

- Replaced insecure `__import__()` with `importlib.util`
- Fixed global Markdown state that leaked between renders
- Added a proper test suite (33 tests)
- Modern packaging with `pyproject.toml`
- Built-in dev server with live reload via SSE

## What I Learned

- **Rewriting is sometimes necessary** — The Python 2 → 3 migration was painful but forced me to understand every line of the codebase. The result is cleaner, safer, and properly tested.
- **`__import__()` is a security hole** — Using string-based module loading for plugin systems is convenient but dangerous. `importlib.util.spec_from_file_location()` is the safe alternative that I should have used from the start.
- **Static site generators are deceptively simple** — The core loop is trivial: routes → templates → files. But the ecosystem (live reload, build optimization, error handling, template inheritance) is where the complexity hides.
- **Submodule workflows are fiddly** — Having the blog output in a git submodule means every deploy is a two-step process: update the submodule, then update the parent. It's worth it for clean separation, but it adds friction.
- **Test suites pay for themselves instantly** — The 33 tests caught regressions during the Python 3 migration that would have taken hours to find manually.
