from dataclasses import dataclass
from typing import List
from .syntax import (
    Term, Ty,
    Forall, Arrow, UnitTy, TVarI, Type,
    TAbs, TApp, Abs, App,
    Unit, VarI,
)

@dataclass
class Binding(object):
    name: str
    ty: Ty

class TypeCheckException(Exception): ...

def shift_ty_index(ty: Ty, base: int, delta: int) -> Ty:
    if isinstance(ty, Forall):
        return Forall(ty.var, shift_ty_index(ty.body, base+1, delta))
    elif isinstance(ty, Arrow):
        return Arrow(
            shift_ty_index(ty.t1, base, delta),
            shift_ty_index(ty.t2, base, delta),
        )
    elif isinstance(ty, UnitTy):
        return ty
    elif isinstance(ty, TVarI):
        return TVarI(ty.i + delta) if ty.i > base else ty
    else:
        raise TypeCheckException(f"unhandled type: {ty}")

def ty_subst(tf: Forall, ty: Ty) -> Ty:
    def _ty_subst(t: Ty, i: int) -> Ty:
        if isinstance(t, Forall):
            return Forall(t.var, _ty_subst(t.body, i+1))
        elif isinstance(t, Arrow):
            return Arrow(
                _ty_subst(t.t1, i),
                _ty_subst(t.t2, i),
            )
        elif isinstance(t, UnitTy):
            return t
        elif isinstance(t, TVarI):
            return shift_ty_index(ty, 0, i) if t.i == i else t
        else:
            assert False, f"unhandled type: {t}"
    return _ty_subst(tf.body, 0)

def _typeof(t: Term, stack: List[Binding]) -> Ty:
    if isinstance(t, TAbs):
        stack.append(Binding(t.var, Type()))
        tmp = _typeof(t.body, stack)
        stack.pop()
        return Forall(t.var, tmp)
    elif isinstance(t, TApp):
        ty1 = _typeof(t.t, stack)
        if not isinstance(ty1, Forall):
            raise TypeCheckException(f"only t:Forall allowed in type application")
        return ty_subst(ty1, t.ty)
    elif isinstance(t, Abs):
        stack.append(Binding(t.var, t.ty))
        ty_body = shift_ty_index(_typeof(t.body, stack), 0, -1)
        stack.pop()
        return Arrow(t.ty, ty_body)
    elif isinstance(t, App):
        ty1 = _typeof(t.t1, stack)
        ty2 = _typeof(t.t2, stack)
        if not (isinstance(ty1, Arrow) and ty1.t1 == ty2):
            raise TypeCheckException(f"{ty1} applied to {ty2}")
        return ty1.t2
    elif isinstance(t, Unit):
        return UnitTy()
    elif isinstance(t, VarI):
        return shift_ty_index(stack[-(t.i+1)].ty, 0, t.i)
    else:
        assert False, f"unhandled term: {t}"

def typeof(t: Term) -> Ty:
    return _typeof(t, [])
