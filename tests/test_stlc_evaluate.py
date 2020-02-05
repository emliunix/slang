from slang.stlc.syntax import Arrow, Unit, UnitTy, VarStr, Var, Lam, to_dbi
from slang.stlc.evaluate import EmptyEnv, type_of
from unittest.case import TestCase

class TestSTLCEvaluate(TestCase):
    def test_type_of(self):
        assert type_of(Unit(), EmptyEnv()) == UnitTy()

    def test_type_of_2(self):
        t = Lam("x", Arrow(UnitTy(), UnitTy()), VarStr("x"))
        t = to_dbi(t)
        assert type_of(t, EmptyEnv()) == Arrow(Arrow(UnitTy(), UnitTy()), Arrow(UnitTy(), UnitTy()))
