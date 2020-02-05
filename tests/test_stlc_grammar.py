from slang.stlc.grammar import mk_grammar
from slang.stlc import grammar_ty as ty
from slang.stlc.syntax import Arrow, Unit, UnitTy, VarStr, Lam, App
from slang.stlc.lexer import lex
from slang.slr import apply_tranx, print_parsed
from unittest.case import TestCase

class TestSTLCGrammar(TestCase):
    def test_g(self):
        mk_grammar()

    def test_parse(self):
        g = mk_grammar()
        toks = lex("(\\x:0->0.x 0)(\\x:0.x)")
        res = g.parse(iter(toks))
        print_parsed(res)

    def test_tranx(self):
        g = mk_grammar()
        toks = lex("(\\x:0->0.x 0)(\\x:0.x)")
        res = g.parse(iter(toks))
        U = UnitTy()
        u = Unit()
        assert apply_tranx(res) == App(Lam("x", Arrow(U, U), App(VarStr('x'), u)), Lam("x", U, VarStr('x')))

    def test_ty(self):
        g = ty.mk_grammar()
        # g.print_states()
        # g.print_parsing_table()
        toks = lex("(0->0)->0->0")
        res = g.parse(iter(toks))
        U = UnitTy()
        assert apply_tranx(res) == Arrow(Arrow(U, U), Arrow(U, U))
