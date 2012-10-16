doc:
	make -C doc html

upload:
	python setup.py register sdist upload
