#!/usr/bin/env python

"""
Convert S-expressions in files to JSONs.
"""

import sys
import json
import sexpdata


def tojsonable(obj):
    if hasattr(obj, "value") and callable(getattr(obj, "value")):
        return tojsonable(obj.value())
    if isinstance(obj, list):
        return list(map(tojsonable, obj))
    return obj


def sexp2json(file, out, recursionlimit):
    sys.setrecursionlimit(recursionlimit)
    for path in file:
        with open(path) as f:
            json.dump(tojsonable(sexpdata.parse(f.read())), out, indent=2)


def main(args=None):
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=__doc__
    )
    parser.add_argument("file", nargs="*")
    parser.add_argument(
        "--out",
        "-o",
        type=argparse.FileType("wt"),
        default="-",
        help="Output file.",
    )
    parser.add_argument(
        "--recursionlimit",
        "-l",
        type=int,
        default=sys.getrecursionlimit(),
        help="Set Python recursion limit.",
    )
    ns = parser.parse_args(args)
    sexp2json(**vars(ns))


if __name__ == "__main__":
    main()
