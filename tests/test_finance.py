import unittest

from mortcalc.finance import (
    pmt_from_balance,
    amortize_with_extra,
    fv_from_contributions,
    MortgageInputs,
    InvestmentInputs,
    simulate_prepay_equal_cashflow,
    simulate_invest_only,
)


class FinanceTests(unittest.TestCase):
    def test_pmt_example(self):
        # $100k, 6% APR, 360 months ≈ $599.55
        P = pmt_from_balance(100_000, 0.06, 360)
        self.assertAlmostEqual(P, 599.55, places=2)

    def test_amortization_monotonic(self):
        # Higher extra should pay off earlier and reduce interest
        B, apr, N = 200_000, 0.05, 360
        P = pmt_from_balance(B, apr, N)
        res0 = amortize_with_extra(B, apr, P, 0.0)
        res1 = amortize_with_extra(B, apr, P, 200.0)
        self.assertLess(res1.payoff_month, res0.payoff_month)
        self.assertLess(res1.interest_paid, res0.interest_paid)

    def test_fv_constant_contrib_closed_form(self):
        # Closed-form: FV = C * [((1+r)^n - 1)/r] for constant C and monthly r
        C, r, n = 500.0, 0.005, 240
        fv_loop = fv_from_contributions([C] * n, r)
        fv_closed = C * (((1 + r) ** n - 1.0) / r)
        self.assertAlmostEqual(fv_loop, fv_closed, places=6)

    def test_equal_cashflow_brackets_solution(self):
        # Ensure the equal-cashflow function changes sign across E in [0, M]
        mort = MortgageInputs(balance=350_000, apr=0.065, months=324)
        invest = InvestmentInputs(monthly_return=(1 + 0.10) ** (1 / 12) - 1)
        P = pmt_from_balance(mort.balance, mort.apr, mort.months)
        M = 800.0

        pre0 = simulate_prepay_equal_cashflow(mort, invest, M, 0.0, P)
        preM = simulate_prepay_equal_cashflow(mort, invest, M, M, P)
        inv = simulate_invest_only(mort, invest, M)

        f0 = pre0.fv - inv
        fM = preM.fv - inv
        # Either we hit equality exactly, or the signs differ
        self.assertTrue((abs(f0) < 1e-9) or (abs(fM) < 1e-9) or (f0 * fM < 0.0))


if __name__ == "__main__":
    unittest.main()
