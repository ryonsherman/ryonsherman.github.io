#!/usr/bin/env python2
from noise import Noise

app = Noise(__name__)

from util import ascii_filter
app.template.env.filters['ascii'] = ascii_filter

@app.route('/')
def index(page):
    # set some template variables
    page.data.update({
        'title': "Noise: Make Some!",
        'body':  "Hello World"
    })
