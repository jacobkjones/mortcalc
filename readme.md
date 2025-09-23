
# mortcalc — Mortgage Prepay vs Invest Tipping-Point Calculator (CLI)


**Goal**: Compare putting extra dollars into your mortgage vs investing in an S&P 500–like index, and solve for tipping points:
- **Equal-Cashflow breakeven** `E*` (extra per month within fixed budget `M`)
- **Lambda tipping point** `λ*` (how many ×`M` you’d need to put toward the mortgage to break even)
- **Mortgage-Max** head-to-head (put all `M` to principal until payoff, then invest)


## Features
- Pure-Python, standard library only (3.10+)
- Deterministic math (bisection solver)
- Minimal inputs; sane defaults (annual return default 10%)
- Common horizon comparison at month `N`
- After payoff, freed cash flow invested through month `N`


## Install / Run
```bash
python -m mortcalc.cli --balance 350000 --rate 0.065 --years 27 --contrib 800 --solve-equal-cashflow --solve-lambda


## Arguments

- --balance B (required)

- --rate r_m nominal APR (required)

- --months N or --years Y (required)

- --contrib M monthly discretionary (required)

- --payment P (optional; validated against computed PMT)

- --annual-return R (default 0.10)

- Modes: --solve-equal-cashflow, --solve-lambda, --mortgage-max

### Notes

- Taxes and inflation ignored (for now). --taxes flag reserved for future.

- If R <= 12 * i_m (roughly), prepay often favored—CLI may surface a note in a later pass.