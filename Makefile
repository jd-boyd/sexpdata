.PHONY: test doc upload benchmark plot-benchmark clean-benchmark

vbench_dir = ${PWD}/lib/vbench
PYTHONPATH := ${PYTHONPATH}:${vbench_dir}

sexpdata.py: README.rst
	cog.py -r $@

test: sexpdata.py
	tox

doc: sexpdata.py
	make -C doc html

upload: sexpdata.py
	python setup.py register sdist upload

benchmark:
	python benchmark/run_benchmark.py

plot-benchmark:
	python benchmark/plot_benchmark.py

clean-benchmark:
	rm -rf tmp
	rm benchmark/benchmarks.db
