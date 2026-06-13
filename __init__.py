#!/usr/bin/env python3
from noise import Noise

app = Noise(__file__)

import markdown

from util import ascii_filter, load_posts
app.template.env.filters['ascii'] = ascii_filter

posts = load_posts(app.path('posts'))

@app.route('/')
def index(page):
    page.data.update({
        'title': "secretco.de.com",
        'body': "Hello World",
        'recent_posts': posts[:25],
    })

@app.route('/blog')
def blog_index(page):
    page.template = str(page.app.path.template('blog.html'))
    page.data.update({
        'title': "Blog - secretco.de.com",
        'recent_posts': posts[:25],
        **pagination(1),
    })

@app.route('/blog/feed.atom')
def blog_feed(page):
    md = markdown.Markdown(extensions=['extra'])
    for p in posts:
        p['html'] = md.convert(p['body'])
        md.reset()
    page.template = str(page.app.path.template('atom.xml'))
    page.data.update({
        'posts': posts,
        'updated': posts[0]['date'] + 'T00:00:00Z' if posts else '',
    })

PER_PAGE = 10
total_pages = max(1, (len(posts) + PER_PAGE - 1) // PER_PAGE)

def pagination(page_num):
    start = (page_num - 1) * PER_PAGE
    end = start + PER_PAGE
    return {
        'posts': posts[start:end],
        'page': page_num,
        'total_pages': total_pages,
        'prev_page': page_num - 1 if page_num > 1 else None,
        'next_page': page_num + 1 if page_num < total_pages else None,
    }

for page_num in range(2, total_pages + 1):
    def make_paginated_handler(n):
        def handler(page):
            page.template = str(page.app.path.template('blog.html'))
            page.data.update({
                'title': f'Blog (Page {n}) - secretco.de.com',
                'recent_posts': posts[:25],
                **pagination(n),
            })
        return handler
    app.routes[f'/blog/index/{page_num}.html'] = make_paginated_handler(page_num)

for post in posts:
    def make_handler(p):
        def handler(page):
            page.template = str(page.app.path.template('post.html'))
            page.data.update({
                'title': p['title'] + ' - secretco.de.com',
                'post': p,
                'recent_posts': posts[:25],
            })
        return handler
    app.routes['/blog/' + post['slug'] + '.html'] = make_handler(post)
