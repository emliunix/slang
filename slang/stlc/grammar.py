from slang.slr import (
    EOF, Symbol, Terminal, NonTerminal,
    grammar, RightAssoc
)
from slang.stlc.syntax import Arrow, Unit, UnitTy
from slang.stlc.lexer import ARROW, Token as STLC_Token
from slang.stlc.lexer import (
    LAM,
    DOT,
    COLON,
    LPAREN,
    RPAREN,
    UNIT,
    VAR,
)
from . import syntax as Syn

def pick(i):
    def _pick_i(p):
        return p[i]
    return _pick_i

def mk_grammar():
    S  = NonTerminal("S")
    E  = NonTerminal("E")
    E1 = NonTerminal("E1")
    E2 = NonTerminal("E2")
    TY  = NonTerminal("TY")

    TLAM = Terminal("lambda")
    TCOLON = Terminal("colon")
    TDOT = Terminal("dot")
    TLPAREN = Terminal("(")
    TRPAREN = Terminal(")")
    TVAR = Terminal("var")
    TARROW = Terminal("->")
    TUNIT = Terminal("0")

    U = UnitTy()
    u = Unit()

    rules = [
        (S, [E, EOF], pick(0)),
        (E, [TLAM, TVAR, TCOLON, TY, TDOT, E1], lambda p: Syn.Lam(p[1].name, p[3], p[5])),
        (E, [E1], pick(0)),
        (E1, [E1, E2], lambda p: Syn.App(p[0], p[1])),
        (E1, [E2], pick(0)),
        (E2, [TVAR], lambda p: Syn.VarStr(p[0].name)),
        (E2, [TUNIT], lambda p: u),
        (E2, [TLPAREN, E, TRPAREN], pick(1)),
        (TY, [TY, TARROW, TY], lambda p: Arrow(p[0], p[2])),
        (TY, [TUNIT], lambda _: U),
        (TY, [TLPAREN, TY, TRPAREN], pick(1)),
    ]

    assoc_preceds = [
        (RightAssoc, [TARROW])
    ]

    class Matcher(object):
        def match(self, s: Symbol, t: STLC_Token):
            return (
                s == TLAM and t is LAM
                or s == TCOLON and t is COLON
                or s == TDOT and t is DOT
                or s == TLPAREN and t is LPAREN
                or s == TRPAREN and t is RPAREN
                or s == TVAR and isinstance(t, VAR)
                or s == TUNIT and t is UNIT
                or s == TARROW and t is ARROW
            )

    g = grammar(rules, assoc_preceds, Matcher())
    return g
