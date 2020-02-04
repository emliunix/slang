from unittest.case import TestCase

from slang.stlc.syntax import Var, VarStr, Lam, App, to_dbi

class TestSTLCSyntax(TestCase):
    def test_to_dbi(self):
        t1 = App(Lam("x", App(VarStr("x"), VarStr("x"))), Lam("x", App(VarStr("x"), VarStr("x"))))
        t2 = App(Lam("x", App(Var(0), Var(0))), Lam("x", App( Var(0),  Var(0))))
        assert to_dbi(t1) == t2

    def test_to_dbi_2(self):
        t1 = App(Lam("x", Lam("y", VarStr("x"))), Lam("x", VarStr("x")))
        t2 = App(Lam("x", Lam("y", Var(1))), Lam("x", Var(0)))
        assert to_dbi(t1) == t2
