from __future__ import annotations

import random
from dataclasses import dataclass

@dataclass(frozen=True)
class StudentProfileParams:
    ability_mean: float     # средний коэффициент 0..1
    ability_sd: float
    miss_prob: float        # вероятность пропуска конкретной активности
    shock_prob: float       # вероятность резкого провала после 9 недели
    shock_drop: float       # насколько падает способность при шоке (0..1)

def sample_profile(rng: random.Random) -> StudentProfileParams:
    """
    Смешиваем несколько типов студентов: сильные/средние/слабые.
    """
    p = rng.random()
    if p < 0.15:  # сильные
        return StudentProfileParams(ability_mean=0.90, ability_sd=0.05, miss_prob=0.05, shock_prob=0.05, shock_drop=0.15)
    if p < 0.75:  # средние
        return StudentProfileParams(ability_mean=0.75, ability_sd=0.10, miss_prob=0.12, shock_prob=0.12, shock_drop=0.25)
    # слабые/нестабильные
    return StudentProfileParams(ability_mean=0.55, ability_sd=0.12, miss_prob=0.22, shock_prob=0.18, shock_drop=0.35)

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def sample_ability(rng: random.Random, mean: float, sd: float) -> float:
    # нормальное приближение, ограничиваем
    return clamp(rng.gauss(mean, sd), 0.05, 0.98)