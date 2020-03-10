from dataclasses import dataclass
from slang.slr import Terminal, Symbol

@dataclass
class Token(object): ...

class TerminalOfToken(Terminal):
    token: Token
    def __init__(self, s: str, token: Token):
        super().__init__(s)
        self.token = token

class Matcher(object):
    def match(self, s: Symbol, t: Token):
        return isinstance(s, TerminalOfToken) and isinstance(t, s.token)
