from string import whitespace
from collections import Iterator
import functools

BRACKETS = {'(': ')', '[': ']'}
CBRACKETS = set(BRACKETS.values())
ATOM_END = set(BRACKETS) | set(CBRACKETS) | set('"\'') | set(whitespace)


try:
    basestring
except NameError:
    basestring = str  # Python 3


def load(filelike):
    """
    Load object from S-expression stored in `filelike`.
    """
    return loads(filelike.read())


def loads(string):
    """
    Load object from S-expression `string`.

    >>> loads("(a b)")
    [Symbol('a'), Symbol('b')]
    >>> loads("a")
    Symbol('a')
    >>> loads("(a 'b)")
    [Symbol('a'), Quoted(Symbol('b'))]
    >>> loads("(a '(b))")
    [Symbol('a'), Quoted([Symbol('b')])]

    """
    obj = parse(string)
    assert len(obj) == 1  # FIXME: raise an appropriate error
    return obj[0]


def dump(obj, filelike, **kwds):
    """
    Serialize `obj` as a S-expression formatted stream to `filelike`.
    """
    filelike.write(dump(obj))


def dumps(obj, **kwds):
    """
    Convert python object into s-expression.

    >>> dumps([Symbol('a'), Symbol('b')])
    '(a b)'
    >>> dumps(Symbol('a'))
    'a'
    >>> dumps([Symbol('a'), Quoted(Symbol('b'))])
    "(a 'b)"
    >>> dumps([Symbol('a'), Quoted([Symbol('b')])])
    "(a '(b))"

    """
    return tosexp(obj, **kwds)


def tosexp(obj, stras='symbol', tupleas='list'):
    if isinstance(obj, list):
        return Bracket(obj, '(').tosexp(stras=stras, tupleas=tupleas)
    elif isinstance(obj, tuple):
        if tupleas == 'list':
            return Bracket(obj, '(').tosexp(stras=stras, tupleas=tupleas)
        elif tupleas == 'array':
            return Bracket(obj, '[').tosexp(stras=stras, tupleas=tupleas)
        else:
            raise ValueError('tupleas={0!r} is not valid'.format(tupleas))
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, basestring):
        if stras == 'symbol':
            return obj
        elif stras == 'string':
            return String(obj).tosexp(stras=stras, tupleas=tupleas)
        else:
            raise ValueError("stras={0!r} is not valid".format(stras))
    elif isinstance(obj, SExpBase):
        return obj.tosexp(stras=stras, tupleas=tupleas)
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

    def value(self):
        return self._val

    def tosexp(self, stras, tupleas):
        raise NotImplementedError


class Symbol(SExpBase):

    def tosexp(self, stras, tupleas):
        return self._val


class String(SExpBase):

    _lisp_quoted_specials = [  # from Pymacs
        ('"', '\\"'), ('\\', '\\\\'), ('\b', '\\b'), ('\f', '\\f'),
        ('\n', '\\n'), ('\r', '\\r'), ('\t', '\\t')]

    def tosexp(self, stras, tupleas):
        val = self._val
        for (s, q) in self._lisp_quoted_specials:
            val = val.replace(s, q)
        return '"{0}"'.format(val)


class Quoted(SExpBase):

    def tosexp(self, stras, tupleas):
        return "'{0}".format(tosexp(self._val, stras, tupleas))


class Bracket(SExpBase):

    def __init__(self, val, bra):
        assert bra in BRACKETS  # FIXME: raise an appropriate error
        super(Bracket, self).__init__(val)
        self._bra = bra

    def __repr__(self):
        return "{0}({1!r}, {2!r})".format(
            self.__class__.__name__, self._val, self._bra)

    def tosexp(self, stras, tupleas):
        bra = self._bra
        ket = BRACKETS[self._bra]
        c = ' '.join(tosexp(v, stras, tupleas) for v in self._val)
        return "{0}{1}{2}".format(bra, c, ket)


def bracket(val, bra):
    if bra == '(':
        return val
    else:
        return Bracket(val, bra)


class ExpectClosingBracket(Exception):

    def __init__(self, got, expect):
        super(ExpectClosingBracket, self).__init__(
            "Not enough closing brackets. "
            "Expected {0!r} to be the last letter in the sexp. "
            "Got: {1!r}".format(expect, got))


class ExpectNothing(Exception):

    def __init__(self, got):
        super(ExpectNothing, self).__init__(
            "Too many closing brackets. "
            "Expected no character left in the sexp. "
            "Got: {0!r}".format(got))


class LookAheadIterator(Iterator):

    def __init__(self, iterable):
        self._iter = iter(iterable)

    def next(self):
        if hasattr(self, '_next_item'):
            item = self._next_item
            del self._next_item
        else:
            item = next(self._iter)
        return item

    __next__ = next  # Python 3

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


def gas(converter):
    """
    Decorator to convert iterator to a function.

    It is just a function composition. The following two codes are
    equivalent.

    Using `@gas`::

        @gas(converter)
        def generator(args):
            ...

        result = generator(args)

    Manually do the same::

        def generator(args):
            ...

        result = converter(generator(args))

    Although this decorator can be used for composition of any kind of
    functions, it must be used only for generators as the name
    suggests (gas = Generator AS).

    Example:

    >>> @gas(list)
    ... def f():
    ...     for i in range(3):
    ...         yield i
    ...
    >>> f()  # this gives a list, not an iterator
    [0, 1, 2]

    """
    def wrapper(generator):
        @functools.wraps(generator)
        def func(*args, **kwds):
            return converter(generator(*args, **kwds))
        return func
    return wrapper


@gas(lambda x: String(''.join(x)))
def parse_str(laiter):
    assert laiter.next() == '"'  # never fail
    while True:
        c = laiter.next()
        if c == '"':
            return
        elif c == '\\':
            yield c
            yield laiter.next()
        else:
            yield c


@gas(lambda x: atom(''.join(x)))
def parse_atom(laiter):
    while laiter.has_next():
        if laiter.lookahead() in ATOM_END:
            break
        yield laiter.next()


def atom(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


@gas(list)
def parse_sexp(laiter):
    while laiter.has_next():
        c = laiter.lookahead()
        if c == '"':
            yield parse_str(laiter)
        elif c in whitespace:
            laiter.next()
            continue
        elif c in BRACKETS:
            close = BRACKETS[c]
            laiter.next()
            yield bracket(parse_sexp(laiter), c)
            if laiter.lookahead_safe() != close:
                raise ExpectClosingBracket(laiter.lookahead_safe(), close)
            laiter.next()
        elif c in CBRACKETS:
            break
        elif c == "'":
            laiter.next()
            subsexp = parse_sexp(laiter)
            yield Quoted(subsexp[0])
            for sexp in subsexp[1:]:
                yield sexp
        else:
            yield parse_atom(laiter)


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

    """
    laiter = LookAheadIterator(iterable)
    sexp = parse_sexp(laiter)
    if laiter.has_next():
        raise ExpectNothing(laiter.lookahead())
    return sexp
