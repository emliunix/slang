from slang.slr_impl import apply_tranx
from slang.stlc.lexer import lex
from slang.stlc.grammar import mk_grammar
from slang.stlc.syntax import Arrow, Term, Unit, UnitTy, VarStr, Var, Lam, to_dbi
from slang.stlc.evaluate import EmptyEnv, EvalException, StopEvalException, TypeException, type_of, evaluate, CEK
from unittest.case import TestCase

class TestSTLCEvaluate(TestCase):
    def setUp(self):
        self.g = mk_grammar()

    def parse(self, s: str) -> Term:
        return to_dbi(apply_tranx(self.g.parse(iter(lex(s.replace("/", "\\"))))))

    @staticmethod
    def cek_eval(t: Term, max_steps=10000) -> Term:
        cek = CEK(t)
        try:
            for i in range(max_steps):
                cek.step()
        except StopEvalException:
            return cek.c
        raise EvalException("maybe loop in input or cek bug")

    def test_type_of(self):
        assert type_of(Unit(), EmptyEnv()) == UnitTy()

    def test_type_of_abs(self):
        t = Lam("x", Arrow(UnitTy(), UnitTy()), VarStr("x"))
        t = to_dbi(t)
        _tmp = self.parse("/x:(0->0)->0->0.x")
        if isinstance(_tmp, Lam):
            assert type_of(t, EmptyEnv()) == _tmp.ty
        else:
            assert False

    def test_type_of_app(self):
        t = self.parse("(/x:0->0.x)(/x:0.x)")
        _tmp = self.parse("/x:0->0.x")
        if isinstance(_tmp, Lam):
            assert type_of(t, EmptyEnv()) == _tmp.ty
        else:
            assert False

    def test_type_of_exc_1(self):
        with self.assertRaises(TypeException):
            type_of(self.parse("(/x:0->0.x)0"), EmptyEnv())

    def test_eval_1(self):
        t = self.parse("(/x:0.x)0")
        t2 = self.parse("0")
        t3 = evaluate(t, EmptyEnv())
        assert t2 == t3

    def test_eval_2(self):
        assert evaluate(self.parse("(/x:0->0.x)(/x:0.0)"), EmptyEnv()) == self.parse("(/x:0.0)")

    def test_cek_eval_1(self):
        t = self.parse("(/x:0->0.x)(/x:0.0)")
        cek = CEK(t)
        try:
            with self.assertRaises(StopEvalException):
                while True:
                    cek.step()
        except:
            pass
        assert cek.c == self.parse("(/x:0.0)")

    def test_cek_eval_2(self):
        assert self.cek_eval(self.parse("0")) == self.parse("0")
        assert self.cek_eval(self.parse("(/x:0->0.x 0)(/x:0.0)")) == self.parse("0")
        # assert self.cek_eval(self.parse("0")) == self.parse("0")
