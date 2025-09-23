import unittest
from mortcalc.solvers import solve_bisection


class SolverTests(unittest.TestCase):
    def test_bisection_linear(self):
        f = lambda x: x - 2.0
        res = solve_bisection(f, 0.0, 5.0)
        self.assertTrue(res.converged)
        self.assertIsNotNone(res.root)
        self.assertAlmostEqual(res.root, 2.0, places=6)

    def test_bisection_no_sign_change(self):
        # f(x) = x + 1 is positive on [0, 1]
        f = lambda x: x + 1.0
        res = solve_bisection(f, 0.0, 1.0)
        self.assertFalse(res.converged)
        self.assertIsNone(res.root)


if __name__ == "__main__":
    unittest.main()
