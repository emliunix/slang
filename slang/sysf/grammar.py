# flake8: noqa E221,E241

from dataclasses import dataclass
from slang.nicetoken import Matcher, TerminalOfToken, Token
from slang.slr import NonTerminal, EOF, grammar, RightAssoc

# from . import lexer as Lex
# from . import syntax as Syn
from slang.sysf import lexer as Lex
from slang.sysf import syntax as Syn
# from .lexer import (
#     FORALL, LAMBDA, IDENT, DOT, COLON,
#     LPAREN, RPAREN, LSQPAREN, RSQPAREN,
#     UNIT, ARROW,
# )

def pick(i):
    def _pick_i(p):
        return p[i]
    return _pick_i

def const(v):
    def _const(_):
        return v
    return _const

def mk_grammar():
    NT = NonTerminal
    T = TerminalOfToken
    M = Matcher()

    FORALL   = T("@",  Lex.FORALL)
    LAMBDA   = T("/",  Lex.LAMBDA)
    IDENT    = T("v",  Lex.IDENT)
    DOT      = T(".",  Lex.DOT)
    COLON    = T(":",  Lex.COLON)
    LPAREN   = T("(",  Lex.LPAREN)
    RPAREN   = T(")",  Lex.RPAREN)
    LSQPAREN = T("[",  Lex.LSQPAREN)
    RSQPAREN = T("]",  Lex.RSQPAREN)
    UNIT     = T("0",  Lex.UNIT)
    ARROW    = T("->", Lex.ARROW)

    U = Syn.UnitTy()
    u = Syn.Unit()

    S   = NT("S")
    E   = NT("E")
    E1  = NT("E1")
    ES  = NT("ES")
    TY  = NT("TY")
    TY1  = NT("TY1")
    TYS = NT("TYS")

    rules = [
        (S, [ ([E, EOF], pick(0)) ]),
        (E, [
            ([LAMBDA, IDENT, COLON, TY, DOT, E],
             lambda p: Syn.Abs(p[1].s, p[3], p[5])),
            ([FORALL, IDENT, DOT, E],
             lambda p: Syn.TAbs(p[1].s, p[3])),
            ([E1], pick(0)),
        ]),
        (E1, [
            ([E1, ES], lambda p: Syn.App(p[0], p[1])),
            ([E1, LSQPAREN, TY, RSQPAREN], lambda p: Syn.TApp(p[0], p[2])),
            ([ES], pick(0)),
        ]),
        (ES, [
            ([IDENT], lambda p: Syn.Var(p[0].s)),
            ([UNIT], const(u)),
            ([LPAREN, E, RPAREN], lambda p: p[1]),
        ]),
        (TY, [
            ([TY1], pick(0)),
            ([FORALL, IDENT, DOT, TY1], lambda p: Syn.Forall(p[1].s, p[3])),
        ]),
        (TY1, [
            ([TYS], pick(0)),
            ([TY1, ARROW, TY1], lambda p: Syn.Arrow(p[0], p[2])),
        ]),
        (TYS, [
            ([UNIT], const(U)),
            ([IDENT], lambda p: Syn.TVar(p[0].s)),
            ([LPAREN, TY, RPAREN], lambda p: p[1]),
        ]),
    ]
    rules = [(NT, sub[0], sub[1]) for (NT, subs) in rules for sub in subs]
    assoc_preceds = [
        (RightAssoc, [ARROW]),
    ]
    g = grammar(rules, assoc_preceds, M)
    return g
