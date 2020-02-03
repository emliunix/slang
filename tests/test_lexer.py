from slang.lexer import (
    parse,
    Token, LAM, DOT, COLON, LPAREN, RPAREN, VAR
)

def test_parse():
    r = parse("""(\\x:t.x)y""")
    assert(r == [LPAREN, LAM, VAR("x"), COLON, VAR("t"), DOT, VAR("x"), RPAREN, VAR("y")])
