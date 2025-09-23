from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class MortgageInputs:
    balance: float  # B
    apr: float      # r_m nominal annual APR (e.g., 0.065)
    months: int     # N remaining term in months
    payment: Optional[float] = None  # P (optional)


@dataclass(frozen=True)
class InvestmentInputs:
    monthly_return: float  # r_i monthly, i.e., (1+R)**(1/12)-1


@dataclass(frozen=True)
class AmortizationResult:
    payoff_month: int  # month index (1-based) when balance hits 0
    interest_paid: float
    months_elapsed: int  # equals payoff_month


def pmt_from_balance(balance: float, apr: float, months: int) -> float:
    """
    Compute the mortgage payment P for given balance, APR, and months.

    i_m = apr / 12
    P = B * i_m / (1 - (1 + i_m)^(-N))
    """
    if months <= 0:
        raise ValueError("months must be positive")
    if balance <= 0:
        raise ValueError("balance must be positive")
    if apr < 0:
        raise ValueError("apr must be non-negative")

    i_m = apr / 12.0
    if i_m == 0.0:
        return balance / months
    denom = 1.0 - (1.0 + i_m) ** (-months)
    if denom <= 0:
        raise ValueError("invalid parameters result in non-positive denominator")
    return balance * i_m / denom


def amortize_with_extra(balance: float, apr: float, payment: float, extra: float) -> AmortizationResult:
    """
    Amortize with constant scheduled payment `payment` and constant extra `extra`.
    Returns when balance reaches zero. Raises if payment+extra cannot amortize.
    """
    if balance <= 0:
        return AmortizationResult(payoff_month=0, interest_paid=0.0, months_elapsed=0)

    if payment < 0 or extra < 0:
        raise ValueError("payment and extra must be non-negative")

    i_m = apr / 12.0
    bal = float(balance)
    interest_paid = 0.0
    month = 0

    # Safety cap to prevent infinite loop on bad inputs
    max_iter = 100000

    while bal > 1e-8:
        month += 1
        if month > max_iter:
            raise RuntimeError("amortization did not converge; check inputs")
        interest = bal * i_m
        interest_paid += interest
        principal_due = payment - interest
        total_principal = principal_due + extra
        if total_principal <= 0:
            raise ValueError("payment + extra not sufficient to amortize the loan")
        pay_principal = min(bal, total_principal)
        bal -= pay_principal

    return AmortizationResult(payoff_month=month, interest_paid=interest_paid, months_elapsed=month)


def fv_from_contributions(contribs: List[float], monthly_return: float) -> float:
    """
    Future value at the end of len(contribs) months with monthly compounding and
    end-of-period contributions: FV_t = FV_{t-1} * (1+r) + C_t
    """
    fv = 0.0
    r = monthly_return
    for c in contribs:
        fv = fv * (1.0 + r) + c
    return fv


def invest_only_fv(months: int, monthly_contribution: float, monthly_return: float) -> float:
    return fv_from_contributions([monthly_contribution] * months, monthly_return)


@dataclass(frozen=True)
class ScenarioResult:
    fv: float
    payoff_month: int
    interest_paid: float


def simulate_prepay_equal_cashflow(
    mort: MortgageInputs,
    invest: InvestmentInputs,
    M: float,
    E: float,
    payment: float,
) -> ScenarioResult:
    """
    Equal-Cashflow scenario: total outflow fixed at (P+M).
      - Prepay: pay P+E to mortgage, invest (M−E) until payoff; after payoff, invest (P+M).
      - Horizon: month N.
    """
    if E < 0 or E > M:
        raise ValueError("E must be in [0, M] for equal-cashflow mode")

    amort = amortize_with_extra(mort.balance, mort.apr, payment, E)
    t_pay = amort.payoff_month

    N = mort.months
    contribs: List[float] = []
    for t in range(1, N + 1):
        if t <= t_pay:
            contribs.append(M - E)
        else:
            contribs.append(payment + M)

    fv = fv_from_contributions(contribs, invest.monthly_return)
    return ScenarioResult(fv=fv, payoff_month=t_pay, interest_paid=amort.interest_paid)


def simulate_prepay_lambda(
    mort: MortgageInputs,
    invest: InvestmentInputs,
    M: float,
    lam: float,
    payment: float,
) -> ScenarioResult:
    """
    Lambda mode: extra E = lam * M (lam >= 0). Cash flow may exceed (P+M).
      - Prepay: pay P + lam*M until payoff; invest 0 before payoff; invest (P + lam*M) after payoff.
      - Horizon: month N.
    """
    if lam < 0:
        raise ValueError("lambda must be >= 0")

    E = lam * M
    amort = amortize_with_extra(mort.balance, mort.apr, payment, E)
    t_pay = amort.payoff_month

    N = mort.months
    contribs: List[float] = []
    for t in range(1, N + 1):
        if t <= t_pay:
            contribs.append(0.0)
        else:
            contribs.append(payment + E)

    fv = fv_from_contributions(contribs, invest.monthly_return)
    return ScenarioResult(fv=fv, payoff_month=t_pay, interest_paid=amort.interest_paid)


def simulate_mortgage_max(
    mort: MortgageInputs,
    invest: InvestmentInputs,
    M: float,
    payment: float,
) -> ScenarioResult:
    """
    Mortgage-Max mode: E = M (invest $0 until payoff), then invest (P+M) through N.
    """
    E = M
    amort = amortize_with_extra(mort.balance, mort.apr, payment, E)
    t_pay = amort.payoff_month

    N = mort.months
    contribs: List[float] = []
    for t in range(1, N + 1):
        if t <= t_pay:
            contribs.append(0.0)
        else:
            contribs.append(payment + M)

    fv = fv_from_contributions(contribs, invest.monthly_return)
    return ScenarioResult(fv=fv, payoff_month=t_pay, interest_paid=amort.interest_paid)


def simulate_invest_only(
    mort: MortgageInputs,
    invest: InvestmentInputs,
    M: float,
) -> float:
    """
    Invest scenario: pay P, invest M throughout for N months. Returns FV only.
    """
    return invest_only_fv(mort.months, M, invest.monthly_return)
