"""Compact section-profile illustrations for report chapters."""
from __future__ import annotations

import io
import re


def _selected(inputs: dict, prefix: str) -> str:
    for key, value in inputs.items():
        if key.startswith(prefix) and value not in (None, ""):
            return str(value)
    return ""


def _dimensions(designation: str) -> tuple[float, float, float]:
    values = [float(value) for value in re.findall(r"\d+(?:\.\d+)?", designation)]
    if len(values) >= 3:
        return values[0], values[1], values[2]
    if len(values) == 2:
        return values[0], values[1], max(3.0, min(values) * 0.08)
    return 50.0, 50.0, 5.0


def _profile_png(section_type: str, designation: str, *, girder=None) -> bytes:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Rectangle

    section_type = (section_type or "").strip()
    designation = (designation or "Section not specified").strip()
    fig, ax = plt.subplots(figsize=(3.7, 2.6), constrained_layout=True)
    fill, edge = "#91b20d", "#34420a"

    if girder is not None:
        depth = float(girder.girder_section_d)
        web_t = float(girder.girder_section_tw)
        top_w = float(girder.girder_section_bf)
        top_t = float(girder.girder_section_tf)
        bot_w = float(girder.girder_section_bf_b)
        bot_t = float(girder.girder_section_tf_b)
        ax.add_patch(Rectangle((-top_w / 2, depth / 2 - top_t), top_w, top_t,
                               facecolor=fill, edgecolor=edge, linewidth=1.4))
        ax.add_patch(Rectangle((-web_t / 2, -depth / 2 + bot_t), web_t,
                               depth - top_t - bot_t, facecolor=fill,
                               edgecolor=edge, linewidth=1.4))
        ax.add_patch(Rectangle((-bot_w / 2, -depth / 2), bot_w, bot_t,
                               facecolor=fill, edgecolor=edge, linewidth=1.4))
        label = (f"Web {web_t:g} × {depth - top_t - bot_t:g} mm; "
                 f"flanges {top_w:g} × {top_t:g} / {bot_w:g} × {bot_t:g} mm")
    else:
        width, height, thickness = _dimensions(designation)
        stype = section_type.lower()
        if any(token in stype for token in ("double angle", "double l")):
            gap = max(thickness * 0.5, width * 0.06)
            for sign in (-1, 1):
                cx = sign * gap / 2
                points = (
                    (cx, -height / 2),
                    (cx - sign * width, -height / 2),
                    (cx - sign * width, -height / 2 + thickness),
                    (cx - sign * thickness, -height / 2 + thickness),
                    (cx - sign * thickness, height / 2),
                    (cx, height / 2),
                )
                ax.add_patch(Polygon(points, closed=True, facecolor=fill,
                                     edgecolor=edge, linewidth=1.4))
            label = f"Double angle profile: {designation}"
        elif "angle" in stype or stype.strip().startswith("l"):
            points = ((0, 0), (width, 0), (width, thickness),
                      (thickness, thickness), (thickness, height), (0, height))
            ax.add_patch(Polygon(points, closed=True, facecolor=fill,
                                 edgecolor=edge, linewidth=1.4))
            label = f"Angle profile: {designation}"
        elif any(token in stype for token in ("hollow", "box", "tube", "shs", "rhs")):
            wall = min(thickness, width * 0.35, height * 0.35)
            ax.add_patch(Rectangle((-width / 2, -height / 2), width, height,
                                   facecolor=fill, edgecolor=edge, linewidth=1.4))
            ax.add_patch(Rectangle((-width / 2 + wall, -height / 2 + wall),
                                   width - 2 * wall, height - 2 * wall,
                                   facecolor="white", edgecolor=edge, linewidth=1.0))
            label = f"Hollow profile: {designation}"
        else:
            flange = max(thickness, min(width, height) * 0.12)
            web = max(thickness, width * 0.12)
            ax.add_patch(Rectangle((-width / 2, height / 2 - flange), width, flange,
                                   facecolor=fill, edgecolor=edge, linewidth=1.4))
            ax.add_patch(Rectangle((-web / 2, -height / 2 + flange), web,
                                   height - 2 * flange, facecolor=fill,
                                   edgecolor=edge, linewidth=1.4))
            ax.add_patch(Rectangle((-width / 2, -height / 2), width, flange,
                                   facecolor=fill, edgecolor=edge, linewidth=1.4))
            label = f"{section_type or 'Section'}: {designation}"

    ax.set_aspect("equal", adjustable="datalim")
    ax.autoscale_view()
    ax.margins(0.2)
    ax.axis("off")
    ax.text(0.5, -0.04, label, transform=ax.transAxes,
            ha="center", va="top", fontsize=8, wrap=True)
    ax.text(0.5, -0.14, "Section profile schematic; use the listed designation for dimensions.",
            transform=ax.transAxes, ha="center", va="top", fontsize=6.5, color="#555555")
    stream = io.BytesIO()
    fig.savefig(stream, format="png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    return stream.getvalue()


def build_section_figures(inputs: dict, girder_parameters) -> dict[str, bytes]:
    """Build CAD-adjacent section sketches using selected section metadata."""
    figures = {
        "section_preview": _profile_png("Plate Girder", "Plate Girder", girder=girder_parameters),
    }
    section_specs = (
        ("cb_bracing", "member_properties.cross_bracing_details.bracing_section_type.",
         "member_properties.cross_bracing_details.bracing_section_designation."),
        ("cb_top_chord", "member_properties.cross_bracing_details.top_chord_section_type.",
         "member_properties.cross_bracing_details.top_chord_section_designation."),
        ("cb_bottom_chord", "member_properties.cross_bracing_details.bottom_chord_section_type.",
         "member_properties.cross_bracing_details.bottom_chord_section_designation."),
        ("ed_bracing", "member_properties.end_diaphragm_details.bracing_section.",
         "member_properties.end_diaphragm_details.bracing_section_designation."),
        ("ed_top_chord", "member_properties.end_diaphragm_details.top_chord_section_type.",
         "member_properties.end_diaphragm_details.top_chord_section_designation."),
        ("ed_bottom_chord", "member_properties.end_diaphragm_details.bottom_chord_section_type.",
         "member_properties.end_diaphragm_details.bottom_chord_section_designation."),
    )
    for name, type_prefix, designation_prefix in section_specs:
        section_type = _selected(inputs, type_prefix)
        designation = _selected(inputs, designation_prefix)
        if section_type or designation:
            figures[name] = _profile_png(section_type, designation)
    return figures
