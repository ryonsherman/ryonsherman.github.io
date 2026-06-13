#!/usr/bin/env python3
from noise import Noise

app = Noise(__file__)

from util import ascii_filter, load_posts
app.template.env.filters['ascii'] = ascii_filter

posts = load_posts(app.path('posts'))

@app.route('/')
def index(page):
    page.data.update({
        'title': "secretco.de.com",
        'body': "Hello World",
        'recent_posts': posts[:5],
    })

@app.route('/blog')
def blog_index(page):
    page.data.update({
        'title': "Blog - secretco.de.com",
        'posts': posts,
        'recent_posts': posts[:5],
    })

for post in posts:
    def make_handler(p):
        def handler(page):
            page.template = str(page.app.path.template('post.html'))
            page.data.update({
                'title': p['title'] + ' - secretco.de.com',
                'post': p,
                'recent_posts': posts[:5],
            })
        return handler
    app.routes['/blog/' + post['slug'] + '.html'] = make_handler(post)
