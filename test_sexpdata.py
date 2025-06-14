# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sexpdata import (
    ExpectClosingBracket,
    ExpectNothing,
    ExpectSExp,
    UnterminatedString,
    InvalidEscape,
    SExpError,
    Position,
    parse,
    tosexp,
    Symbol,
    String,
    Quoted,
    bracket,
    Parens,
    Brackets,
    Delimiters,
)
import unittest
import sys

import pytest


### Test cases

data_identity = [
    Symbol("a"),
    "a",
    [Symbol("a")],
    ["a"],
    Quoted(Symbol("a")),
    Quoted("a"),
    Quoted([Symbol("a")]),
    Quoted(["a"]),
    [Symbol("a"), Symbol("b")],
    [Symbol("a"), [Symbol("b")]],
    [Symbol("a"), Quoted([Symbol("b")])],
    [Symbol("a"), Quoted(Symbol("b")), Symbol("c")],
    [Symbol("a"), Quoted([Symbol("b")]), Symbol("c")],
    [Symbol("a"), Quoted(Symbol("b")), Quoted(Symbol("c")), Symbol("d")],
    [Symbol("a"), Quoted(Symbol("b")), Symbol("c"), Quoted(Symbol("d"))],
    [Symbol("set"), Symbol("set'")],
    [bracket([1, 2, 3], "[")],
    [bracket([1, [2, bracket([3], "[")]], "[")],
    '""',
    "",
    "''",
    "'",
    "\\",
    '\\"',
    ";",
    Symbol(r"path.join"),
    Symbol(r"path join"),
    Symbol(r"path\join"),
    "日本語能力!!ソﾊﾝｶｸ",
]

data_identity += map(lambda x: x[0], String._lisp_quoted_specials)
data_identity += map(lambda x: x[1], String._lisp_quoted_specials)


def test_identity():
    for data in data_identity:
        assert parse(tosexp(data))[0] == data


def test_identity_pretty_print():
    for data in data_identity:
        assert parse(tosexp(data, pretty_print=True))[0] == data


class BaseTestCase(unittest.TestCase):
    def assert_parse(self, string, obj):
        """`string` must be parsed into `obj`."""
        self.assertEqual(parse(string)[0], obj)


class TestSymbol(BaseTestCase):
    def test_parse_symbol_with_backslash(self):
        self.assert_parse(r"path.join", Symbol(r"path.join"))
        self.assert_parse(r"path\ join", Symbol(r"path join"))
        self.assert_parse(r"path\\join", Symbol(r"path\join"))

    def test_parse_special_symbols(self):
        for s in [
            r"\\",
            r"\'",
            r"\`",
            r"\"",
            r"\(",
            r"\)",
            r"\[",
            r"\]",
            r"\ ",
            r"\.",
            r"\,",
            r"\?",
            r"\;",
            r"\#",
        ]:
            self.assert_parse(s, Symbol(Symbol.unquote(s)))

    def test_hashable_and_distinct(self):
        d = {
            String("A"): "StrA",
            Symbol("A"): "SymA",
            "A": "strA",
        }
        self.assertEqual(3, len(d))
        self.assertEqual("StrA", d[String("A")])
        self.assertEqual("SymA", d[Symbol("A")])
        self.assertEqual("strA", d["A"])


class TestParseFluctuation(BaseTestCase):
    def test_spaces_must_be_ignored(self):
        self.assert_parse(
            " \n\t\r  ( ( a )  \t\n\r  ( b ) )  ", [[Symbol("a")], [Symbol("b")]]
        )

    def test_spaces_between_parentheses_can_be_skipped(self):
        self.assert_parse("((a)(b))", [[Symbol("a")], [Symbol("b")]])

    def test_spaces_between_double_quotes_can_be_skipped(self):
        self.assert_parse('("a""b")', ["a", "b"])


class TestDeliminter(BaseTestCase):
    def test_normal(self):
        """
        When the brace subclass does not exist, brace should be parsed as alphanumeric
        """
        import gc

        gc.collect()
        self.assertEqual(Delimiters.get_brackets(), {"(": ")", "[": "]"})
        self.assertEqual(parse("{a b c}"), [Symbol("{a"), Symbol("b"), Symbol("c}")])

    def test_curly_brace(self):
        """
        Extending the delimiters using braces
        """

        class Braces(Delimiters):
            opener, closer = "{", "}"

        self.assertEqual(Delimiters.get_brackets(), {"(": ")", "[": "]", "{": "}"})

        self.assert_parse("[a b c]", Brackets([Symbol("a"), Symbol("b"), Symbol("c")]))
        self.assert_parse("{a b c}", Braces([Symbol("a"), Symbol("b"), Symbol("c")]))

    def test_multiple_brackets(self):
        """
        Extending the delimiters using braces and unicode braces
        """

        class Implicit(Delimiters):
            opener, closer = "{", "}"

        class StrictImplicit(Delimiters):
            opener, closer = "⦃", "⦄"

        target = "{σ : Type u} → {m : Type u → Type v} → [inst : Functor m] → ⦃α : Type u⦄ → StateT σ m α → σ → m α"
        self.assertEqual(
            Delimiters.get_brackets(), {"(": ")", "[": "]", "{": "}", "⦃": "⦄"}
        )

        self.assertEqual(
            parse(target),
            [
                Implicit([Symbol("σ"), Symbol(":"), Symbol("Type"), Symbol("u")]),
                Symbol("→"),
                Implicit(
                    [
                        Symbol("m"),
                        Symbol(":"),
                        Symbol("Type"),
                        Symbol("u"),
                        Symbol("→"),
                        Symbol("Type"),
                        Symbol("v"),
                    ]
                ),
                Symbol("→"),
                Brackets([Symbol("inst"), Symbol(":"), Symbol("Functor"), Symbol("m")]),
                Symbol("→"),
                StrictImplicit([Symbol("α"), Symbol(":"), Symbol("Type"), Symbol("u")]),
                Symbol("→"),
                Symbol("StateT"),
                Symbol("σ"),
                Symbol("m"),
                Symbol("α"),
                Symbol("→"),
                Symbol("σ"),
                Symbol("→"),
                Symbol("m"),
                Symbol("α"),
            ],
        )


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
    assert tosexp("a", str_as="symbol") == "a"
    assert tosexp(["a"], str_as="symbol") == "(a)"
    assert tosexp("a") == '"a"'
    assert tosexp(["a"]) == '("a")'
    assert tosexp(Quoted("a")) == '\'"a"'
    assert tosexp(Quoted(["a"]), str_as="symbol") == "'(a)"
    assert tosexp([Quoted("a")], str_as="symbol") == "('a)"
    assert tosexp(Quoted("a"), str_as="symbol") == "'a"
    assert tosexp(Quoted(["a"])) == '\'("a")'
    assert tosexp([Quoted("a")]) == '(\'"a")'


def test_tosexp_tuple_as():
    assert tosexp(("a", "b")) == '("a" "b")'
    assert tosexp(("a", "b"), tuple_as="array") == '["a" "b"]'
    assert tosexp([("a", "b")]) == '(("a" "b"))'
    assert tosexp([("a", "b")], tuple_as="array") == '(["a" "b"])'
    assert tosexp(Quoted(("a",))) == '\'("a")'
    assert tosexp(Quoted(("a",)), tuple_as="array") == '\'["a"]'


def test_tosexp_value_errors():
    with pytest.raises(ValueError):
        tosexp((), tuple_as="")
    with pytest.raises(ValueError):
        tosexp("", str_as="")
    with pytest.raises(ValueError):
        tosexp(Parens())


def test_parse_float():
    assert parse("-1.012") == [-1.012]
    assert parse("2E22") == [2e22]
    assert parse("inf") == [Symbol("inf")]
    # Values chosen from floating point examples on Wikipedia
    assert parse("-0.0") == [-0.0]
    assert parse("6.28318") == [6.28318]
    assert parse("6.022e23") == [6.022e23]
    assert parse("5E888720") == [Symbol("5E888720")]


def test_too_many_brackets():
    with pytest.raises(ExpectNothing):
        parse("(a b))")


def test_not_enough_brackets():
    with pytest.raises(ExpectClosingBracket):
        parse("(a (b)")


def test_no_eol_after_comment():
    assert parse("a ; comment") == [Symbol("a")]


def test_issue_4():
    assert parse("(0 ;; (\n)") == [[0]]
    assert parse("(0;; (\n)") == [[0]]


def test_issue_18():
    import sexpdata

    sexp = "(foo)'   "
    with pytest.raises(ExpectSExp, match="No s-exp is found after an apostrophe"):
        sexpdata.parse(sexp)

    sexp = "'   "
    with pytest.raises(ExpectSExp, match="No s-exp is found after an apostrophe"):
        sexpdata.parse(sexp)


def test_other_issue_18():
    import sexpdata

    sexp = b"(foo)'   "
    with pytest.raises(AssertionError):
        sexpdata.loads(sexp)


def test_issue_37_value_field():
    assert String("ObjStr").value() == "ObjStr"
    assert Symbol("ObjSym").value() == "ObjSym"
    assert Symbol("ObjList").value() == "ObjList"


def test_malformed_unclosed_string():
    import sexpdata

    with pytest.raises(UnterminatedString):
        sexpdata.loads('"asdf')


def test_malformed_invalid_escape():
    import sexpdata

    with pytest.raises(InvalidEscape):
        sexpdata.loads("\\")


def test_unterminated_string_position():
    """Test that UnterminatedString errors report correct position."""
    import sexpdata

    # Simple case at start of line
    with pytest.raises(UnterminatedString) as exc_info:
        sexpdata.loads('"asdf')
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 1

    # Case with content before
    with pytest.raises(UnterminatedString) as exc_info:
        sexpdata.loads('(a "asdf')
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 4


def test_invalid_escape_position():
    """Test that InvalidEscape errors report correct position."""
    import sexpdata

    # Lone backslash at start
    with pytest.raises(InvalidEscape) as exc_info:
        sexpdata.loads("\\")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 1

    # Invalid escape in atom (backslash at end)
    with pytest.raises(InvalidEscape) as exc_info:
        sexpdata.loads("test\\")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 5


def test_expect_closing_bracket_position():
    """Test that ExpectClosingBracket errors report correct position."""
    import sexpdata

    # Missing closing bracket
    with pytest.raises(ExpectClosingBracket) as exc_info:
        sexpdata.loads("(a b")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 1


def test_expect_sexp_position():
    """Test that ExpectSExp errors report correct position."""
    import sexpdata

    # Quote without following expression
    with pytest.raises(ExpectSExp) as exc_info:
        sexpdata.loads("'")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 1

    # Quote at end of expression
    with pytest.raises(ExpectSExp) as exc_info:
        sexpdata.loads("(a b)'")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 6


def test_multiline_position_tracking():
    """Test position tracking across multiple lines."""
    import sexpdata

    multiline_input = """(first line
second "unterminated"""

    with pytest.raises(UnterminatedString) as exc_info:
        sexpdata.loads(multiline_input)
    assert exc_info.value.position.line == 2
    assert exc_info.value.position.column == 8

    # Test with more complex multiline structure
    complex_input = """(
  (nested
    (deeply "unterminated"""

    with pytest.raises(UnterminatedString) as exc_info:
        sexpdata.loads(complex_input)
    assert exc_info.value.position.line == 3
    assert exc_info.value.position.column == 13


def test_position_object():
    """Test Position object functionality."""
    pos = Position(3, 15, 42)
    assert pos.line == 3
    assert pos.column == 15
    assert pos.offset == 42
    assert str(pos) == "line 3, column 15"
    assert repr(pos) == "Position(line=3, column=15)"


def test_mismatched_brackets_position():
    """Test position tracking for mismatched bracket types."""
    import sexpdata

    # Opening with ( but closing with ]
    with pytest.raises(ExpectClosingBracket) as exc_info:
        sexpdata.loads("(a b]")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 1

    # Opening with [ but closing with )
    with pytest.raises(ExpectClosingBracket) as exc_info:
        sexpdata.loads("[a b)")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 1

    # Nested mismatched brackets
    with pytest.raises(ExpectClosingBracket) as exc_info:
        sexpdata.loads("(outer [inner)")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 8


def test_too_many_closing_brackets_position():
    """Test position tracking for ExpectNothing (too many closing brackets)."""
    import sexpdata

    # Extra closing bracket at end
    with pytest.raises(ExpectNothing) as exc_info:
        sexpdata.loads("(a b))")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 6

    # Multiple extra closing brackets
    with pytest.raises(ExpectNothing) as exc_info:
        sexpdata.loads("(test)]")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 7

    # Extra bracket after valid expression
    with pytest.raises(ExpectNothing) as exc_info:
        sexpdata.loads("valid ]")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 7


def test_nested_bracket_errors_position():
    """Test position tracking in deeply nested bracket errors."""
    import sexpdata

    # Multiple levels of unclosed brackets
    with pytest.raises(ExpectClosingBracket) as exc_info:
        sexpdata.loads("(level1 (level2 (level3")
    assert exc_info.value.position.line == 1
    assert (
        exc_info.value.position.column == 17
    )  # Reports the innermost unclosed bracket

    # Mixed bracket types in deep nesting
    with pytest.raises(ExpectClosingBracket) as exc_info:
        sexpdata.loads("(round [square (round")
    assert exc_info.value.position.line == 1
    assert (
        exc_info.value.position.column == 16
    )  # Position of innermost unclosed bracket


def test_complex_multiline_errors():
    """Test position tracking in complex multiline scenarios."""
    import sexpdata

    # Error in middle of complex structure
    multiline_complex = """(
  (define function
    (lambda (x y)
      (if (> x y
        (* x y)
        (+ x y))))
  (another "unterminated)"""

    with pytest.raises(UnterminatedString) as exc_info:
        sexpdata.loads(multiline_complex)
    assert exc_info.value.position.line == 7
    assert exc_info.value.position.column == 12

    # Bracket mismatch in multiline
    multiline_brackets = """(
  (first-expr)
  [second-expr
    (nested)
  )  ; Wrong closing bracket
"""

    with pytest.raises(ExpectClosingBracket) as exc_info:
        sexpdata.loads(multiline_brackets)
    assert exc_info.value.position.line == 3
    assert exc_info.value.position.column == 3


def test_edge_case_positions():
    """Test position tracking for edge cases."""
    import sexpdata

    # Quote at very end of line with newline
    with pytest.raises(ExpectSExp) as exc_info:
        sexpdata.loads("(valid expression)'\n")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 19

    # Error after whitespace and comments
    with pytest.raises(UnterminatedString) as exc_info:
        sexpdata.loads('  ; comment\n   "unterminated')
    assert exc_info.value.position.line == 2
    assert exc_info.value.position.column == 4

    # Escape error in different contexts
    with pytest.raises(InvalidEscape) as exc_info:
        sexpdata.loads("(before after\\")
    assert exc_info.value.position.line == 1
    assert exc_info.value.position.column == 14


def test_string_equality_permutations():
    """Test that String, Symbol, and str objects have distinct equality."""
    S = "a", String("a"), Symbol("a")

    assert String("a") == String("a")
    assert Symbol("a") == Symbol("a")

    assert Symbol("a") != String("a")

    assert String("a") != "a"
    assert Symbol("a") != "a"


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="match/case requires Python 3.10+"
)
def test_symbol_match_case():
    """Test that Symbol objects work with match/case syntax."""
    result = None

    # Test matching against Symbol type
    symbol_obj = Symbol("asdf")
    match symbol_obj:
        case Symbol() if symbol_obj == Symbol("asdf"):
            result = 1
        case _:
            result = 0

    assert result == 1

    # Test symbol matching with different string values
    other_symbol = Symbol("other")
    match other_symbol:
        case Symbol() if other_symbol == Symbol("asdf"):
            result = 0
        case Symbol() if other_symbol == Symbol("other"):
            result = 2
        case _:
            result = -1

    assert result == 2

    # Test general Symbol type matching
    test_symbol = Symbol("test")
    match test_symbol:
        case Symbol():
            result = str(test_symbol)
        case _:
            result = None

    assert result == "test"


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="match/case requires Python 3.10+"
)
def test_symbol_match_case_user_supplied():

    # Test derived from in issue #58
    matched = False
    match String("asdf"):
        case String("asdf"):
            matched = True
    assert matched

    # Test example in issue #58
    matched = False
    match Symbol("asdf"):
        case Symbol("asdf"):
            matched = True
    assert matched
