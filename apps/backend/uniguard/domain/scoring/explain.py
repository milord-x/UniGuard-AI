from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

@dataclass(frozen=True)
class Explanation:
    reasons: List[str]
    required: Dict[str, float]  # минимально необходимый rk2/exam и т.п.

def build_explanation(
    week: int,
    rk1_pred: float,
    rk2_pred: float,
    exam_pred: float,
    final_pred: float,
    rk2_rate_adj: float,
    zero_streak: int,
    threshold_main: float = 50.0,
) -> Explanation:
    reasons: List[str] = []

    if rk2_rate_adj < 0.6:
        reasons.append(f"Low RK2 progress rate (rate={rk2_rate_adj:.2f})")
    if zero_streak >= 2:
        reasons.append(f"Missed submissions streak: {zero_streak} weeks")
    if final_pred < threshold_main:
        reasons.append(f"Predicted final below {threshold_main:.0f}: {final_pred:.1f}")

    # Что нужно для выхода за 50: минимальный экзамен при текущем допуске
    # Final = 0.6*Adm + 0.4*Exam >= 50  => Exam >= (50 - 0.6*Adm)/0.4
    adm = (rk1_pred + rk2_pred) / 2.0
    need_exam = (threshold_main - 0.6 * adm) / 0.4
    need_exam = clamp(need_exam, 0.0, 100.0)

    required = {"exam_min_for_50": need_exam}

    # Если причин мало — добавим универсальную
    if not reasons:
        reasons.append("Stable performance; no critical risk indicators detected")

    return Explanation(reasons=reasons[:3], required=required)