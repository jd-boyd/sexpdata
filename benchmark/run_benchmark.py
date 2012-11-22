"""
Run benchmarks using vbench.

Use plot_benchmark.py to view benchmark result.

"""

import os
from datetime import datetime

from vbench.api import Benchmark, BenchmarkRunner

import benchcode


START_DATE = datetime(2012, 10, 16)

benchmarks = [
    Benchmark(start_date=START_DATE, **kwds) for kwds in benchcode.data]

bench_path = os.path.dirname(os.path.abspath(__file__))
REPO_PATH = os.path.dirname(bench_path)
REPO_URL = 'git@github.com:tkf/sexpdata.git'
DB_PATH = os.path.join(bench_path, 'benchmarks.db')
TMP_DIR = os.path.join(REPO_PATH, 'tmp', 'vb')
PREPARE = ''

BUILD = ''


def main(args=None):
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        '--run-option', default='eod',
        help="one of {'eod', 'all', 'last', integer}")
    ns = parser.parse_args(args)

    run_option = ns.run_option
    if run_option.isdigit():
        run_option = int(run_option)

    runner = BenchmarkRunner(benchmarks, REPO_PATH, REPO_URL,
                             BUILD, DB_PATH, TMP_DIR, PREPARE,
                             run_option=run_option, start_date=START_DATE)
    runner.run()
    return runner


if __name__ == '__main__':
    runner = main()
