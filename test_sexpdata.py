# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sexpdata import (
    PY3,
    ExpectClosingBracket, ExpectNothing,
    parse, tosexp, Symbol, String, Quoted, bracket,
)
import unittest
from nose.tools import eq_, raises


### Test utils

def compare_parsed(sexp, obj):
    eq_(parse(sexp), obj)


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
    "日本語能力!!ソﾊﾝｶｸ",
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

    ustr = "日本語能力!!ソﾊﾝｶｸ"

#    if not PY3:
        # Let's not support dumping/parsing bytes.
        # (In Python 3, ``string.encode()`` returns bytes.)

    def test_dump_raw_utf8(self):
        """
        Test that sexpdata supports dumping encoded (raw) string.

        See also: https://github.com/tkf/emacs-jedi/issues/43

        """
        ustr = self.ustr
        sexp = '"{0}"'.format(ustr)
        self.assertEqual(tosexp(ustr), sexp)

    def test_parse_raw_utf8(self):
        ustr = self.ustr
        sexp = '"{0}"'.format(ustr)
        self.assert_parse(sexp, ustr)


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


def test_issue_4():
    yield (compare_parsed, "(0 ;; (\n)", [[0]])
    yield (compare_parsed, "(0;; (\n)", [[0]])
