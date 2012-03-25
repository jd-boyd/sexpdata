================================
 S-expression parser for Python
================================


>>> import sexpdata
>>> sexpdata.loads("(a b)")
[Symbol('a'), Symbol('b')]
>>> sexpdata.dumps([Symbol('a'), Symbol('b')])
'(a b)'
