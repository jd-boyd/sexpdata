from distutils.core import setup

import sexpdata

setup(
    name='sexpdata',
    version=sexpdata.__version__,
    py_modules=['sexpdata'],
    author=sexpdata.__author__,
    author_email='aka.tkf@gmail.com',
    url='https://github.com/tkf/sexpdata',
    license=sexpdata.__license__,
    description='S-expression parser for Python',
    long_description=sexpdata.__doc__,
    keywords='s-expression, lisp, parser',
    classifiers=[
        "Development Status :: 3 - Alpha",
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        "Programming Language :: Lisp",
        "Programming Language :: Emacs-Lisp",
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
)
