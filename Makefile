.PHONY: test doc upload benchmark clean-benchmark

sexpdata.py: README.rst
	cog.py -r $@

test: sexpdata.py
	tox

doc: sexpdata.py
	make -C doc html

upload: sexpdata.py
	python setup.py register sdist upload

benchmark:
	benchmark/run.sh

clean-benchmark:
	rm -rf tmp
	rm benchmark/benchmarks.db
