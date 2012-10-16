sexpdata.py: README.rst
	cog.py -r $@

doc: sexpdata.py
	make -C doc html

upload: sexpdata.py
	python setup.py register sdist upload
