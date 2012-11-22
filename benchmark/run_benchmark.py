import os
from datetime import datetime

from vbench.api import Benchmark, BenchmarkRunner

START_DATE = datetime(2012, 10, 16)

common_setup = """
import sexpdata
length = 10000
"""
do_loads = 'sexpdata.loads(string)'

benchmarks = [
    Benchmark(
        do_loads,
        common_setup + r"""
string = '"{0}"'.format('x' * length)
""",
        name="Plain long string (plain:quote = 1:0)",
        start_date=START_DATE),
    Benchmark(
        do_loads,
        common_setup + r"""
string = '"{0}"'.format(r'\"' * length)
""",
        name="Long string only with escaped quotes (plain:quote = 0:1)",
        start_date=START_DATE),
    Benchmark(
        do_loads,
        common_setup + r"""
string = '"{0}"'.format(r'1\"' * length)
""",
        name="Long mixed string (plain:quote = 1:1)",
        start_date=START_DATE),
    Benchmark(
        do_loads,
        common_setup + r"""
string = '"{0}"'.format(r'12345\"' * length)
""",
        name="Long mixed string (plain:quote = 5:1)",
        start_date=START_DATE),
]

bench_path = os.path.dirname(os.path.abspath(__file__))
REPO_PATH = os.path.dirname(bench_path)
REPO_URL = 'git@github.com:tkf/sexpdata.git'
DB_PATH = os.path.join(bench_path, 'benchmarks.db')
TMP_DIR = os.path.join(REPO_PATH, 'tmp', 'vb')
PREPARE = ''

BUILD = ''

if __name__ == '__main__':
    runner = BenchmarkRunner(benchmarks, REPO_PATH, REPO_URL,
                             BUILD, DB_PATH, TMP_DIR, PREPARE,
                             run_option='eod', start_date=START_DATE)
    runner.run()
