from __future__ import annotations

from typing import Any, Dict, List

from .base import connect


def list_subjects() -> List[Dict[str, Any]]:
    con = connect()
    try:
        cur = con.execute(
            "SELECT subject_id, subject_name, rk1_max, rk2_max FROM templates ORDER BY subject_id"
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        con.close()