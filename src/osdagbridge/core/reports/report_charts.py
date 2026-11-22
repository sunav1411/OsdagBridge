"""Temporary, data-driven charts embedded in report chapters."""
from __future__ import annotations

import logging
import math
import os

logger = logging.getLogger(__name__)


def _number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def _max_numeric(values):
    parsed = [_number(value) for value in values]
    parsed = [value for value in parsed if value is not None and value >= 0]
    return max(parsed) if parsed else None


def _design_utilizations(payload, bridge):
    outputs = payload.output_dict or {}
    results = outputs.get("design_results", {}) or {}
    steel = []
    for item in (results.get("per_girder", {}) or {}).values():
        for check in item.get("checks", []) or []:
            if isinstance(check, dict):
                # The current design payload calls this dcr; older payloads
                # and report adapters use ur.
                steel.append(check.get("ur", check.get("dcr")))
    # Flat steel utilization values are expressed as percentages by the UI.
    for key in ("util.flexure", "util.shear", "util.interaction", "util.ltb"):
        if outputs.get(key) is not None:
            steel.append(_number(outputs[key]) / 100.0)

    deck = []
    deck_values = outputs.get("deck_report_values", {}) or {}
    for demand_key, capacity_key in (
        ("deck.report.m_uls_sag", "deck.report.mu_bot"),
        ("deck.report.m_uls_hog", "deck.report.mu_top"),
        ("deck.report.m_uls_oh", "deck.report.mu_oh"),
        ("deck.report.punch_ved", "deck.report.vrd_c_mpa"),
        ("deck.report.shear_ved", "deck.report.shear_vrdc"),
    ):
        demand, capacity = _number(deck_values.get(demand_key)), _number(deck_values.get(capacity_key))
        if demand is not None and capacity is not None and capacity > 0:
            deck.append(demand / capacity)
    deck_results = outputs.get("deck_design_results", {}) or {}
    for key, value in deck_results.items():
        if "ur" in str(key).lower() or "ratio" in str(key).lower():
            deck.append(value)

    cross_bracing = []
    for pair in bridge.get_cb_pairs():
        for member in ("diagonal", "chord"):
            for force_type in ("tension", "compression"):
                cross_bracing.append(bridge.get_cb_efficiency(pair, member, force_type))

    end_diaphragm = []
    def collect_efficiencies(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if str(key).lower() in {"ur", "dcr", "efficiency", "ratio"}:
                    end_diaphragm.append(value)
                else:
                    collect_efficiencies(value)
        elif isinstance(obj, list):
            for value in obj:
                collect_efficiencies(value)
    collect_efficiencies(outputs.get("end_diaphragm_design_results", {}) or {})

    return {
        "Steel Plate Girders": _max_numeric(steel),
        "Concrete Deck Slab": _max_numeric(deck),
        "Cross Bracing": _max_numeric(cross_bracing),
        "End Diaphragms": _max_numeric(end_diaphragm),
    }


def _save_utilization_chart(path, payload, bridge):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .styles import PALETTE

    values = _design_utilizations(payload, bridge)
    labels = list(values)
    numbers = [values[label] for label in labels]
    fig, ax = plt.subplots(figsize=(8.4, 3.8), constrained_layout=True)
    colors = [f"#{PALETTE['pass']}" if value is not None and value <= 1 else f"#{PALETTE['fail']}" for value in numbers]
    heights = [value if value is not None else 0 for value in numbers]
    bars = ax.bar(labels, heights, color=colors, width=0.62)
    ax.axhline(1.0, color=f"#{PALETTE['fail']}", linestyle="--", linewidth=1.6, label="Capacity limit (UR = 1.0)")
    for bar, value in zip(bars, numbers):
        ax.text(bar.get_x() + bar.get_width()/2, max(bar.get_height(), 0) + 0.035,
                f"{value:.2f}" if value is not None else "No check data",
                ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("Utilization Ratio (Demand / Capacity)")
    ax.set_ylim(0, max(1.25, max((value or 0 for value in numbers), default=0) * 1.18))
    ax.tick_params(axis="x", labelrotation=12, labelsize=8)
    ax.grid(axis="y", alpha=0.22)
    ax.legend(frameon=False, loc="upper right", fontsize=8)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_quantity_charts(path_steel, path_concrete, quantities):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .styles import PALETTE

    def total(key):
        return _number(quantities.get(key))

    steel_labels = ["Girders", "Cross bracing", "End diaphragms"]
    steel_values = [total("steel_girders_wt_total"),
                    sum(value or 0 for value in (total("bracing_top_wt_total"), total("bracing_bot_wt_total"), total("bracing_diag_wt_total"))),
                    total("end_diaphragms_wt_total")]
    fig, ax = plt.subplots(figsize=(7.6, 3.3), constrained_layout=True)
    bars = ax.bar(steel_labels, [value or 0 for value in steel_values], color=f"#{PALETTE['steel']}")
    for bar, value in zip(bars, steel_values):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height(), f"{value:.2f}" if value is not None else "N/A", ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("Structural steel (MT)"); ax.grid(axis="y", alpha=.2)
    fig.savefig(path_steel, dpi=180, bbox_inches="tight"); plt.close(fig)

    concrete = total("concrete_deck_vol_total")
    rebar = total("rebar_deck_wt_total")
    fig, ax = plt.subplots(figsize=(7.6, 3.3), constrained_layout=True)
    bars = ax.bar(["Concrete deck (m³)", "Reinforcement steel (MT)"], [concrete or 0, rebar or 0],
                  color=[f"#{PALETTE['concrete']}", f"#{PALETTE['reinforcement']}"])
    for bar, value in zip(bars, (concrete, rebar)):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height(), f"{value:.2f}" if value is not None else "N/A", ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("Quantity (units shown per bar)"); ax.grid(axis="y", alpha=.2)
    fig.savefig(path_concrete, dpi=180, bbox_inches="tight"); plt.close(fig)


def generate_report_charts(directory, payload, bridge):
    """Generate report-only chart images in the report's temporary directory."""
    os.makedirs(directory, exist_ok=True)
    paths = {"utilization_summary": os.path.join(directory, "utilization_summary.png"),
             "steel_quantities": os.path.join(directory, "steel_quantities.png"),
             "concrete_reinforcement": os.path.join(directory, "concrete_reinforcement.png")}
    try:
        _save_utilization_chart(paths["utilization_summary"], payload, bridge)
        _save_quantity_charts(paths["steel_quantities"], paths["concrete_reinforcement"], payload.inputs)
        return {key: f"images/{os.path.basename(value)}" for key, value in paths.items()}
    except Exception:
        logger.exception("Could not generate report summary charts")
        return {}
