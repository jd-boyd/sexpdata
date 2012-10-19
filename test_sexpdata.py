from sexpdata import (
    ExpectClosingBracket, ExpectNothing, LookAheadIterator,
    parse, tosexp, Symbol, String, Quoted, bracket,
)
from nose.tools import eq_, raises

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


def test_lookaheaditerator_as_normal():
    for length in [0, 1, 2, 3, 5]:
        lst = range(length)
        yield (eq_, list(iter(lst)), list(LookAheadIterator(lst)))


def test_lookaheaditerator_lookahead():
    laiter = LookAheadIterator(range(3))
    eq_(laiter.lookahead(), 0)
    eq_(laiter.lookahead(), 0)
    eq_(laiter.next(), 0)
    eq_(laiter.lookahead(), 1)
    eq_(laiter.lookahead(), 1)
    eq_(laiter.next(), 1)
    eq_(laiter.lookahead(), 2)
    eq_(laiter.lookahead(), 2)
    eq_(laiter.next(), 2)
    try:
        laiter.next()
        assert False
    except StopIteration:
        assert True
    try:
        laiter.lookahead()
        assert False
    except StopIteration:
        assert True


def test_lookaheaditerator_has_next():
    laiter = LookAheadIterator(range(3))
    assert laiter.has_next() is True
    list(laiter)
    assert laiter.has_next() is False


def test_lookaheaditerator_consume_until_simple():
    laiter = LookAheadIterator(range(10))
    laiter.consume_until(3)
    eq_(laiter.next(), 4)
