from dataclasses import dataclass

class Term(object):
    pass

@dataclass
class VarStr(Term):
    name: str

@dataclass
class Var(Term):
    i: int

@dataclass
class Lam(Term):
    var: str
    term: Term

@dataclass
class App(Term):
    f: Term
    arg: Term

@dataclass
class _Unit(Term):
    pass

Unit = _Unit()

def to_dbi(t: Term):
    vars = ["u"]
    
    def rfind(vs, n):
        len_vs = len(vs)
        for i in range(len_vs):
            if vs[len_vs-i-1]== n:
                return i
        raise Exception(F"Unbound variable: {n}")

    def go(t: Term):
        if isinstance(t, VarStr):
            return Var(rfind(vars, t.name))
        elif isinstance(t, App):
            return App(go(t.f), go(t.arg))
        elif isinstance(t, Lam):
            vars.append(t.var)
            term = go(t.term)
            vars.pop()
            return Lam(t.var, term)
        else:
            raise Exception(F"Unknown term type: {type(t)}")
    return go(t)
