"""
Run benchmarks on the current work tree using `timeit`.

Note that this script does not use vbench.

"""

import timeit

import benchcode


def do_timeit(code, setup, name, number):
    print(name)
    sec = timeit.timeit(code, setup, number=number) / number
    print("{0:.3f} sec".format(sec))


def run_timeit(number):
    for data in benchcode.data:
        do_timeit(number=number, **data)


def main(args=None):
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--number", type=int, default=10)
    ns = parser.parse_args(args)
    run_timeit(**vars(ns))


if __name__ == "__main__":
    main()
