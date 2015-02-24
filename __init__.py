#!/usr/bin/env python2
from noise import Noise

app = Noise(__file__)

@app.route('/')
def index(page):
    # set template variables
    page.data.update({
        'title': "noise: a static website generator",
        'body':  "Hello World!"
    })

