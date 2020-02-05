import re
from typing import List

RE_LAM = re.compile(R"\\")
RE_VAR = re.compile(R"\w+")
RE_DOT = re.compile(R"\.")
RE_COLON = re.compile(R":")
RE_LPAREN = re.compile(R"\(")
RE_RPAREN = re.compile(R"\)")
RE_UNIT = re.compile(R"0")
RE_BLANK = re.compile(R"\s+")
RE_ARROW = re.compile(R"->")

class Token(object):
    def __init__(self, repr_str: str) -> None:
        self.REPR = repr_str
    
    def __str__(self) -> str:
        return self.REPR

    def __repr__(self) -> str:
        return self.REPR

LAM = Token("LAM")
DOT = Token("DOT")
COLON = Token("COLON")
LPAREN = Token("LPAREN")
RPAREN = Token("RPAREN")
UNIT = Token("UNIT")
DOT = Token("DOT")
ARROW = Token("ARROW")

class VAR(Token):
    def __init__(self, name: str) -> None:
        super().__init__(F"VAR({name})")
        self.name = name

    def __eq__(self, o: object) -> bool:
        if isinstance(o, VAR):
            return self.name == o.name
        else:
            return False

def lex(s: str) -> List[Token]:
    tokens : List[Token] = []
    r = None
    while s != "":
        defs = [
            (RE_LAM, lambda toks, r: toks.append(LAM)),
            (RE_VAR, lambda toks, r: toks.append(VAR(r.group()))),
            (RE_DOT, lambda toks, r: toks.append(DOT)),
            (RE_COLON, lambda toks, r: toks.append(COLON)),
            (RE_LPAREN, lambda toks, r: toks.append(LPAREN)),
            (RE_RPAREN, lambda toks, r: toks.append(RPAREN)),
            (RE_UNIT, lambda toks, r: toks.append(UNIT)),
            (RE_ARROW, lambda toks, r: toks.append(ARROW)),
            (RE_BLANK, lambda toks, r: None),
        ]

        for (pat, proc) in defs:
            if r := pat.match(s):
                proc(tokens, r)
                break
        if not r:
            break
        s = s[r.end():]
    return tokens
