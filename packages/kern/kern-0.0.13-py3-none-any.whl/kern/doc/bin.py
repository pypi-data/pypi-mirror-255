#!/usr/bin/env python

__all__ = ['main']

import sys

def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]

    import argparse
    parser = argparse.ArgumentParser('doc')
    parser.add_argument('path', nargs='?')
    args = parser.parse_args(argv)

    if args.path is not None:
        bytes = open(args.path, 'rb').read()
    else:
        bytes = sys.stdin.buffer.read()

    from kern.doc import doc_to_text
    text = doc_to_text(bytes)
    print(text)

if __name__ == '__main__':
    main(sys.argv[1:])
