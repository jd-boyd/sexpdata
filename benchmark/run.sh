#!/bin/sh

cd $(dirname $0)/..
vbench_dir=$(pwd)/lib/vbench
export PYTHONPATH=$PYTHONPATH:$vbench_dir

python benchmark/run_benchmark.py
