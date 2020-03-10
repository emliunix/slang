from dataclasses import dataclass
from typing import List, TypeVar

# type language

@dataclass
class Ty(object): ...

@dataclass
class TVar(Ty):
    name: str

@dataclass
class TVarI(Ty):
    i: int

@dataclass
class Arrow(Ty):
    t1: Ty
    t2: Ty

@dataclass
class Forall(Ty):
    var: str
    body: Ty

@dataclass
class UnitTy(Ty): ...

@dataclass
class Type(Ty):
    """
    The type of type, currently only used by typechecker,
    in Binding, reresenting a bind of type (Forall)
    """
    pass

# term language

@dataclass
class Term(object): ...

@dataclass
class Abs(Term):
    var: str
    ty: Ty
    body: Term

@dataclass
class App(Term):
    t1: Term
    t2: Term

@dataclass
class TAbs(Term):
    var: str
    body: Term

@dataclass
class TApp(Term):
    t: Term
    ty: Ty

@dataclass
class Var(Term):
    name: str

@dataclass
class VarI(Term):
    i: int

@dataclass
class Unit(Term): ...

T = TypeVar("T")

def stack_index(l: List[T], e: T) -> int:
    for i in range(len(l)):
        if l[len(l)-1-i] == e:
            return i
    return -1

def _to_dbi_ty(t: Ty, stack: List[str]) -> Ty:
    if isinstance(t, Forall):
        stack.append(t.var)
        tmp = _to_dbi_ty(t.body, stack)
        stack.pop()
        return Forall(t.var, tmp)
    elif isinstance(t, Arrow):
        return Arrow(_to_dbi_ty(t.t1, stack), _to_dbi_ty(t.t2, stack))
    elif isinstance(t, UnitTy):
        return t
    elif isinstance(t, TVar):
        return TVarI(stack_index(stack, t.name))
    else:
        assert False, f"unhandled type: {t}"

def _to_dbi(t: Term, stack: List[str]) -> Term:
    if isinstance(t, TAbs):
        stack.append(t.var)
        tmp = _to_dbi(t.body, stack)
        stack.pop()
        return TAbs(t.var, tmp)
    elif isinstance(t, TApp):
        return TApp(
            _to_dbi(t.t, stack),
            _to_dbi_ty(t.ty, stack),
        )
    elif isinstance(t, Abs):
        tmp_ty = _to_dbi_ty(t.ty, stack)
        stack.append(t.var)
        tmp = _to_dbi(t.body, stack)
        stack.pop()
        return Abs(t.var, tmp_ty, tmp)
    elif isinstance(t, App):
        return App(
            _to_dbi(t.t1, stack),
            _to_dbi(t.t2, stack),
        )
    elif isinstance(t, Unit):
        return t
    elif isinstance(t, Var):
        return VarI(stack_index(stack, t.name))
    else:
        assert False, f"unhandled term: {t}"

def to_dbi(t: Term) -> Term:
    stack = []
    return _to_dbi(t, stack)
