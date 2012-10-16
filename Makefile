sexpdata.py: README.rst
	cog.py -r $@

test: sexpdata.py
	tox

doc: sexpdata.py
	make -C doc html

upload: sexpdata.py
	python setup.py register sdist upload
