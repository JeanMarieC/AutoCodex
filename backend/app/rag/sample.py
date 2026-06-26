"""Generated sample-manual PDFs.

Fallback for when a real download didn't yield a usable PDF (e.g. a ManualsLib
viewer page, or keyless stub mode) so document processing — extraction,
sectioning, chunking — stays demonstrable end-to-end. Content is generic and
clearly marked as a sample; it is NOT a substitute for a real manual.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf

from app.agent.state import Car
from app.tools.models import ManualKind

_OWNER_SECTIONS = [
    ("Engine Oil", "Use a fully synthetic engine oil meeting the manufacturer "
     "specification. Check the level on flat ground with the engine warm. The "
     "oil and filter should be changed at the recommended service interval."),
    ("Tire Pressures", "Recommended cold tire pressures are listed on the driver's "
     "door pillar. Check pressures monthly and before long trips. Under-inflation "
     "increases wear and fuel consumption."),
    ("Warning Lights", "A steady amber lamp indicates a system needs attention "
     "soon; a red lamp indicates a fault requiring you to stop safely. Have the "
     "fault codes read if a warning lamp stays on."),
    ("Fluids and Capacities", "Coolant, brake fluid and washer fluid reservoirs "
     "are located in the engine bay. Use only the fluid types specified for this "
     "vehicle. Do not overfill."),
]

_WORKSHOP_SECTIONS = [
    ("Torque Specifications", "Tighten fasteners to the specified torque in the "
     "correct sequence. Wheel bolts and suspension fasteners are safety-critical "
     "and must be torqued to specification."),
    ("Brake System", "Inspect pads, discs and lines at each service. Bleed the "
     "system after any hydraulic component is opened. Use fresh fluid of the "
     "specified grade."),
    ("Transmission Service", "Check fluid level at operating temperature. When "
     "servicing, drop the pan, replace the filter and refill to the correct "
     "level. Follow the specified fill procedure."),
]


def generate_sample_pdf(path: str | Path, car: Car, manual_name: str, kind: ManualKind) -> str:
    """Create a small multi-page sample PDF (with a TOC) and return its path."""
    sections = _WORKSHOP_SECTIONS if kind == "workshop" else _OWNER_SECTIONS
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open()
    toc: list[list] = []
    for page_no, (title, body) in enumerate(sections, start=1):
        page = doc.new_page()
        rect = pymupdf.Rect(72, 72, page.rect.width - 72, page.rect.height - 72)
        content = (
            f"{car.make} {car.model} {car.year} — {manual_name} (SAMPLE)\n\n"
            f"{title}\n\n{body}\n"
        )
        page.insert_textbox(rect, content, fontsize=11, fontname="helv")
        toc.append([1, title, page_no])

    doc.set_toc(toc)
    doc.save(str(dest))
    doc.close()
    return str(dest)
