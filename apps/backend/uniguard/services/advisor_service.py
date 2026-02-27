from __future__ import annotations

from typing import Any, Dict, List

from uniguard.db.repo_advisor import heatmap_rows, list_groups


def _cluster(risk: float) -> str:
    if risk >= 70:
        return "HIGH"
    if risk >= 30:
        return "MED"
    return "LOW"


def _dominant_subject(subjects: Dict[str, float]) -> str | None:
    if not subjects:
        return None
    return max(subjects.items(), key=lambda kv: kv[1])[0]


def get_groups_payload() -> Dict[str, Any]:
    groups = list_groups()
    return {"groups": groups}


def get_heatmap_payload(group_name: str, week: int = 12, limit: int = 24) -> Dict[str, Any]:
    subjects, rows = heatmap_rows(group_name=group_name, week=week, limit=limit)

    out_rows: List[Dict[str, Any]] = []
    for r in rows:
        dom = _dominant_subject(r["subjects"])
        out_rows.append(
            {
                **r,
                "cluster": _cluster(float(r["risk_score"])),
                "dominant_subject": dom,
            }
        )

    # summary (clusters)
    summary = {"HIGH": 0, "MED": 0, "LOW": 0}
    for r in out_rows:
        summary[r["cluster"]] += 1

    return {
        "week": week,
        "group_name": group_name,
        "limit": limit,
        "subjects": subjects,
        "rows": out_rows,
        "summary": summary,
    }