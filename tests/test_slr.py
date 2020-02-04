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
            (G, [S, EOF]),
            (S, [S, PLUS, P]),
            (S, [P]),
            (P, [P, MUL, V]),
            (P, [V]),
            (V, [LPAREN, S, RPAREN]),
            (V, [VAL]),
        ], ArithMatcher())
        g.print_states()
        g.print_parsing_table()
        print_parsed(g.parse(iter(arith)))
