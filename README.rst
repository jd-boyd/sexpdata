S-expression parser for Python
==============================

>>> from sexpdata import loads, dumps
>>> loads("(a b)")
[Symbol('a'), Symbol('b')]
>>> print(dumps(['a', 'b']))
(a b)

Links:

* `Documentaions (at Read the Docs) <http://sexpdata.readthedocs.org/>`_
* `Repository (at GitHub) <https://github.com/tkf/sexpdata>`_
* `Issue tracker (at GitHub) <https://github.com/tkf/sexpdata/issues>`_
* `PyPI <http://pypi.python.org/pypi/sexpdata>`_
* `Travis CI <https://travis-ci.org/#!/tkf/sexpdata>`_
