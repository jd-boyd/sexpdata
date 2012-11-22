# -*- coding: utf-8 -*-

from sexpdata import (
    PY3,
    ExpectClosingBracket, ExpectNothing,
    parse, tosexp, Symbol, String, Quoted, bracket,
)
from nose.tools import eq_, raises


### Python 3 compatibility

if PY3:
    utf8 = lambda s: s
else:
    utf8 = lambda s: s.decode('utf-8')

utf8.__doc__ = """
Decode a raw string into unicode object.  Do nothing in Python 3.
"""


### Test cases

data_identity = [
    Symbol('a'),
    'a',
    [Symbol('a')],
    ['a'],
    Quoted(Symbol('a')),
    Quoted('a'),
    Quoted([Symbol('a')]),
    Quoted(['a']),
    [Symbol('a'), Symbol('b')],
    [Symbol('a'), [Symbol('b')]],
    [Symbol('a'), Quoted([Symbol('b')])],
    [Symbol('a'), Quoted(Symbol('b')), Symbol('c')],
    [Symbol('a'), Quoted([Symbol('b')]), Symbol('c')],
    [Symbol('a'), Quoted(Symbol('b')), Quoted(Symbol('c')), Symbol('d')],
    [Symbol('a'), Quoted(Symbol('b')), Symbol('c'), Quoted(Symbol('d'))],
    [bracket([1, 2, 3], '[')],
    [bracket([1, [2, bracket([3], '[')]], '[')],
    '""',
    "",
    "''",
    "'",
    '\\',
    '\\\"',
    ";",
    utf8("日本語能力!!ソﾊﾝｶｸ"),
]

data_identity += map(lambda x: x[0], String._lisp_quoted_specials)
data_identity += map(lambda x: x[1], String._lisp_quoted_specials)


def check_identity(obj):
    eq_(parse(tosexp(obj))[0], obj)


def test_identity():
    for data in data_identity:
        yield (check_identity, data)


def test_tosexp_str_as():
    yield (eq_, tosexp('a', str_as='symbol'), 'a')
    yield (eq_, tosexp(['a'], str_as='symbol'), '(a)')
    yield (eq_, tosexp('a'), '"a"')
    yield (eq_, tosexp(['a']), '("a")')
    yield (eq_, tosexp(Quoted('a')), '\'"a"')
    yield (eq_, tosexp(Quoted(['a']), str_as='symbol'), '\'(a)')
    yield (eq_, tosexp([Quoted('a')], str_as='symbol'), '(\'a)')
    yield (eq_, tosexp(Quoted('a'), str_as='symbol'), '\'a')
    yield (eq_, tosexp(Quoted(['a'])), '\'("a")')
    yield (eq_, tosexp([Quoted('a')]), '(\'"a")')


def test_tosexp_tuple_as():
    yield (eq_, tosexp(('a', 'b')), '("a" "b")')
    yield (eq_, tosexp(('a', 'b'), tuple_as='array'), '["a" "b"]')
    yield (eq_, tosexp([('a', 'b')]), '(("a" "b"))')
    yield (eq_, tosexp([('a', 'b')], tuple_as='array'), '(["a" "b"])')
    yield (eq_, tosexp(Quoted(('a',))), '\'("a")')
    yield (eq_, tosexp(Quoted(('a',)), tuple_as='array'), '\'["a"]')


@raises(ExpectNothing)
def test_too_many_brackets():
    parse("(a b))")


@raises(ExpectClosingBracket)
def test_not_enough_brackets():
    parse("(a (b)")


def test_no_eol_after_comment():
    eq_(parse('a ; comment'), [Symbol('a')])
