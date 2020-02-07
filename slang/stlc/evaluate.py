from typing import Union, Tuple
from dataclasses import dataclass
from .syntax import Arrow, Ty, Term, Lam, Unit, UnitTy, Var, App

@dataclass
class Binding(object):
    name: str
    ty: Ty

class Env(object):
    def lookup(self, i: int) -> Binding:
        raise NotImplementedError()

class EmptyEnv(Env):
    def lookup(self, i: int) -> Binding:
        raise Exception("corrupted variable index")

@dataclass
class Env2(Env):
    var: Binding
    env: Env

    def lookup(self, i: int) -> Binding:
        if i == 0:
            return self.var
        else:
            return self.env.lookup(i - 1)

class TypeException(Exception):
    pass

def fmt_ty(t: Ty):
    if isinstance(t, UnitTy):
        return "0"
    elif isinstance(t, Arrow):
        if isinstance(t.src, Arrow):
            return F"({fmt_ty(t.src)}) -> {fmt_ty(t.dst)}"
        else:
            return F"{fmt_ty(t.src)} -> {fmt_ty(t.dst)}"
    else:
        raise TypeException(F"unknow type {type(t)}")

def type_of(t: Term, env: Env) -> Ty:
    if isinstance(t, Var):
        return env.lookup(t.i).ty
    elif isinstance(t, App):
        fty = type_of(t.f, env)
        argty = type_of(t.arg, env)
        if isinstance(fty, Arrow) and fty.src == argty:
            return fty.dst
        else:
            raise TypeException(F"type mismatch for App ({fmt_ty(fty)})({fmt_ty(argty)})")
    elif isinstance(t, Lam):
        env2 = Env2(Binding(t.var, t.ty), env)
        return Arrow(t.ty, type_of(t.term, env2))
    elif isinstance(t, Unit):
        return UnitTy()
    else:
        raise TypeException("Unknown type of term")

class StopEvalException(Exception):
    def __init__(self) -> None:
        super().__init__("Stop Eval")

def is_simple_value(t: Term):
    return not isinstance(t, App)

class EvalException(Exception):
    pass

def shift(t: Term, d: int, c=0) -> Term:
    """
    :param d: delta
    :param c: cutoff
    """
    if isinstance(t, Var):
        if t.i > c:
            return Var(t.i + d)
        else:
            return t
    elif isinstance(t, Lam):
        return Lam(t.var, t.ty, shift(t.term, d, c + 1))
    elif isinstance(t, App):
        return App(shift(t.f, d, c), shift(t.arg, d, c))
    elif isinstance(t, Unit):
        return t
    else:
        raise EvalException()

def subst(t1: Term, k: int, t2: Term) -> Term:
    if isinstance(t1, Var):
        if t1.i == k:
            return t2
        else:
            return t1
    elif isinstance(t1, Lam):
        return Lam(t1.var, t1.ty, subst(t1.term, k + 1, shift(t2, 1)))
    elif isinstance(t1, App):
        return App(subst(t1.f, k, t2), subst(t1.arg, k, t2))
    elif isinstance(t1, Unit):
        return t1
    else:
        raise EvalException()

def eval1(t: Term) -> Term:
    if isinstance(t, App):
        t1 = t.f
        t2 = t.arg
        if isinstance(t1, Lam) and is_simple_value(t2):
            return shift(subst(t1.term, 0, t2), -1)
        elif isinstance(t1, Lam):
            return App(t1, eval1(t2))
        else:
            return App(eval1(t1), t2)
    else:
        raise StopEvalException()

def evaluate(t: Term, env: Env) -> Term:
    try:
        while True:
            t = eval1(t)
    except StopEvalException:
        return t
