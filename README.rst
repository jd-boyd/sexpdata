S-expression parser for Python
==============================

`sexpdata` is a simple S-expression parser/serializer.  It has
simple `load` and `dump` functions like `pickle`, `json` or `PyYAML`
module.

>>> from sexpdata import loads, dumps
>>> loads('("a" "b")')
['a', 'b']
>>> print(dumps(['a', 'b']))
("a" "b")


You can install `sexpdata` from PyPI_::

  pip install sexpdata


Links:

* `Documentation (at Read the Docs) <http://sexpdata.readthedocs.org/>`_
* `Repository (at GitHub) <https://github.com/jd-boyd/sexpdata>`_
* `Issue tracker (at GitHub) <https://github.com/jd-boyd/sexpdata/issues>`_
* `PyPI <http://pypi.python.org/pypi/sexpdata>`_
* `Travis CI <https://travis-ci.org/#!/jd-boyd/sexpdata>`_


Making a release
----------------

1. `python -m build`
1. `twine check dist/*`
1. `git tag v1.0.x`
1. `twine upload dist/*`


License
-------

`sexpdata` is licensed under the terms of the BSD 2-Clause License.
See the source code for more information.
