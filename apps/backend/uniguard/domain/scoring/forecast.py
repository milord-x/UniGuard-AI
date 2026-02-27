from __future__ import annotations

import math

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def predict_rk_from_progress(earned_so_far: float, max_so_far: float, max_total: float, prior_rate: float = 0.75) -> float:
    """
    Прогнозируем итог RK (0..max_total) по текущему темпу.
    """
    if max_so_far <= 1e-9:
        rate = prior_rate
    else:
        rate = earned_so_far / max_so_far
    rate_adj = clamp(0.7 * rate + 0.3 * prior_rate, 0.0, 1.0)
    pred = earned_so_far + (max_total - max_so_far) * rate_adj
    return clamp(pred, 0.0, max_total)

def predict_exam_from_admission(admission_pred: float) -> float:
    """
    Экзамен обычно коррелирует с допуском, но шумнее.
    """
    return clamp(0.85 * admission_pred + 12.0, 0.0, 100.0)