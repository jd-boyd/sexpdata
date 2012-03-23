from itertools import chain
from string import whitespace
from collections import Iterator

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


class ParenMismatched(Exception):
    pass


class LookAheadIterator(Iterator):

    def __init__(self, iterable):
        self._iter = iter(iterable)

    def next(self):
        if hasattr(self, '_next_item'):
            item = self._next_item
            del self._next_item
        else:
            item = self._iter.next()
        return item

    def has_next(self):
        try:
            self.lookahead()
            return True
        except StopIteration:
            return False

    def lookahead(self):
        self._next_item = self.next()
        return self._next_item

    def lookahead_safe(self, default=None):
        if self.has_next():
            return self.lookahead()
        else:
            return default


def parse_str(laiter):
    while True:
        c = laiter.next()
        if c == '"':
            return
        elif c == '\\':
            yield c
            yield laiter.next()
        else:
            yield c


def parse_atom(laiter):
    chars = []
    while laiter.has_next():
        if laiter.lookahead() in atom_end:
            break
        chars.append(laiter.next())
    return atom(''.join(chars))


def atom(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


def parse_sexp(laiter):
    sexp = []
    try:
        while True:
            c = laiter.lookahead()
            if c is None:
                break
            elif c == '"':
                laiter.next()
                sexp.append(String(''.join(parse_str(laiter))))
            elif c in whitespace:
                laiter.next()
                continue
            elif c == '(':
                laiter.next()
                sexp.append(parse_sexp(laiter))
                if laiter.lookahead_safe() != ')':
                    raise ParenMismatched(
                        "Not enough closing parentheses. "
                        "Expected ')' to be the last letter in the sexp. "
                        "Got: {0!r}".format(laiter.lookahead_safe()))
                laiter.next()
            elif c == ')':
                break
            elif c == "'":
                laiter.next()
                subsexp = parse_sexp(laiter)
                sexp.append(Quoted(subsexp[0]))
                sexp.extend(subsexp[1:])
            else:
                sexp.append(parse_atom(laiter))
    except StopIteration:
        pass  # FIXME: get rid of this
    return sexp


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
    >>> parse("(a (b)")  #doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    ParenMismatched: Not enough closing parentheses.
    Expected ')' to be the last letter in the sexp. Got: None
    >>> parse("(a b))")  #doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    ParenMismatched: Too many closing parentheses.
    Expected no character left in the sexp. Got: ')'

    """
    laiter = LookAheadIterator(iterable)
    sexp = parse_sexp(laiter)
    if laiter.has_next():
        raise ParenMismatched(
            "Too many closing parentheses. "
            "Expected no character left in the sexp. "
            "Got: {0!r}".format(laiter.lookahead()))
    return sexp
