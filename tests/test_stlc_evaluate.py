from slang.slr_impl import apply_tranx
from slang.stlc.lexer import lex
from slang.stlc.grammar import mk_grammar
from slang.stlc.syntax import Arrow, Term, Unit, UnitTy, VarStr, Var, Lam, to_dbi
from slang.stlc.evaluate import EmptyEnv, TypeException, type_of
from unittest.case import TestCase

class TestSTLCEvaluate(TestCase):
    def setUp(self):
        self.g = mk_grammar()

    def parse(self, s: str) -> Term:
        return to_dbi(apply_tranx(self.g.parse(iter(lex(s)))))

    def test_type_of(self):
        assert type_of(Unit(), EmptyEnv()) == UnitTy()

    def test_type_of_abs(self):
        t = Lam("x", Arrow(UnitTy(), UnitTy()), VarStr("x"))
        t = to_dbi(t)
        _tmp = self.parse("\\x:(0->0)->0->0.x")
        if isinstance(_tmp, Lam):
            assert type_of(t, EmptyEnv()) == _tmp.ty
        else:
            assert False

    def test_type_of_app(self):
        t = self.parse("(\\x:0->0.x)(\\x:0.x)")
        _tmp = self.parse("\\x:0->0.x")
        if isinstance(_tmp, Lam):
            assert type_of(t, EmptyEnv()) == _tmp.ty
        else:
            assert False

    def test_type_of_exc_1(self):
        with self.assertRaises(TypeException):
            type_of(self.parse("(/x:0->0.x)0".replace("/", "\\")), EmptyEnv())
