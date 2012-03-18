from itertools import chain
from string import whitespace

atom_end = set('()"\'') | set(whitespace)


class SExpBase(object):

    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return "{0}({1!r})".format(self.__class__.__name__, self._name)


class Symbol(SExpBase):
    pass


class String(SExpBase):
    pass


class Quoted(SExpBase):
    pass


def parse_str(iterator):
    while True:
        c = iterator.next()
        if c == '"':
            return
        elif c == '\\':
            yield c
            yield iterator.next()
        else:
            yield c


def parse_atom(iterator):
    chars = []
    c = iterator.next()
    try:
        while True:
            if c in atom_end:
                break
            chars.append(c)
            c = iterator.next()
    except StopIteration:
        c = None
    return (atom(''.join(chars)), c)


def atom(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


def parse_sexp(iterator):
    c = iterator.next()
    sexp = []
    try:
        while True:
            if c is None:
                break
            elif c == '"':
                sexp.append(String(''.join(parse_str(chain([c], iterator)))))
                c = iterator.next()
            elif c in whitespace:
                c = iterator.next()
                continue
            elif c == '(':
                (subsexp, c) = parse_sexp(iterator)
                sexp.append(subsexp)
                assert c == ')'
                c = iterator.next()
            elif c == ')':
                break
            elif c == "'":
                c = iterator.next()
                if c == '(':
                    (subsexp, c) = parse_sexp(iterator)
                    assert c == ')'
                    c = iterator.next()
                else:
                    (subsexp, c) = parse_atom(chain([c], iterator))
                sexp.append(Quoted(subsexp))
            else:
                (atom, c) = parse_atom(chain([c], iterator))
                sexp.append(atom)
    except StopIteration:
        c = None
    return (sexp, c)


def parse(iterable):
    """
    Parse s-expression.

    >>> parse("(a b)")
    [[Symbol('a'), Symbol('b')]]
    >>> parse("a")
    [Symbol('a')]
    >>> parse("(a 'b)")
    [[Symbol('a'), Quoted(Symbol('b'))]]
    >>> parse("(a '(b))")
    [[Symbol('a'), Quoted([Symbol('b')])]]
    >>> parse("(a (b)")  # not enough ')'
    Traceback (most recent call last):
        ...
    AssertionError
    >>> parse("(a b))")  # too many ')'
    Traceback (most recent call last):
        ...
    AssertionError

    """
    (sexp, c) = parse_sexp(iter(iterable))
    assert c is None
    return sexp
