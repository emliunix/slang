
from slang.stlc.grammar import mk_grammar
from slang.stlc.syntax import VarStr, Lam, App
from slang.lexer import lex
from slang.slr import apply_tranx, print_parsed
from unittest.case import TestCase

class TestSTLCGrammar(TestCase):
    def test_g(self):
        mk_grammar()

    def test_parse(self):
        g = mk_grammar()
        toks = lex("(\\x.x x)(\\x.x x)")
        res = g.parse(iter(toks))
        print_parsed(res)

    def test_tranx(self):
        g = mk_grammar()
        toks = lex("(\\x.x x)(\\x.x x)")
        res = g.parse(iter(toks))
        assert apply_tranx(res) == App(Lam("x", App(VarStr('x'), VarStr('x'))), Lam("x", App(VarStr('x'), VarStr('x'))))
