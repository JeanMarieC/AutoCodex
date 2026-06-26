"""Small labeled Q&A set for evaluation.

Tied to the generated sample-manual content (app/rag/sample.py) so the harness
is self-contained and reproducible. `expected_section` is the manual section the
answer should be retrieved from; `expected_keywords` are facts a faithful answer
should mention.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.agent.state import Car

EVAL_CAR = Car(make="Mercedes-Benz", model="C200", year="1998")


@dataclass(frozen=True)
class EvalItem:
    question: str
    expected_section: str
    expected_keywords: tuple[str, ...]


EVAL_ITEMS: list[EvalItem] = [
    EvalItem("What kind of engine oil should I use?", "Engine Oil", ("synthetic", "oil")),
    EvalItem("Where are the recommended tire pressures listed?", "Tire Pressures", ("door",)),
    EvalItem("What does a red warning lamp mean?", "Warning Lights", ("red", "stop")),
    EvalItem("How tight should fasteners be?", "Torque Specifications", ("torque",)),
    EvalItem("How do I service the brakes?", "Brake System", ("brake",)),
    EvalItem("How is the transmission serviced?", "Transmission Service", ("filter",)),
]
