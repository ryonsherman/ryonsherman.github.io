#!/usr/bin/env python3

import os
import re


def ascii_filter(char):
    return ''.join('&#{};'.format(ord(x)) for x in char)


def slugify(name):
    name = os.path.splitext(name)[0]
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    name = name.strip('-')
    return name


def title_from_filename(filepath):
    name = os.path.splitext(os.path.basename(filepath))[0]
    return name.replace('-', ' ').title()


def parse_post(filepath):
    with open(filepath) as f:
        content = f.read()

    parts = content.split('---', 1)
    if len(parts) == 2:
        header, body = parts
    else:
        header, body = '', parts[0]

    meta = {}
    for line in header.strip().splitlines():
        if ':' in line:
            key, _, val = line.partition(':')
            meta[key.strip()] = val.strip()

    body_text = body.strip()
    desc = meta.get('description', '')
    if not desc:
        first_line = body_text.split('\n\n')[0].strip()
        desc = first_line[:200].rstrip('.') + '.' if len(first_line) > 200 else first_line

    return {
        'title': meta.get('title', title_from_filename(filepath)),
        'date': meta.get('date', ''),
        'body': body_text,
        'description': desc,
        'slug': slugify(meta.get('slug', os.path.basename(filepath))),
    }


def load_posts(posts_dir):
    if not os.path.isdir(posts_dir):
        return []

    posts = []
    for name in sorted(os.listdir(posts_dir)):
        if not name.endswith('.md'):
            continue
        post = parse_post(os.path.join(posts_dir, name))
        post['filename'] = name
        posts.append(post)

    posts.sort(key=lambda p: p['date'], reverse=True)
    return posts
