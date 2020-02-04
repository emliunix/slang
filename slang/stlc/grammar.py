from ..slr import (
    EOF, Symbol, Terminal, NonTerminal,
    grammar
)

from ..lexer import Token as STLC_Token
from ..lexer import (
    LAM,
    DOT,
    COLON,
    LPAREN,
    RPAREN,
    UNIT,
    VAR,
)
from . import syntax as Syn

def identity(x):
    return x

def mk_grammar():
    S  = NonTerminal("S")
    E  = NonTerminal("E")
    E1 = NonTerminal("E1")
    E2 = NonTerminal("E2")

    TLAM = Terminal("lambda")
    TCOLON = Terminal("colon")
    TDOT = Terminal("dot")
    TLPAREN = Terminal("(")
    TRPAREN = Terminal(")")
    TVAR = Terminal("var")

    rules = [
        (S, [E, EOF], lambda e,_: e),
        (E, [TLAM, TVAR, TDOT, E1], lambda _1,v,_2,t: Syn.Lam(v.name, t)),
        (E, [E1], identity),
        (E1, [E1, E2], lambda e1,e2: Syn.App(e1, e2)),
        (E1, [E2], identity),
        (E2, [TVAR], lambda v: Syn.VarStr(v.name)),
        (E2, [TLPAREN, E, TRPAREN], lambda _1,e,_2: e),
    ]

    class Matcher(object):
        def match(self, s: Symbol, t: STLC_Token):
            return (
                s == TLAM and t is LAM or
                s == TCOLON and t is COLON or
                s == TDOT and t is DOT or
                s == TLPAREN and t is LPAREN or
                s == TRPAREN and t is RPAREN or
                s == TVAR and isinstance(t, VAR)
            )

    g = grammar(rules, Matcher())
    return g
