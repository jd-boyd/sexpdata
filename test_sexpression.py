from sexpression import (
    parse, tosexp, Symbol, String, Quoted, ParenMismatched)
from nose.tools import eq_, raises

data_identity = [
    Symbol('a'),
    String('a'),
    [Symbol('a')],
    [String('a')],
    Quoted(Symbol('a')),
    Quoted(String('a')),
    Quoted([Symbol('a')]),
    Quoted([String('a')]),
    [Symbol('a'), Symbol('b')],
    [Symbol('a'), [Symbol('b')]],
    [Symbol('a'), Quoted([Symbol('b')])],
]


def check_identity(obj):
    eq_(parse(tosexp(obj))[0], obj)


def test_identity():
    for data in data_identity:
        yield (check_identity, data)


@raises(ParenMismatched)
def test_too_many_parentheses():
    parse("(a b))")


@raises(ParenMismatched)
def test_not_enough_parentheses():
    parse("(a (b)")
