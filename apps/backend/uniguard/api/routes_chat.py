from __future__ import annotations

from fastapi import APIRouter

from uniguard.services.student_service import student_profile

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
def chat(payload: dict):
    student_id = payload.get("student_id")
    if not student_id:
        return {"reply": "student_id жоқ. Мысалы: {\"student_id\":\"S0001\", \"message\":\"Не істеу керек?\"}"}

    prof = student_profile(student_id)
    if prof.get("error"):
        return {"reply": "Студент табылмады."}

    subjects = prof.get("subjects", [])
    if not subjects:
        return {"reply": "Пәндер бойынша дерек жоқ."}

    # ең қауіпті пән
    worst = max(subjects, key=lambda x: float(x.get("risk_score", 0.0)))
    sid = worst["subject_id"]
    risk = worst["risk_score"]
    final_pred = worst["final_pred"]
    reasons = worst.get("reasons", [])
    req = worst.get("required", {})
    need_exam = req.get("exam_min_for_50")

    msg_lines = []
    msg_lines.append(f"Ең жоғары қауіп пәні: {sid}")
    msg_lines.append(f"RiskScore (құлау ықтималдығы): {risk:.1f}/100")
    msg_lines.append(f"Болжамды итог: {final_pred:.1f}")

    if reasons:
        msg_lines.append("Негізгі себептер:")
        for r in reasons[:3]:
            msg_lines.append(f"- {r}")

    # нақты әрекет ұсынысы
    msg_lines.append("Ұсынылатын әрекеттер:")
    msg_lines.append("- RK2 бойынша апта сайынғы тапсырмаларды жабу (қазір темп төмен болса — бірінші мақсат).")
    msg_lines.append("- 2 апта қатарынан нөл болса: ең жақын тапсырмаларды тез жинап, streak үз.")
    if need_exam is not None:
        msg_lines.append(f"- 50-ден шығу үшін минималды емтихан: {float(need_exam):.1f}")

    return {"reply": "\n".join(msg_lines)}