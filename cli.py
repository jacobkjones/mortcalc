from __future__ import annotations

import argparse
from dataclasses import dataclass

from .finance import (
    MortgageInputs,
    InvestmentInputs,
    pmt_from_balance,
    simulate_invest_only,
    simulate_prepay_equal_cashflow,
    simulate_prepay_lambda,
    simulate_mortgage_max,
)
from .solvers import solve_bisection

DEFAULT_ANNUAL_RETURN = 0.10  # 10% nominal


def monthly_return_from_annual(R_annual: float) -> float:
    return (1.0 + R_annual) ** (1.0 / 12.0) - 1.0


@dataclass
class ParsedArgs:
    balance: float
    rate: float
    months: int
    payment: float
    contrib: float
    annual_return: float
    solve_equal: bool
    solve_lambda: bool
    mortgage_max: bool
    json: bool
    table: bool
    chart: bool
    precision: int


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mortcalc", description="Mortgage Prepay vs Invest tipping-point calculator")
    p.add_argument("--balance", type=float, required=True)
    p.add_argument("--rate", type=float, required=True, help="Mortgage nominal APR (e.g., 0.065)")

    gterm = p.add_mutually_exclusive_group(required=True)
    gterm.add_argument("--months", type=int)
    gterm.add_argument("--years", type=float)

    p.add_argument("--contrib", type=float, required=True, help="Monthly discretionary contribution M")
    p.add_argument("--payment", type=float)
    p.add_argument("--annual-return", type=float, default=DEFAULT_ANNUAL_RETURN)

    p.add_argument("--solve-equal-cashflow", action="store_true")
    p.add_argument("--solve-lambda", action="store_true")
    p.add_argument("--mortgage-max", action="store_true")

    p.add_argument("--json", action="store_true")
    p.add_argument("--table", action="store_true")
    p.add_argument("--chart", action="store_true")
    p.add_argument("--precision", type=int, default=6)

    p.add_argument("--version", action="version", version="mortcalc 0.1.0")
    return p


def parse_args(ns: argparse.Namespace) -> ParsedArgs:
    months = ns.months if ns.months else int(round(float(ns.years) * 12))
    payment = ns.payment
    if payment is None:
        payment = pmt_from_balance(ns.balance, ns.rate, months)
    else:
        computed = pmt_from_balance(ns.balance, ns.rate, months)
        if abs(payment - computed) > 1.0:
            print(f"[warn] Provided payment ${payment:.2f} differs from computed ${computed:.2f} by > $1.00")
    return ParsedArgs(
        balance=float(ns.balance),
        rate=float(ns.rate),
        months=int(months),
        payment=float(payment),
        contrib=float(ns.contrib),
        annual_return=float(ns.annual_return),
        solve_equal=bool(ns.solve_equal_cashflow),
        solve_lambda=bool(ns.solve_lambda),
        mortgage_max=bool(ns.mortgage_max),
        json=bool(ns.json),
        table=bool(ns.table),
        chart=bool(ns.chart),
        precision=int(ns.precision),
    )


def run_cli(argv: list[str] | None = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    args = parse_args(ns)

    mort = MortgageInputs(balance=args.balance, apr=args.rate, months=args.months, payment=args.payment)
    invest = InvestmentInputs(monthly_return=monthly_return_from_annual(args.annual_return))

    fv_invest = simulate_invest_only(mort, invest, args.contrib)

    if args.solve_equal:
        def f_E(E: float) -> float:
            pre = simulate_prepay_equal_cashflow(mort, invest, args.contrib, E, args.payment)
            return pre.fv - fv_invest

        res = solve_bisection(f_E, 0.0, args.contrib)
        if res.converged and res.root is not None:
            E_star = res.root
            pct = (E_star / args.contrib * 100.0) if args.contrib > 0 else 0.0
            print(f"Equal-Cashflow breakeven E*: ${E_star:.{args.precision}f} ({pct:.{args.precision}f}% of M)")
        else:
            print("Equal-Cashflow: no root found within [0, M].")

    if args.solve_lambda:
        def f_lam(lam: float) -> float:
            pre = simulate_prepay_lambda(mort, invest, args.contrib, lam, args.payment)
            return pre.fv - fv_invest

        lo, hi = 0.0, 1.0
        f_lo = f_lam(lo)
        f_hi = f_lam(hi)
        cap = 20.0
        while f_lo * f_hi > 0 and hi < cap:
            hi *= 2.0
            f_hi = f_lam(hi)

        if f_lo * f_hi > 0:
            print("Lambda: no tipping point up to 20×M — investing dominates.")
        else:
            res = solve_bisection(f_lam, lo, hi)
            if res.converged and res.root is not None:
                lam_star = res.root
                pct_more = max(0.0, (lam_star - 1.0) * 100.0)
                print(
                    f"Tipping point λ*: {lam_star:.{args.precision}f}×M → +{pct_more:.{args.precision}f}% more toward mortgage to break even."
                )
            else:
                print("Lambda: bisection failed to converge.")

    if args.mortgage_max:
        pre = simulate_mortgage_max(mort, invest, args.contrib, args.payment)
        delta = pre.fv - fv_invest
        winner = "Prepay (Mortgage-Max)" if delta >= 0 else "Invest"
        print(f"Mortgage-Max winner: {winner}. ΔFV = ${delta:.{args.precision}f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
