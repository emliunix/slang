import re

from typing import List, Tuple, TypeVar, Callable

TToken = TypeVar("Token")
LexDef = List[Tuple[re.Pattern, Callable[[List[TToken], re.Match], None]]]

def lex(lex_def: LexDef, s: str) -> List[TToken]:
    tokens : List[Token] = []
    r = None
    while s != "":
        for (pat, proc) in lex_def:
            if r := pat.match(s):
                proc(tokens, r)
                break
        if not r:
            break
        s = s[r.end():]
    return tokens
