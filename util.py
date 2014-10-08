#!/usr/bin/env python2

def ascii_filter(char):
    return ''.join(map(lambda x: '&#{};'.format(ord(x)), char))
