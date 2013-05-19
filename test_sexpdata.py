# -*- coding: utf-8 -*-

from sexpdata import (
    PY3,
    ExpectClosingBracket, ExpectNothing,
    parse, tosexp, Symbol, String, Quoted, bracket,
)
import unittest
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
    Symbol(r'path.join'),
    Symbol(r'path join'),
    Symbol(r'path\join'),
    utf8("日本語能力!!ソﾊﾝｶｸ"),
]

data_identity += map(lambda x: x[0], String._lisp_quoted_specials)
data_identity += map(lambda x: x[1], String._lisp_quoted_specials)


def check_identity(obj):
    eq_(parse(tosexp(obj))[0], obj)


def test_identity():
    for data in data_identity:
        yield (check_identity, data)


class BaseTestCase(unittest.TestCase):

    def assert_parse(self, string, obj):
        """`string` must be parsed into `obj`."""
        self.assertEqual(parse(string)[0], obj)


class TestSymbol(BaseTestCase):

    def test_parse_symbol_with_backslash(self):
        self.assert_parse(r'path\.join', Symbol(r'path.join'))
        self.assert_parse(r'path\ join', Symbol(r'path join'))
        self.assert_parse(r'path\\join', Symbol(r'path\join'))

    def test_parse_special_symbols(self):
        for s in [r'\\', r"\'", r"\`", r'\"', r'\(', r'\)', r'\[', r'\]',
                  r'\ ', r'\.', r'\,', r'\?', r'\;', r'\#']:
            self.assert_parse(s, Symbol(Symbol.unquote(s)))


class TestParseFluctuation(BaseTestCase):

    def test_spaces_must_be_ignored(self):
        self.assert_parse(' \n\t\r  ( ( a )  \t\n\r  ( b ) )  ',
                          [[Symbol('a')], [Symbol('b')]])

    def test_spaces_between_parentheses_can_be_skipped(self):
        self.assert_parse('((a)(b))', [[Symbol('a')], [Symbol('b')]])

    def test_spaces_between_double_quotes_can_be_skipped(self):
        self.assert_parse('("a""b")', ['a', 'b'])


class TestUnicode(BaseTestCase):

    ustr = utf8("日本語能力!!ソﾊﾝｶｸ")

    def test_dump_raw_utf8(self):
        ustr = self.ustr
        sexp = utf8('"{0}"').format(ustr)
        self.assertEqual(String(ustr.encode('utf-8')).tosexp(), sexp)

    def test_parse_raw_utf8(self):
        ustr = self.ustr
        sexp = utf8('"{0}"').format(ustr)
        self.assert_parse(sexp.encode('utf-8'), ustr.encode('utf-8'))


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
