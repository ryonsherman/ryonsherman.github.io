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

The source is at [ryonsherman/noise](https://github.com/ryonsherman/noise).
