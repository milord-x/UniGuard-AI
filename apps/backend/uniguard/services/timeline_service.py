from __future__ import annotations

from typing import Any, Dict, List

from uniguard.db.repo_timeline import timeline_weekly


def build_timeline(student_id: str, subject_id: str) -> Dict[str, Any]:
    rows = timeline_weekly(student_id, subject_id)

    # Превращаем в удобный формат: weeks 1..12, rk1/rk2 series
    # Если недели пропущены — заполняем нулями.
    max_week = 12

    rk1 = {r["week"]: r for r in rows if r["block"] == "RK1"}
    rk2 = {r["week"]: r for r in rows if r["block"] == "RK2"}

    def pack(block_map: dict) -> List[Dict[str, Any]]:
        out = []
        for w in range(1, max_week + 1):
            r = block_map.get(w)
            earned = float(r["earned_sum"]) if r else 0.0
            maxs = float(r["max_sum"]) if r else 0.0
            rate = (earned / maxs) if maxs > 1e-9 else None
            out.append({"week": w, "earned": round(earned, 2), "max": round(maxs, 2), "rate": rate})
        return out

    return {"student_id": student_id, "subject_id": subject_id, "rk1": pack(rk1), "rk2": pack(rk2)}