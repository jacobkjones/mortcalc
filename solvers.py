from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class SolveResult:
    root: Optional[float]
    f_at_root: Optional[float]
    iters: int
    converged: bool
    message: str = ""


def solve_bisection(
    f: Callable[[float], float],
    lo: float,
    hi: float,
    tol: float = 1e-6,
    max_iter: int = 200,
) -> SolveResult:
    """
    Find root of f(x)=0 in [lo, hi] using bisection. Requires sign change.
    Converges when abs(f(mid)) < tol or when interval becomes tiny.
    """
    f_lo = f(lo)
    f_hi = f(hi)
    if f_lo == 0.0:
        return SolveResult(root=lo, f_at_root=0.0, iters=0, converged=True, message="exact lo root")
    if f_hi == 0.0:
        return SolveResult(root=hi, f_at_root=0.0, iters=0, converged=True, message="exact hi root")

    if f_lo * f_hi > 0:
        return SolveResult(root=None, f_at_root=None, iters=0, converged=False, message="no sign change on [lo, hi]")

    a, b = lo, hi
    fa, fb = f_lo, f_hi
    it = 0
    while it < max_iter:
        it += 1
        mid = (a + b) / 2.0
        fm = f(mid)
        if abs(fm) < tol:
            return SolveResult(root=mid, f_at_root=fm, iters=it, converged=True, message="abs(f) < tol")
        if fa * fm <= 0:
            b, fb = mid, fm
        else:
            a, fa = mid, fm
        if abs(b - a) < 1e-12:
            m = (a + b) / 2.0
            return SolveResult(root=m, f_at_root=f(m), iters=it, converged=True, message="interval tiny")

    m = (a + b) / 2.0
    return SolveResult(root=m, f_at_root=f(m), iters=it, converged=False, message="max_iter reached")
