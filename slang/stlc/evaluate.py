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
