import re

from functools import partial
from dataclasses import dataclass
from slang.lexer import lex as _lex
from slang.nicetoken import Token

@dataclass
class FORALL(Token): ...
@dataclass
class LAMBDA(Token): ...
@dataclass
class COLON(Token): ...
@dataclass
class DOT(Token): ...
@dataclass
class LPAREN(Token): ...
@dataclass
class RPAREN(Token): ...
@dataclass
class LSQPAREN(Token): ...
@dataclass
class RSQPAREN(Token): ...
@dataclass
class ARROW(Token): ...
@dataclass
class UNIT(Token): ...
@dataclass
class IDENT(Token):
    s: str

LEX_DEF = [
    (r"\s+",       lambda o, _:  None                      ),
    (r"/",         lambda o, _:  o.append(LAMBDA()        )),
    (r"@",         lambda o, _:  o.append(FORALL()        )),
    (r"\.",        lambda o, _:  o.append(DOT()           )),
    (r":",         lambda o, _:  o.append(COLON()         )),
    (r"->",        lambda o, _:  o.append(ARROW()         )),
    (r"\(",        lambda o, _:  o.append(LPAREN()        )),
    (r"\)",        lambda o, _:  o.append(RPAREN()        )),
    (r"\[",        lambda o, _:  o.append(LSQPAREN()      )),
    (r"\]",        lambda o, _:  o.append(RSQPAREN()      )),
    (r"0",         lambda o, _:  o.append(UNIT()          )),
    (r"[a-zA-Z]+", lambda o, r:  o.append(IDENT(r.group()))),
]

lex = partial(_lex, [(re.compile(p), f) for (p, f) in LEX_DEF])
