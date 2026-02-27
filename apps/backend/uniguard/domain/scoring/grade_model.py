from __future__ import annotations

def admission(rk1: float, rk2: float) -> float:
    return (rk1 + rk2) / 2.0

def final_grade(rk1: float, rk2: float, exam: float) -> float:
    adm = admission(rk1, rk2)
    return 0.6 * adm + 0.4 * exam