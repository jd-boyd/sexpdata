# [[[cog import cog; cog.outl('"""\n%s\n"""' % file('README.rst').read()) ]]]
from __future__ import unicode_literals

"""
S-expression parser for Python
==============================

`sexpdata` is a simple S-expression parser/serializer.  It has
simple `load` and `dump` functions like `pickle`, `json` or `PyYAML`
module.

>>> from sexpdata import loads, dumps
>>> loads('("a" "b")')
['a', 'b']
>>> print(dumps(['a', 'b']))
("a" "b")


You can install `sexpdata` from PyPI_::

  pip install sexpdata


Links:

* `Documentation (at Read the Docs) <http://sexpdata.readthedocs.org/>`_
* `Repository (at GitHub) <https://github.com/tkf/sexpdata>`_
* `Issue tracker (at GitHub) <https://github.com/tkf/sexpdata/issues>`_
* `PyPI <http://pypi.python.org/pypi/sexpdata>`_
* `Travis CI <https://travis-ci.org/#!/tkf/sexpdata>`_


License
-------

`sexpdata` is licensed under the terms of the BSD 2-Clause License.
See the source code for more information.

"""
# [[[end]]]

# Copyright (c) 2012 Takafumi Arakaki
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.

# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__version__ = "1.0.4"
__author__ = "Joshua D. Boyd, Takafumi Arakaki"
__license__ = "BSD License"
__all__ = [
    # API functions:
    "load",
    "loads",
    "dump",
    "dumps",
    "parse",
    # Utility functions:
    "car",
    "cdr",
    # S-expression classes:
    "Symbol",
    "String",
    "Quoted",
    "Brackets",
    "Parens",
    # Position tracking:
    "Position",
    # Exception classes:
    "SExpError",
    "ExpectClosingBracket",
    "ExpectNothing",
    "ExpectSExp",
    "UnterminatedString",
    "InvalidEscape",
]

import re
from collections import namedtuple

try:
    from collections.abc import Iterable, Mapping, Sequence
except ImportError:
    # Python < 3.3
    from collections import Iterable, Mapping, Sequence
from itertools import chain
from string import whitespace
from functools import singledispatch


### Position Tracking


class Position:
    """Represents a position in the source text with line and column numbers."""

    def __init__(self, line=1, column=1, offset=0):
        self.line = line
        self.column = column
        self.offset = offset

    def __repr__(self):
        return f"Position(line={self.line}, column={self.column})"

    def __str__(self):
        return f"line {self.line}, column {self.column}"


### Interface


def load(filelike, **kwds):
    """
    Load object from S-expression stored in `filelike`.

    :arg  filelike: A text stream object.

    See :func:`loads` for valid keyword arguments.

    >>> import io
    >>> fp = io.StringIO()
    >>> sexp = [Symbol('a'), Symbol('b')]   # let's dump and load this object
    >>> dump(sexp, fp)
    >>> _ = fp.seek(0)
    >>> load(fp) == sexp
    True

    """
    return loads(filelike.read(), **kwds)


def loads(string, **kwds):
    """
    Load object from S-expression `string`.

    :arg        string: String containing an S-expression.
    :type          nil: str or None
    :keyword       nil: A symbol interpreted as an empty list.
                        Default is ``'nil'``.
    :type         true: str or None
    :keyword      true: A symbol interpreted as True.
                        Default is ``'t'``.
    :type        false: str or None
    :keyword     false: A symbol interpreted as False.
                        Default is ``None``.
    :type     line_comment: str
    :keyword  line_comment: Beginning of line comment.
                            Default is ``';'``.

    >>> loads("(a b)")
    [Symbol('a'), Symbol('b')]
    >>> loads("a")
    Symbol('a')
    >>> loads("(a 'b)")
    [Symbol('a'), Quoted(Symbol('b'))]
    >>> loads("(a '(b))")
    [Symbol('a'), Quoted([Symbol('b')])]
    >>> loads('''
    ... ;; This is a line comment.
    ... ("a" "b")  ; this is also a comment.
    ... ''')
    ['a', 'b']
    >>> loads('''
    ... # This is a line comment.
    ... ("a" "b")  # this is also a comment.
    ... ''', line_comment='#')
    ['a', 'b']

    ``nil`` is converted to an empty list by default.  You can use
    keyword argument `nil` to change what symbol must be interpreted
    as nil:

    >>> loads("nil")
    []
    >>> loads("null", nil='null')
    []
    >>> loads("nil", nil=None)
    Symbol('nil')

    ``t`` is converted to True by default.  You can use keyword
    argument `true` to change what symbol must be converted to True.:

    >>> loads("t")
    True
    >>> loads("#t", true='#t')
    True
    >>> loads("t", true=None)
    Symbol('t')

    No symbol is converted to False by default.  You can use keyword
    argument `false` to convert a symbol to False.

    >>> loads("#f")
    Symbol('#f')
    >>> loads("#f", false='#f')
    False
    >>> loads("nil", false='nil', nil=None)
    False

    """
    obj = parse(string, **kwds)
    assert len(obj) == 1  # FIXME: raise an appropriate error
    return obj[0]


def dump(obj, filelike, **kwds):
    """
    Write `obj` as an S-expression into given stream `filelike`.

    :arg       obj: A Python object.
    :arg  filelike: A text stream object.

    See :func:`dumps` for valid keyword arguments.

    >>> import io
    >>> fp = io.StringIO()
    >>> dump(('a', 'b'), fp, str_as='symbol')
    >>> print(fp.getvalue())
    (a b)

    """
    filelike.write(dumps(obj, **kwds))


def dumps(obj, **kwds):
    """
    Convert python object into an S-expression.

    :arg           obj: A Python object.
    :type       str_as: ``'symbol'`` or ``'string'``
    :keyword    str_as: How string should be interpreted.
                        Default is ``'string'``.
    :type     tuple_as: ``'list'`` or ``'array'``
    :keyword  tuple_as: How tuple should be interpreted.
                        Default is ``'list'``.
    :type      true_as: str
    :keyword   true_as: How True should be interpreted.
                        Default is ``'t'``
    :type     false_as: str
    :keyword  false_as: How False should be interpreted.
                        Default is ``'()'``
    :type      none_as: str
    :keyword   none_as: How None should be interpreted.
                        Default is ``'()'``
    :type     pretty_print: bool
    :keyword  pretty_print: Format output as a tree.
                           Default is ``False``
    :type     indent_as: str
    :keyword  indent_as: String to use for each level of tree indentation.
                         Default is ``'  '``

    Basic usage:

    >>> print(dumps(['a', 'b']))
    ("a" "b")
    >>> print(dumps(['a', 'b'], str_as='symbol'))
    (a b)
    >>> print(dumps(dict(a=1)))
    (:a 1)
    >>> ProperTuple = namedtuple('ProperTuple', 'k')
    >>> print(dumps(ProperTuple('v')))
    (:k "v")
    >>> print(dumps([None, True, False, ()]))
    (() t () ())
    >>> print(dumps([None, True, False, ()],
    ...             none_as='null', true_as='#t', false_as='#f'))
    (null #t #f ())
    >>> print(dumps(('a', 'b')))
    ("a" "b")
    >>> print(dumps(('a', 'b'), tuple_as='array'))
    ["a" "b"]

    More verbose usage:

    >>> print(dumps([Symbol('a'), Symbol('b')]))
    (a b)
    >>> print(dumps(Symbol('a')))
    a
    >>> print(dumps([Symbol('a'), Quoted(Symbol('b'))]))
    (a 'b)
    >>> print(dumps([Symbol('a'), Quoted([Symbol('b')])]))
    (a '(b))

    """
    return str(tosexp(obj, **kwds))


def car(obj):
    """
    Alias of ``obj[0]``.

    >>> car(loads('(a . b)'))
    Symbol('a')
    >>> car(loads('(a b)'))
    Symbol('a')

    """
    return obj[0]


def cdr(obj):
    """
    `cdr`-like function.

    >>> cdr(loads('(a . b)'))
    Symbol('b')
    >>> cdr(loads('(a b)'))
    [Symbol('b')]
    >>> cdr(loads('(a . (b))'))
    [Symbol('b')]
    >>> cdr(loads('(a)'))
    []
    >>> cdr(loads('(a . nil)'))
    []

    """
    # This is very lazy implementation.  Probably the best way to do
    # it is to define `Cons` S-expression class.
    if len(obj) > 2:
        if obj[1] == Symbol("."):
            return obj[2]
    return obj[1:]


### Core


@singledispatch
def tosexp(obj, **kwds):
    """
    Convert an object to an S-expression (`dumps` is just calling this).

    See this table for comparison of lispy languages, to support them
    as much as possible:
    `Lisp: Common Lisp, Scheme/Racket, Clojure, Emacs Lisp - Hyperpolyglot
    <http://hyperpolyglot.org/lisp>`_

    Most classes can be supported by tosexp() by adding a __to_lisp_as__ method
    that returns a restructuring of an instance. The method can use builtin
    types, sexpdata hinting classes, and instances of classes that have
    tosexp() support.

    Methods that require customizing the recursion or output string of tosexp()
    should be registered with @sexpdata.tosexp.register(). Also the default
    handlers can be overridden by re-registration.

    Define tosexp() for a simple immutable Cons class. The dot is formatted
    rather than doing a 3-tuple w/Symbol('.') hack.

    >>> import sexpdata
    >>> class Cons(namedtuple('Cons', 'car cdr')):
    ...     pass
    >>> @sexpdata.tosexp.register(Cons)
    ... def _(obj, **kwds):
    ...     return '({0} . {1})'.format(sexpdata.tosexp(obj.car, **kwds),
    ...                                 sexpdata.tosexp(obj.cdr, **kwds))
    ...
    >>> dumps(Cons(True, False))
    '(t . ())'

    A simple alist using Cons:

    >>> dumps(map(Cons, 'abcde', range(5)), str_as='symbol')
    '((a . 0) (b . 1) (c . 2) (d . 3) (e . 4))'

    Overriding the float handler for application-wide formatting:

    >>> @sexpdata.tosexp.register(float)
    ... def _(obj, **kwds):
    ...     return '{0:.3}'.format(obj)
    ...
    >>> import math
    >>> tuple(round(math.pi, n) for n in range(5)) # doctest: +SKIP
    (3.0, 3.1, 3.14, 3.142, 3.1416)
    >>> dumps(round(math.pi, n) for n in range(5))
    '(3.0 3.1 3.14 3.14 3.14)'
    """
    if hasattr(obj, "__to_lisp_as__"):
        return tosexp(obj.__to_lisp_as__(), **kwds)
    else:
        raise TypeError(
            "Object of type '{0}' cannot be converted by `tosexp`. "
            "It's value is '{1!r}'".format(type(obj), obj)
        )


@tosexp.register(Iterable)
@tosexp.register(Mapping)
def _(obj, **kwds):
    return tosexp(Parens(obj), **kwds)


@tosexp.register(tuple)
def _(obj, tuple_as="list", **kwds):
    kwds["tuple_as"] = tuple_as
    if hasattr(obj, "__to_lisp_as__"):
        return tosexp(obj.__to_lisp_as__(), **kwds)
    elif hasattr(obj, "_asdict"):
        return tosexp(Parens(obj._asdict()), **kwds)
    elif tuple_as == "list":
        return tosexp(Parens(obj), **kwds)
    elif tuple_as == "array":
        return tosexp(Brackets(obj), **kwds)
    else:
        raise ValueError("tuple_as={0!r} is not valid".format(tuple_as))


@tosexp.register(str)
def _(obj, str_as="string", **kwds):
    kwds["str_as"] = str_as
    if str_as == "symbol":
        return obj
    elif str_as == "string":
        return tosexp(String(obj))
    else:
        raise ValueError("str_as={0!r} is not valid".format(str_as))


@tosexp.register(type(None))
def _(obj, none_as="()", **kwds):
    return none_as


@tosexp.register(bool)
def _(obj, false_as="()", true_as="t", **kwds):
    return true_as if obj else false_as


@tosexp.register(float)
@tosexp.register(int)
def _(obj, **kwds):
    return str(obj)


class String:
    __match_args__ = ("object",)

    def __init__(self, object, position=None):
        print("INIT", object)
        self._s = str(object)
        self.position = position

    def __eq__(self, other):
        # I'm not confident that this won't have to be backed out.
        print("EQ", self.__class__, other.__class__)
        return self.__class__ == other.__class__ and str.__eq__(self._s, other._s)
        # return other.__class__ in (self.__class__, str) and str.__eq__(self, other)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        """
        >>> D = {'a': 1, String('a'): 2, Symbol('a'): 3}
        >>> len(D)
        3
        """
        return str.__hash__(self._s)

    _lisp_quoted_specials = [  # from Pymacs
        ("\\", "\\\\"),  # must come first to avoid doubly quoting "\"
        ('"', '\\"'),
        ("\b", "\\b"),
        ("\f", "\\f"),
        ("\n", "\\n"),
        ("\r", "\\r"),
        ("\t", "\\t"),
    ]

    _lisp_quoted_to_raw = dict((q, r) for (r, q) in _lisp_quoted_specials)

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, str.__repr__(self._s))

    def __str__(self):
        return self._s

    @classmethod
    def quote(cls, string):
        for s, q in cls._lisp_quoted_specials:
            if type(string) == str:
                string = string.replace(s, q)
            else:
                string = string._s.replace(s, q)
        return string

    @classmethod
    def unquote(cls, string):
        return cls._lisp_quoted_to_raw.get(string, string)

    def value(self):
        return str(self._s)


@tosexp.register(String)
def _(obj, **kwds):
    return '"' + String.quote(obj) + '"'


class Symbol(String):
    _lisp_quoted_specials = [
        ("\\", "\\\\"),  # must come first to avoid doubly quoting "\"
        ("'", r"\'"),
        ("`", r"\`"),
        ('"', r"\""),
        ("(", r"\("),
        (")", r"\)"),
        ("[", r"\["),
        ("]", r"\]"),
        (" ", r"\ "),
        (",", r"\,"),
        ("?", r"\?"),
        (";", r"\;"),
        ("#", r"\#"),
    ]

    _lisp_quoted_to_raw = dict((q, r) for (r, q) in _lisp_quoted_specials)


@tosexp.register(Symbol)
def _(obj, **kwds):
    return Symbol.quote(obj)


class Quoted(namedtuple("Quoted", "x")):
    def __repr__(self):
        return "{0.__class__.__name__}({0.x!r})".format(self)


@tosexp.register(Quoted)
def _(obj, **kwds):
    return "'" + tosexp(obj.x, **kwds)


class Delimiters(namedtuple("Delimiters", "I")):
    def __new__(cls, *args):
        if not args:
            raise ValueError("Expected an Iterable/Mapping argument or *args")
        x = args[0] if len(args) == 1 else args

        if isinstance(x, Mapping):
            plist_pairs = ((Symbol(":" + k), v) for k, v in x.items())
            return tuple.__new__(cls, (tuple(chain.from_iterable(plist_pairs)),))
        elif isinstance(x, (str, bytes)) or not isinstance(x, Iterable):
            return tuple.__new__(cls, ((x,),))  # unary *args
        elif isinstance(x, Sequence):
            return tuple.__new__(cls, (x,))
        else:  # isinstance(x, Iterable)
            return tuple.__new__(cls, (tuple(x),))

    @staticmethod
    def from_opener(opener, val):
        cls_map = dict((cls.opener, cls) for cls in Delimiters.__subclasses__())
        if opener in cls_map.keys():
            return cls_map[opener](val)
        else:
            raise TypeError

    @staticmethod
    def get_brackets():
        return {cls.opener: cls.closer for cls in Delimiters.__subclasses__()}


@tosexp.register(Delimiters)
def _(self, **kwds):
    # Don't break up expressions produced by certain overloads of tosexp
    dont_break = all(
        tosexp.dispatch(type(x)) not in DONT_BREAK_OVERLOADS for x in self.I
    )

    if "pretty_print" in kwds and kwds["pretty_print"] and not dont_break:
        expr_separator = "\n"
        exprs_indent = kwds["indent_as"] if "indent_as" in kwds else "  "
        exprs_separator = "\n"
    else:
        expr_separator = " "
        exprs_indent = ""
        exprs_separator = ""

    exprs = expr_separator.join(tosexp(x, **kwds) for x in self.I)
    indented_exprs = "".join(exprs_indent + line for line in exprs.splitlines(True))

    return (
        self.__class__.opener
        + exprs_separator
        + indented_exprs
        + exprs_separator
        + self.__class__.closer
    )


DONT_BREAK_OVERLOADS = [
    tosexp.dispatch(c) for c in (object, Iterable, Mapping, tuple, Delimiters)
]


class Brackets(Delimiters):
    """
    Outputs an Iterable or Mapping with square brackets.

    Selectively make a container an array:

    >>> dumps(Brackets(list(range(5))))
    '[0 1 2 3 4]'

    >>> dumps(Brackets(dict(a=1)))
    '[:a 1]'
    """

    opener, closer = "[", "]"


class Parens(Delimiters):
    """
    Outputs an Iterable or Mapping with parentheses.

    By default Iterables and Mappings output with parentheses.

    >>> dumps(range(5))
    '(0 1 2 3 4)'
    >>> dumps(dict(a=1))
    '(:a 1)'

    Selectively override the tuple_as='array' default parameter:

    >>> dumps((0, Parens((1, 2, 3)), 4), tuple_as='array')
    '[0 (1 2 3) 4]'
    """

    opener, closer = "(", ")"


def bracket(val, bra):
    if bra == "(":
        return val
    else:
        return Delimiters.from_opener(bra, val)


class SExpError(Exception):
    """Base class for S-expression parsing errors with position information."""

    def __init__(self, message, position=None):
        self.position = position
        if position:
            super().__init__(f"{message} at {position}")
        else:
            super().__init__(message)


class ExpectClosingBracket(SExpError):
    def __init__(self, got, expect, position=None):
        message = (
            "Not enough closing brackets. "
            f"Expected {expect!r} to be the last letter in the sexp. "
            f"Got: {got!r}"
        )
        super().__init__(message, position)


class ExpectNothing(SExpError):
    def __init__(self, got, position=None):
        message = (
            "Too many closing brackets. "
            f"Expected no character left in the sexp. "
            f"Got: {got!r}"
        )
        super().__init__(message, position)


class ExpectSExp(SExpError):
    def __init__(self, position=None):
        message = "No s-exp is found after an apostrophe"
        super().__init__(message, position)


class UnterminatedString(SExpError):
    def __init__(self, position=None):
        message = "Unterminated string literal"
        super().__init__(message, position)


class InvalidEscape(SExpError):
    def __init__(self, escape_char, position=None):
        message = f"Invalid escape sequence: \\{escape_char}"
        super().__init__(message, position)


class Parser(object):
    brackets: dict
    closing_brackets: set
    _atom_end_basic: set
    _atom_end_basic_or_escape_regexp: str

    def __init__(
        self, string, string_to=None, nil="nil", true="t", false=None, line_comment=";"
    ):
        self.string = string
        self.nil = nil
        self.true = true
        self.false = false
        self.string_to = (lambda x: x) if string_to is None else string_to
        self.line_comment = line_comment

        # Build position mapping for error reporting
        self.position_map = self._build_position_map(string)

        # Compute brackets from delimiter
        self.brackets = Delimiters.get_brackets()
        self.closing_brackets = set(self.brackets.values())
        self._atom_end_basic = (
            set(self.brackets) | set(self.closing_brackets) | set('"') | set(whitespace)
        )
        self._atom_end_basic_or_escape_regexp = "|".join(
            map(re.escape, self._atom_end_basic | set("\\"))
        )
        self.quote_or_escape_re = re.compile(r'"|\\')
        self.atom_end = set([line_comment]) | self._atom_end_basic
        self.atom_end_or_escape_re = re.compile(
            "{0}|{1}".format(
                self._atom_end_basic_or_escape_regexp, re.escape(line_comment)
            )
        )

    def _build_position_map(self, string):
        """Build a mapping from string offset to (line, column)"""
        positions = {}
        line, column = 1, 1
        for i, char in enumerate(string):
            positions[i] = Position(line, column, i)
            if char == "\n":
                line += 1
                column = 1
            else:
                column += 1
        positions[len(string)] = Position(line, column, len(string))
        return positions

    def get_position(self, offset):
        """Get position information for a given string offset."""
        return self.position_map.get(offset, Position())

    def parse_str(self, i):
        string = self.string
        chars = []
        append = chars.append
        search = self.quote_or_escape_re.search

        start_pos = self.get_position(i)
        while True:
            i += 1
            match = search(string, i)
            if match is None:
                raise UnterminatedString(start_pos)
            end = match.start()
            append(string[i:end])
            c = match.group()
            if c == '"':
                i = end + 1
                break
            elif c == "\\":
                i = end + 1
                if i >= len(string):
                    raise InvalidEscape(end, self.get_position(end))
                append(String.unquote(c + string[i]))
        else:
            raise ExpectClosingBracket('"', self.get_position())
        return (i, "".join(chars))

    def parse_atom(self, i):
        string = self.string
        chars = []
        append = chars.append
        search = self.atom_end_or_escape_re.search
        atom_end = self.atom_end
        start_pos = self.get_position(i)

        while True:
            match = search(string, i)
            if not match:
                append(string[i:])
                i = len(string)
                break
            end = match.start()
            append(string[i:end])
            c = match.group()
            if c in atom_end:
                i = end  # this is different from str
                break
            elif c == "\\":
                i = end + 1
                if i >= len(string):
                    raise InvalidEscape("EOF", self.get_position(end))
                next_char = string[i]
                try:
                    unquoted = Symbol.unquote(c + next_char)
                    append(unquoted)
                except KeyError:
                    raise InvalidEscape(next_char, self.get_position(i))
            i += 1

        return (i, self.atom("".join(chars), start_pos))

    def atom(self, token, position=None):
        if token == self.nil:
            return []
        if token == self.true:
            return True
        if token == self.false:
            return False
        try:
            return int(token)
        except ValueError:
            try:
                result = float(token)
                # Block automatic conversion to infinity or NaN
                if (
                    result in (float("inf"), float("-inf")) or result != result
                ):  # NaN check
                    raise ValueError("Invalid s-exp float")
                return result
            except ValueError:
                return Symbol(token, position)

    def parse_sexp(self, i):
        string = self.string
        len_string = len(self.string)
        sexp = []
        append = sexp.append
        bracket_stack = []  # Track opening brackets for better error reporting
        while i < len_string:
            c = string[i]
            current_pos = self.get_position(i)

            if c == '"':
                try:
                    (i, subsexp) = self.parse_str(i)
                    append(self.string_to(subsexp))
                except SExpError:
                    raise  # Re-raise with position already set
            elif c in whitespace:
                i += 1
                continue
            elif c in self.brackets:
                close = self.brackets[c]
                bracket_stack.append((c, close, current_pos))
                (i, subsexp) = self.parse_sexp(i + 1)
                append(bracket(subsexp, c))
                try:
                    nc = string[i]
                except IndexError:
                    bracket_info = bracket_stack[-1] if bracket_stack else None
                    if bracket_info:
                        raise ExpectClosingBracket(
                            None, bracket_info[1], bracket_info[2]
                        )
                    else:
                        raise ExpectClosingBracket(None, close, current_pos)
                if nc != close:
                    raise ExpectClosingBracket(nc, close, current_pos)
                bracket_stack.pop() if bracket_stack else None
                i += 1
            elif c in self.closing_brackets:
                break
            elif c == "'":
                quote_pos = current_pos
                next_parse_start = i + 1
                (i, subsexp) = self.parse_sexp(next_parse_start)
                if not subsexp:
                    raise ExpectSExp(quote_pos)
                append(Quoted(subsexp[0]))
                sexp.extend(subsexp[1:])
            elif c == self.line_comment:
                i = string.find("\n", i) + 1
                if i <= 0:
                    i = len_string
                    break
            else:
                (i, subsexp) = self.parse_atom(i)
                append(subsexp)
        return (i, sexp)

    def parse(self):
        try:
            (i, sexp) = self.parse_sexp(0)
            if i < len(self.string):
                raise ExpectNothing(self.string[i:], self.get_position(i))
            return sexp
        except SExpError:
            raise  # Re-raise S-expression specific errors
        except Exception as e:
            # Wrap unexpected errors with position info if possible
            raise SExpError(f"Unexpected parsing error: {e}")


def parse(string, **kwds):
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
    assert type(string) == str
    return Parser(string, **kwds).parse()
