from __future__ import annotations

import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any, List, Tuple

from uniguard.domain.templates.excel_parser import parse_subject_template
from uniguard.domain.scoring.grade_model import admission, final_grade
from uniguard.domain.scoring.forecast import predict_rk_from_progress, predict_exam_from_admission
from uniguard.domain.scoring.risk import risk_prob, sigma_final
from uniguard.domain.scoring.explain import build_explanation
from uniguard.domain.seed.distributions import sample_profile, sample_ability, clamp


ROOT = Path(__file__).resolve().parents[5]  # .../UniGuard_AI
TEMPL_DIR = ROOT / "data" / "templates"
OUT_DIR = ROOT / "data" / "demo"

WEEK_NOW = 12
WEEKS_TOTAL = 15

SUBJECTS = [
    ("abai", "Абай ілімі", "abai_ilimi.xlsx"),
    ("ds", "Деректер туралы ғылым", "data_science.xlsx"),
    ("dm", "Дискретті математика", "discrete_math.xlsx"),
    ("pe", "Физическая культура", "phys_culture.xlsx"),
    ("ru", "Русский язык", "russian.xlsx"),
    ("en", "English", "english.xlsx"),
]

def _ensure_dirs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

def _load_templates() -> Dict[str, Any]:
    templates: Dict[str, Any] = {}
    for sid, sname, fname in SUBJECTS:
        path = TEMPL_DIR / fname
        tpl = parse_subject_template(path, sid, sname)
        # sanity: ожидаем около 100 по RK1/RK2 (может быть ± из-за формата)
        templates[sid] = {
            "subject_id": tpl.subject_id,
            "subject_name": tpl.subject_name,
            "items": [asdict(x) for x in tpl.items],
            "rk1_max": tpl.max_total("RK1"),
            "rk2_max": tpl.max_total("RK2"),
        }
    return templates

def _items_by_subject(templates: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    return {sid: templates[sid]["items"] for sid in templates}

def _sum_max(items: List[Dict[str, Any]], block: str, week_upto: int) -> float:
    s = 0.0
    for it in items:
        if it["block"] == block and it["week"] <= week_upto:
            s += float(it["max_points"])
    return s

def _sum_earned(earned: List[Dict[str, Any]], block: str, week_upto: int) -> float:
    s = 0.0
    for e in earned:
        if e["block"] == block and e["week"] <= week_upto:
            s += float(e["earned_points"])
    return s

def _zero_streak(earned_week_totals: Dict[int, float], start_week: int, end_week: int) -> int:
    streak = 0
    for w in range(end_week, start_week - 1, -1):
        if earned_week_totals.get(w, 0.0) <= 1e-9:
            streak += 1
        else:
            break
    return streak

def generate(seed: int = 42, n_students: int = 500) -> None:
    _ensure_dirs()
    rng = random.Random(seed)

    templates = _load_templates()
    items_by_subject = _items_by_subject(templates)

    students: List[Dict[str, Any]] = []
    weekly_earned: List[Dict[str, Any]] = []
    snapshots: List[Dict[str, Any]] = []

    # Генерируем студентов
    for i in range(1, n_students + 1):
        profile = sample_profile(rng)
        base_ability = sample_ability(rng, profile.ability_mean, profile.ability_sd)

        student_id = f"S{i:04d}"
        GROUP_SIZE = 12
        group_index = ((i - 1) // GROUP_SIZE) + 1
        group_name = f"IIBD-{100 + group_index}"
        students.append({
            "student_id": student_id,
            "full_name": f"Student {i:04d}",
            "group": group_name,
            "week_now": WEEK_NOW,
        })

        # на 2-й РК возможен "шок" (резкий провал) — для реалистичности
        has_shock = (rng.random() < profile.shock_prob)

        # начисления по предметам до 12 недели
        for sid, sname, _ in SUBJECTS:
            items = items_by_subject[sid]
            # агрегаты по неделям для streak
            earned_week_totals: Dict[int, float] = {}

            for it in items:
                w = int(it["week"])
                if w > WEEK_NOW:
                    continue

                maxp = float(it["max_points"])
                block = it["block"]

                # способность + шум
                ability = base_ability + rng.gauss(0.0, 0.06)

                # шок проявляется после 9 недели, в RK2
                if has_shock and w >= 9 and block == "RK2":
                    ability = ability * (1.0 - profile.shock_drop)

                ability = clamp(ability, 0.0, 1.0)

                missed = (rng.random() < profile.miss_prob)
                earned = 0.0 if missed else maxp * ability

                # чуть квантуем, чтобы было похоже на “баллы”
                earned = round(earned, 1)

                weekly_earned.append({
                    "student_id": student_id,
                    "subject_id": sid,
                    "subject_name": sname,
                    "week": w,
                    "block": block,
                    "item_title": it["title"],
                    "max_points": maxp,
                    "earned_points": earned,
                })
                earned_week_totals[w] = earned_week_totals.get(w, 0.0) + earned

            # ----------- snapshots на 12 неделе (для демо можно хранить только w=12) ----------
            # считаем RK1 фактически (если закрыт) и RK2 частично + прогноз до 15
            earned_subj = [x for x in weekly_earned if x["student_id"] == student_id and x["subject_id"] == sid]

            rk1_earned = _sum_earned(earned_subj, "RK1", WEEK_NOW)
            rk2_earned = _sum_earned(earned_subj, "RK2", WEEK_NOW)

            rk1_max_sofar = _sum_max(items, "RK1", WEEK_NOW)
            rk2_max_sofar = _sum_max(items, "RK2", WEEK_NOW)

            rk1_max_total = templates[sid]["rk1_max"] or 100.0
            rk2_max_total = templates[sid]["rk2_max"] or 100.0

            # rate RK2
            rk2_rate = (rk2_earned / rk2_max_sofar) if rk2_max_sofar > 1e-9 else 0.75
            rk2_rate_adj = clamp(0.7 * rk2_rate + 0.3 * 0.75, 0.0, 1.0)

            rk1_pred = predict_rk_from_progress(rk1_earned, rk1_max_sofar, rk1_max_total, prior_rate=0.80)
            rk2_pred = predict_rk_from_progress(rk2_earned, rk2_max_sofar, rk2_max_total, prior_rate=0.75)

            adm_pred = admission(rk1_pred, rk2_pred)
            exam_pred = predict_exam_from_admission(adm_pred)
            final_pred = final_grade(rk1_pred, rk2_pred, exam_pred)

            # coverage: берём долю закрытого RK2 (RK1 обычно уже закрыт)
            coverage = clamp(rk2_max_sofar / max(rk2_max_total, 1e-9), 0.0, 1.0)
            sig = sigma_final(coverage)

            r50 = risk_prob(50.0, final_pred, sig)
            r70 = risk_prob(70.0, final_pred, sig)

            zero_streak = _zero_streak(earned_week_totals, 1, WEEK_NOW)
            exp = build_explanation(
                week=WEEK_NOW,
                rk1_pred=rk1_pred,
                rk2_pred=rk2_pred,
                exam_pred=exam_pred,
                final_pred=final_pred,
                rk2_rate_adj=rk2_rate_adj,
                zero_streak=zero_streak,
                threshold_main=50.0,
            )

            snapshots.append({
                "student_id": student_id,
                "subject_id": sid,
                "subject_name": sname,
                "week": WEEK_NOW,
                "rk1_pred": round(rk1_pred, 2),
                "rk2_pred": round(rk2_pred, 2),
                "admission_pred": round(adm_pred, 2),
                "exam_pred": round(exam_pred, 2),
                "final_pred": round(final_pred, 2),
                "risk50": round(r50, 4),
                "risk70": round(r70, 4),
                "risk_score": round(100.0 * r50, 2),
                "reasons": exp.reasons,
                "required": exp.required,
            })

    # Пишем output
    (OUT_DIR / "students.json").write_text(json.dumps(students, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "templates.json").write_text(json.dumps(templates, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "weekly_earned.json").write_text(json.dumps(weekly_earned, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "snapshots_week12.json").write_text(json.dumps(snapshots, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: {len(students)} students, {len(weekly_earned)} earned rows, {len(snapshots)} snapshots")
    print(f"Output: {OUT_DIR}")

if __name__ == "__main__":
    generate()