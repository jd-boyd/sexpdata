from itertools import chain
from string import whitespace

atom_end = set('()"\'') | set(whitespace)


def tosexp(obj):
    """
    Convert python object into s-expression.

    >>> tosexp([Symbol('a'), Symbol('b')])
    '(a b)'
    >>> tosexp(Symbol('a'))
    'a'
    >>> tosexp([Symbol('a'), Quoted(Symbol('b'))])
    "(a 'b)"
    >>> tosexp([Symbol('a'), Quoted([Symbol('b')])])
    "(a '(b))"

    """
    if isinstance(obj, list):
        return "({0})".format(' '.join(map(tosexp, obj)))
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, SExpBase):
        return obj.tosexp()
    else:
        raise TypeError(
            "Object of type '{0}' cannot be converted by `tosexp`. "
            "It's value is '{1!r}'".format(type(obj), obj))


class SExpBase(object):

    def __init__(self, val):
        self._val = val

    def __repr__(self):
        return "{0}({1!r})".format(self.__class__.__name__, self._val)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._val == other._val
        else:
            return False

    def tosexp(self):
        raise NotImplementedError


class Symbol(SExpBase):

    def tosexp(self):
        return self._val


class String(SExpBase):

    _lisp_quoted_specials = {  # from Pymacs
        '"': '\\"', '\\': '\\\\', '\b': '\\b', '\f': '\\f',
        '\n': '\\n', '\r': '\\r', '\t': '\\t'}

    def tosexp(self):
        val = self._val
        for (s, q) in self._lisp_quoted_specials.iteritems():
            val = val.replace(s, q)
        return '"{0}"'.format(val)


class Quoted(SExpBase):

    def tosexp(self):
        return "'{0}".format(tosexp(self._val))


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
                sexp.append(String(''.join(parse_str(iterator))))
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
