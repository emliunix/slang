from slang.slr_impl import apply_tranx
import unittest
from slang.sysf.lexer import (
    lex,
    Token, LAMBDA, DOT, COLON, LPAREN, RPAREN, IDENT
)
from slang.sysf.grammar import mk_grammar
from slang.sysf.syntax import to_dbi
from slang.sysf.typecheck import typeof

class TestLexer(unittest.TestCase):
    def test_lex(self):
        r = lex("""(/x:t.x)y""")
        assert(r == [
            LPAREN(), LAMBDA(), IDENT("x"), COLON(), IDENT("t"), DOT(),
            IDENT("x"), RPAREN(), IDENT("y")])

    def test_grammar(self):
        g = mk_grammar()

    def test_parse1(self):
        g = mk_grammar()
        res = g.parse(iter(lex("@T./x:T.x")))
        res2 = apply_tranx(res)
        print(res2)

    def test_parse2(self):
        g = mk_grammar()
        res = g.parse(iter(lex("(/id:@T.T->T.id[0]0)(@T./x:T.x)")))
        res2 = apply_tranx(res)
        print(res2)

def mk_parse():
    g = mk_grammar()

    def parse(s):
        res = g.parse(iter(lex(s)))
        res2 = apply_tranx(res)
        return res2

    return parse

def mk_parse_dbi():
    parse = mk_parse()
    return lambda s: to_dbi(parse(s))

class TestGrammar(unittest.TestCase):
    def setUp(self):
        self.parse = mk_parse()

    def test_tapp(self):
        self.parse("(/id:@T.T->T.id[0]0)(@T./x:T.x)")

class TestSyntax(unittest.TestCase):
    def setUp(self):
        self.parse = mk_parse_dbi()

    def test_to_dbi(self):
        print(self.parse("(/id:@T.T->T.id[0]0)(@T./x:T.x)"))

class TestTypeChecker(unittest.TestCase):
    def setUp(self):
        self.parse = mk_parse_dbi()

    def test_type_check_0(self):
        print(typeof(self.parse("(/id:@T.T->T.id[0]0)(@T./x:T.x)")))

    def test_type_check_1(self):
        print(typeof(self.parse("(@T./x:T.x)[0]")))

    def test_type_check_2(self):
        print(typeof(self.parse("(@T./x:T.x)[@T.T->T]")))

