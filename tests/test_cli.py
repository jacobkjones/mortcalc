import unittest
from mortcalc.cli import run_cli


class CLISmoke(unittest.TestCase):
    def test_smoke_equal_cashflow(self):
        # Minimal run with one mode to ensure CLI executes without error
        code = run_cli([
            "--balance", "350000",
            "--rate", "0.065",
            "--years", "27",
            "--contrib", "800",
            "--solve-equal-cashflow",
        ])
        self.assertEqual(code, 0)

    def test_smoke_lambda(self):
        code = run_cli([
            "--balance", "275000",
            "--rate", "0.049",
            "--months", "288",
            "--contrib", "500",
            "--solve-lambda",
        ])
        self.assertEqual(code, 0)

    def test_smoke_mortgage_max(self):
        code = run_cli([
            "--balance", "350000",
            "--rate", "0.065",
            "--months", "324",
            "--contrib", "800",
            "--mortgage-max",
        ])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
