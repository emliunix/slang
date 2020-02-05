from unittest.case import TestCase

from slang.stlc.syntax import UnitTy, Var, VarStr, Lam, App, to_dbi, Term

def dbi_eq(t1: Term, t2: Term) -> bool:
    if isinstance(t1, App) and isinstance(t2, App):
        return dbi_eq(t1.f, t2.f) and dbi_eq(t2.arg, t2.arg)
    elif isinstance(t1, Lam) and isinstance(t2, Lam):
        return dbi_eq(t1.term, t2.term)
    elif isinstance(t1, Var) and isinstance(t2, Var):
        return t1 == t2
    else:
        return False

T_U = UnitTy()

class TestSTLCSyntax(TestCase):
    def test_to_dbi(self):
        t1 = App(Lam("x", T_U, App(VarStr("x"), VarStr("x"))), Lam("x", T_U, App(VarStr("x"), VarStr("x"))))
        t2 = App(Lam("x", T_U, App(Var(0), Var(0))), Lam("x", T_U, App(Var(0), Var(0))))
        assert to_dbi(t1) == t2

    def test_to_dbi_2(self):
        t1 = App(Lam("x", T_U, Lam("y", T_U, VarStr("x"))), Lam("x", T_U, VarStr("x")))
        t2 = App(Lam("x", T_U, Lam("y", T_U, Var(1))), Lam("x", T_U, Var(0)))
        assert to_dbi(t1) == t2

    def test_to_dbi_3(self):
        t1 = App(Lam("x", T_U, Lam("y", T_U, VarStr("x"))), Lam("x", T_U, VarStr("x")))
        t2 = App(Lam("i", T_U, Lam("z", T_U, VarStr("i"))), Lam("j", T_U, VarStr("j")))
        assert t1 != t2
        assert dbi_eq(to_dbi(t1), to_dbi(t2))
