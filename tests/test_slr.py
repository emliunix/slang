from slang.slr_impl import apply_tranx
from unittest.case import TestCase
from slang.slr import Symbol, grammar, EOF, Terminal, NonTerminal, print_parsed

G = NonTerminal("G")
S = NonTerminal("S")
P = NonTerminal("P")
F = NonTerminal("F")
V = NonTerminal("V")
PLUS = Terminal("+")
MUL = Terminal("x")
LPAREN = Terminal("(")
RPAREN = Terminal(")")
VAL = Terminal("val")

class ArithMatcher(object):
    def match(self, sym: Symbol, tok: str):
        return (
            sym == PLUS and tok == "+" or
            sym == MUL and tok == "x" or
            sym == LPAREN and tok == "(" or
            sym == RPAREN and tok == ")" or
            sym == VAL and tok.isdigit()
        )

class TestGrammar(TestCase):
    def test_grammar(self):
        arith = ["34", "+", "(", "12", "x", "(", "88", "+", "1", ")", ")"]
        g = grammar([
            (G, [S, EOF], lambda p: p[0]),
            (S, [S, PLUS, P], lambda p: ("+", p[0], p[2])),
            (S, [P], lambda p: p[0]),
            (P, [P, MUL, V], lambda p: ("x", p[0], p[2])),
            (P, [V], lambda p: p[0]),
            (V, [LPAREN, S, RPAREN], lambda p: p[1]),
            (V, [VAL], lambda p: int(p[0])),
        ], [], ArithMatcher())
        g.print_states()
        g.print_parsing_table()
        res = g.parse(iter(arith))
        # print_parsed(res)
        assert apply_tranx(res) == ("+", 34, ("x", 12, ("+", 88, 1)))
