from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Dict

Block = Literal["RK1", "RK2"]

@dataclass(frozen=True)
class TemplateItem:
    subject_id: str
    subject_name: str
    block: Block
    week: int                 # 1..15
    title: str
    max_points: float         # >= 0

@dataclass(frozen=True)
class SubjectTemplate:
    subject_id: str
    subject_name: str
    items: List[TemplateItem]

    def by_block(self, block: Block) -> List[TemplateItem]:
        return [x for x in self.items if x.block == block]

    def max_total(self, block: Block) -> float:
        return sum(x.max_points for x in self.by_block(block))

    def max_by_week(self, block: Block) -> Dict[int, float]:
        out: Dict[int, float] = {}
        for it in self.by_block(block):
            out[it.week] = out.get(it.week, 0.0) + it.max_points
        return out