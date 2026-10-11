import sympy as sp
import pytest
from geometry_extension.constraints import ConstraintSystem


def test_substitution_and_minimum():
    x, y = sp.symbols("x y")
    system = ConstraintSystem((x, y), objective=x*x+y*y)
    system.substitute(y, 2*x+1)
    assert sp.expand(system.reduced(system.objective)) == 5*x*x+4*x+1
    result = system.minimize([0.0])
    assert result.success
    assert result.x[0] == pytest.approx(-0.4, abs=1e-5)


def test_equalities_and_mutation():
    x, y = sp.symbols("x y")
    system = ConstraintSystem((x, y))
    eq = sp.Eq(x+y, 3)
    system.add(eq).add(sp.Eq(x-y, 1))
    assert system.solve_equalities() == [{x: 2, y: 1}]
    system.remove(eq)
    assert len(system.constraints) == 1


def test_inequality():
    x = sp.symbols("x")
    system = ConstraintSystem((x,), objective=(x-3)**2)
    system.add(sp.Le(x, 1))
    assert system.feasible({x: 0})
    assert not system.feasible({x: 2})
    result = system.minimize([0.0])
    assert result.success
    assert result.x[0] == pytest.approx(1.0, abs=1e-5)


def test_strict_inequality_rejected_numerically():
    x = sp.symbols("x")
    system = ConstraintSystem((x,), objective=x*x).add(sp.Lt(x, 1))
    with pytest.raises(ValueError, match="Strict inequalities"):
        system.minimize([0.0])
