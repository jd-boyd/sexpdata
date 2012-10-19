#!/usr/bin/env python

"""
Convert S-expressions in files to JSONs.
"""

import sexpdata
import json


def tojsonable(obj):
    if isinstance(obj, sexpdata.SExpBase):
        return tojsonable(obj.value())
    if isinstance(obj, list):
        return map(tojsonable, obj)
    return obj


def sexp2json(file, out):
    for path in file:
        with open(path) as f:
            json.dump(tojsonable(sexpdata.parse(f.read())), out, indent=2)


def main(args=None):
    from argparse import ArgumentParser, FileType
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('file', nargs='*')
    parser.add_argument('--out', '-o', type=FileType('wt'), default='-')
    ns = parser.parse_args(args)
    sexp2json(**vars(ns))


if __name__ == '__main__':
    main()
