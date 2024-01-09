import sys

from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='sexpdata',
    version='1.0.2',
    py_modules=['sexpdata'],
    author='Joshua D. Boyd, Takafumi Arakaki',
    author_email='jdboyd@jdboyd.net',
    url='https://github.com/jd-boyd/sexpdata',
    license='BSD License',
    description='S-expression parser for Python',
    long_description=long_description,
    keywords='s-expression, lisp, parser',
    classifiers=[
        "Development Status :: 3 - Alpha",
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Programming Language :: Lisp",
        "Programming Language :: Emacs-Lisp",
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
)
