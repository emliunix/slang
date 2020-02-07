import unittest
from slang.stlc.lexer import (
    lex,
    Token, LAM, DOT, COLON, LPAREN, RPAREN, VAR
)

class TestLexer(unittest.TestCase):
    def test_parse(self):
        r = lex("""(\\x:t.x)y""")
        assert(r == [LPAREN, LAM, VAR("x"), COLON, VAR("t"), DOT, VAR("x"), RPAREN, VAR("y")])
