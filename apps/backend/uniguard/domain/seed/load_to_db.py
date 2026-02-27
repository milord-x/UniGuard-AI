from __future__ import annotations

import json
from pathlib import Path

from uniguard.db.base import reset_db, connect

ROOT = Path(__file__).resolve().parents[5]  # .../UniGuard_AI
DEMO_DIR = ROOT / "data" / "demo"

def _read(name: str):
    p = DEMO_DIR / name
    return json.loads(p.read_text(encoding="utf-8"))

def main() -> None:
    students = _read("students.json")
    templates = _read("templates.json")
    weekly = _read("weekly_earned.json")
    snaps = _read("snapshots_week12.json")

    reset_db()
    conn = connect()
    try:
        cur = conn.cursor()

        # students
        cur.executemany(
            "INSERT INTO students(student_id, full_name, group_name, week_now) VALUES (?, ?, ?, ?)",
            [(s["student_id"], s["full_name"], s["group"], int(s["week_now"])) for s in students],
        )

        # templates
        tpl_rows = []
        for sid, t in templates.items():
            tpl_rows.append((
                t["subject_id"],
                t["subject_name"],
                float(t.get("rk1_max") or 100.0),
                float(t.get("rk2_max") or 100.0),
                json.dumps(t, ensure_ascii=False),
            ))
        cur.executemany(
            "INSERT INTO templates(subject_id, subject_name, rk1_max, rk2_max, raw_json) VALUES (?, ?, ?, ?, ?)",
            tpl_rows,
        )

        # weekly_earned (много строк -> батчами)
        batch = []
        BATCH_SIZE = 50_000
        for r in weekly:
            batch.append((
                r["student_id"],
                r["subject_id"],
                int(r["week"]),
                r["block"],
                r["item_title"],
                float(r["max_points"]),
                float(r["earned_points"]),
            ))
            if len(batch) >= BATCH_SIZE:
                cur.executemany(
                    "INSERT INTO weekly_earned(student_id, subject_id, week, block, item_title, max_points, earned_points) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    batch,
                )
                conn.commit()
                batch.clear()
        if batch:
            cur.executemany(
                "INSERT INTO weekly_earned(student_id, subject_id, week, block, item_title, max_points, earned_points) VALUES (?, ?, ?, ?, ?, ?, ?)",
                batch,
            )
            conn.commit()

        # snapshots
        snap_rows = []
        for s in snaps:
            snap_rows.append((
                s["student_id"],
                s["subject_id"],
                int(s["week"]),
                float(s["rk1_pred"]),
                float(s["rk2_pred"]),
                float(s["admission_pred"]),
                float(s["exam_pred"]),
                float(s["final_pred"]),
                float(s["risk50"]),
                float(s["risk70"]),
                float(s["risk_score"]),
                json.dumps(s["reasons"], ensure_ascii=False),
                json.dumps(s["required"], ensure_ascii=False),
            ))
        cur.executemany(
            """INSERT INTO snapshots(
                student_id, subject_id, week,
                rk1_pred, rk2_pred, admission_pred, exam_pred, final_pred,
                risk50, risk70, risk_score, reasons_json, required_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            snap_rows,
        )
        conn.commit()

        # quick stats
        n_students = cur.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]
        n_weekly = cur.execute("SELECT COUNT(*) c FROM weekly_earned").fetchone()["c"]
        n_snaps = cur.execute("SELECT COUNT(*) c FROM snapshots").fetchone()["c"]
        print("DB loaded")
        print("students:", n_students)
        print("weekly_earned:", n_weekly)
        print("snapshots:", n_snaps)

    finally:
        conn.close()

if __name__ == "__main__":
    main()