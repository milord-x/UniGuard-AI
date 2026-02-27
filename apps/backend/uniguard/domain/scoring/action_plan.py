from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


def _cluster(risk_score: float) -> str:
    if risk_score >= 70:
        return "HIGH"
    if risk_score >= 30:
        return "MED"
    return "LOW"


def _dominant_subject(subjects: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not subjects:
        return None
    # dominant = max subject risk
    return max(subjects, key=lambda s: float(s.get("risk_score", 0.0) or 0.0))


def _infer_reasons(subject: Dict[str, Any]) -> List[str]:
    """
    Егер subject.reasons бар болса — соны қолдан.
    Әйтпесе pred мәндерден rule-based reasons шығарамыз.
    """
    reasons = subject.get("reasons") or []
    if isinstance(reasons, list) and len(reasons) > 0:
        # already computed by your risk/explain logic
        return [str(x) for x in reasons][:4]

    final_pred = float(subject.get("final_pred", 0.0) or 0.0)
    exam_pred = float(subject.get("exam_pred", 0.0) or 0.0)
    adm_pred = float(subject.get("admission_pred", 0.0) or 0.0)
    risk = float(subject.get("risk_score", 0.0) or 0.0)

    out: List[str] = []
    # Heuristics (safe + объяснимые)
    if adm_pred < 50:
        out.append("Рейтинг допуска төмен: апта ішіндегі жинақ баяу (СӨЖ/тапсырмалар кешігіп келеді).")
    if exam_pred < 55:
        out.append("Емтихан болжамы әлсіз: базалық тақырыптарда олқылық бар.")
    if final_pred < 60:
        out.append("Қорытынды балл 60-тан төмен болу ықтималдығы бар: тұрақты балл жинау керек.")
    if risk >= 70:
        out.append("Қауіп жоғары: бір аптада түзету болмаса, нәтиже тез құлдырайды.")
    if not out:
        out.append("Қауіп себебі анық емес: қосымша дерек (тапсырма статусы/қатысу) қажет.")

    return out[:4]


def _action_plan(cluster: str, subject_id: str) -> List[Dict[str, str]]:
    """
    3 нақты әрекет: short + detail.
    """
    if cluster == "HIGH":
        return [
            {
                "title": "48 сағат ішінде эдвайзер байланысы",
                "detail": f"{subject_id} пәні бойынша қысқа диагностика: қандай апта/қандай компонент (СӨЖ, тапсырма, тест) құлап тұр — нақтылау.",
            },
            {
                "title": "7 күндік қалпына келтіру жоспары",
                "detail": "Күніне 60–90 минут: 1) backlog тапсырмалар, 2) минималды балл жинау, 3) апта соңында қайта тексеріс.",
            },
            {
                "title": "Емтиханға мақсатты дайындық",
                "detail": "Негізгі 3 тақырыпты анықтап, қысқа конспект + 20–30 практика тапсырма (әлсіз жерге ғана).",
            },
        ]
    if cluster == "MED":
        return [
            {
                "title": "Апта сайынғы бақылау",
                "detail": f"{subject_id} пәнінде келесі аптада қандай балл керек екенін есептеп, жоспарға бекіту.",
            },
            {
                "title": "Кіші интервенция",
                "detail": "Апта ішінде 1 office-hour/консультация, 2 қысқа тапсырма, 1 өзіндік тест.",
            },
            {
                "title": "Тұрақтандыру",
                "detail": "Күнделікті 30–45 минут: лекция+практика тең үлес, кешіктірмеу.",
            },
        ]
    # LOW
    return [
        {
            "title": "Режимді сақтау",
            "detail": "Қазіргі қарқын жақсы: тапсырмаларды уақытында тапсыруды жалғастыру.",
        },
        {
            "title": "Қауіпсіз буфер",
            "detail": f"{subject_id} пәнінен 1 қосымша тапсырма/қайталау жасап, балл қорын жинау.",
        },
        {
            "title": "Емтиханға алдын ала база",
            "detail": "Аптасына 1 рет 40 минут: негізгі ұғымдар мен формулаларды қайталау.",
        },
    ]


def build_action_plan_payload(student: Dict[str, Any], subjects: List[Dict[str, Any]], risk_score: float) -> Dict[str, Any]:
    cluster = _cluster(float(risk_score or 0.0))
    dom = _dominant_subject(subjects)

    dom_id = dom.get("subject_id") if dom else None
    dom_risk = float(dom.get("risk_score", 0.0) or 0.0) if dom else 0.0
    dom_reasons = _infer_reasons(dom) if dom else ["Пән деректері жоқ."]

    actions = _action_plan(cluster, dom_id or "N/A")

    return {
        "student_id": student.get("student_id"),
        "full_name": student.get("full_name"),
        "group_name": student.get("group_name"),
        "risk_score": float(risk_score or 0.0),
        "cluster": cluster,
        "dominant_subject": dom_id,
        "dominant_subject_risk": dom_risk,
        "reasons": dom_reasons,
        "actions": actions,
    }