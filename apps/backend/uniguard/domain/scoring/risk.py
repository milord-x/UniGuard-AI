from __future__ import annotations

import math

def _phi(z: float) -> float:
    # CDF стандартного нормального распределения
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

def risk_prob(threshold: float, mu_final: float, sigma_final: float) -> float:
    if sigma_final <= 1e-9:
        return 1.0 if mu_final < threshold else 0.0
    z = (threshold - mu_final) / sigma_final
    return max(0.0, min(1.0, _phi(z)))

def sigma_final(coverage: float) -> float:
    """
    coverage ~ доля закрытого контроля (0..1). Чем ближе к 1, тем меньше неопределённость.
    """
    coverage = max(0.0, min(1.0, coverage))
    sigma_adm = 18.0 * (1.0 - coverage)
    sigma_exam = 12.0
    # итоговый шум после весов 0.6/0.4
    return math.sqrt((0.6 * sigma_adm) ** 2 + (0.4 * sigma_exam) ** 2)