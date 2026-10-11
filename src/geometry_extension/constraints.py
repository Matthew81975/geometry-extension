"""Symbolic constraints and numerical optimization utilities."""
from dataclasses import dataclass, field
from typing import Sequence
import sympy as sp


@dataclass
class ConstraintSystem:
    """A mutable system of substitutions, equalities and inequalities."""
    variables: Sequence[sp.Symbol]
    objective: sp.Expr | None = None
    substitutions: dict = field(default_factory=dict)
    constraints: list = field(default_factory=list)

    def substitute(self, symbol, expression):
        if symbol not in self.variables:
            raise ValueError("Substitution symbol must be a declared variable")
        self.substitutions[symbol] = sp.sympify(expression)
        return self

    def add(self, relation):
        relation = sp.sympify(relation)
        if not isinstance(relation, sp.core.relational.Relational):
            raise TypeError("Expected Eq, Ne, Lt, Le, Gt or Ge")
        self.constraints.append(relation)
        return self

    def remove(self, relation):
        self.constraints.remove(relation)
        return self

    def reduced(self, expression):
        """Apply substitutions simultaneously (not recursively)."""
        return sp.sympify(expression).subs(self.substitutions, simultaneous=True)

    @property
    def free_variables(self):
        return tuple(v for v in self.variables if v not in self.substitutions)

    def feasible(self, values):
        """Check a fully specified assignment; undecidable symbolic cases raise."""
        assignment = {**self.substitutions, **values}
        for relation in self.constraints:
            result = sp.simplify(self.reduced(relation).subs(values))
            if result == sp.false:
                return False
            if result != sp.true:
                raise ValueError(f"Constraint not numerically decidable: {result}")
        return True

    def solve_equalities(self):
        equations = [self.reduced(c) for c in self.constraints
                     if isinstance(c, sp.Equality)]
        if not equations:
            return []
        return sp.solve(equations, self.free_variables, dict=True)

    def minimize(self, initial, *, bounds=None, method="SLSQP"):
        """Minimize with SciPy; strict inequalities are unsupported numerically."""
        import numpy as np
        from scipy.optimize import minimize
        if self.objective is None:
            raise ValueError("An objective is required")
        variables = self.free_variables
        if len(initial) != len(variables):
            raise ValueError("Initial point length does not match free variables")
        if len(variables) == 0:
            raise ValueError("No free variables")
        expr = self.reduced(self.objective)
        fun = sp.lambdify(variables, expr, "numpy")
        scipy_constraints = []
        for relation in self.constraints:
            c = self.reduced(relation)
            if isinstance(c, sp.Equality):
                residual, kind = c.lhs - c.rhs, "eq"
            elif isinstance(c, (sp.GreaterThan, sp.StrictGreaterThan)):
                if isinstance(c, sp.StrictGreaterThan):
                    raise ValueError("Strict inequalities require an explicit margin")
                residual, kind = c.lhs - c.rhs, "ineq"
            elif isinstance(c, (sp.LessThan, sp.StrictLessThan)):
                if isinstance(c, sp.StrictLessThan):
                    raise ValueError("Strict inequalities require an explicit margin")
                residual, kind = c.rhs - c.lhs, "ineq"
            else:
                raise ValueError("Unsupported numerical relation")
            compiled = sp.lambdify(variables, residual, "numpy")
            scipy_constraints.append({"type": kind, "fun": lambda x, f=compiled: float(f(*x))})
        result = minimize(lambda x: float(fun(*x)), np.asarray(initial, dtype=float),
                          method=method, bounds=bounds, constraints=scipy_constraints)
        return result
