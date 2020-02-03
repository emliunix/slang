from typing import Any, List, Union, Tuple

# types

class Ty(object): ...

class _UnitTy(Ty): ...

UnitTy = _UnitTy()

class ArrowTy(Ty):
    def __init__(self, t1: Ty, t2: Ty) -> None:
        self.t1 = t1
        self.t2 = t2

Binding = Tuple[str, Ty]
Context = List[Binding]

# Terms

class Term(object): ...        

class Var(Term):
    def __init__(self, idx: int) -> None:
        self.idx = idx

class Lam(Term):
    def __init__(self, var: str, ty: Ty, term: Term) -> None:
        self.var = var
        self.ty = ty
        self.term = term

class App(Term):
    def __init__(self, f: Term, arg: Term) -> None:
        self.f = f
        self.arg = arg

class _Unit(Term):
    def __init__(self) -> None:
        pass

Unit = _Unit()

class EvalException(Exception):
    pass

def subst(t: Term, val: Term, var: str) -> Term: ...

def evaluate(t: Term, ctx: Context) -> Term:
    if isinstance(t, App):
        x1 = evaluate(t.f, ctx)
        x2 = evaluate(t.arg, ctx)
        if not isinstance(x1, Lam):
            raise EvalException()
        return subst(x1.term, x2, x1.var)
    else:
        return t

evaluate(App(Lam("x", UnitTy, Var(0)), Unit), [])
