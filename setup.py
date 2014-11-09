import sys

from distutils.core import setup

with open('README.rst') as f:
    long_description = f.read()

install_requires = []
if sys.version_info < (3, 4):
    install_requires.append('singledispatch')
if sys.version_info < (2, 7):
    install_requires.append('ordereddict')

setup(
    name='sexpdata',
    version='0.0.4.dev1',
    py_modules=['sexpdata'],
    author='Takafumi Arakaki',
    author_email='aka.tkf@gmail.com',
    url='https://github.com/tkf/sexpdata',
    license='BSD License',
    description='S-expression parser for Python',
    long_description=long_description,
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        "Programming Language :: Lisp",
        "Programming Language :: Emacs-Lisp",
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    install_requires=install_requires,
)
