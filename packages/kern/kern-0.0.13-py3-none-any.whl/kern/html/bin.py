#!/usr/bin/env python3

__all__ = ['main']

import sys

def main(argv=None):

    import argparse
    from kern.html import is_url
    from kern.html import url_to_html
    from kern.html import html_to_text

    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser('html')
    parser.add_argument('path', nargs='?')
    args = parser.parse_args(argv)

    if args.path is not None:
        text = open(args.path, 'r').read()
    else:
        text = sys.stdin.buffer.read().decode()

    if is_url(text):
        html = url_to_html(text)
    else:
        html = text

    text = html_to_text(html)
    print(text)

if __name__ == '__main__':
    main()
