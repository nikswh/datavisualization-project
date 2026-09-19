from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path as MplPath


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "processed" / "acled_civilian_targeting_2021_2025.parquet"
OUTPUT_DIR = PROJECT_DIR / "outputs" / "eda_figures"
OUTPUT_STEM = OUTPUT_DIR / "10_region_subevent_alluvial"

BACKGROUND = "#F7F3EE"
INK = "#17233C"
MUTED = "#6E7480"
COLORS = {
    "Air/drone strike": "#E76F51",
    "Attack": "#9B2C47",
    "Shelling/artillery/missile attack": "#6C5CE7",
    "Remote explosive/landmine/IED": "#D49A22",
    "Mob violence": "#238A8D",
    "Other": "#B8B3AA",
}
DISPLAY_LABELS = {
    "Air/drone strike": "Air/drone strikes",
    "Attack": "Direct attacks on civilians",
    "Shelling/artillery/missile attack": "Shelling, artillery & missiles",
    "Remote explosive/landmine/IED": "IEDs & landmines",
    "Mob violence": "Mob violence",
    "Other": "Other forms of violence",
}


def format_number(value: int) -> str:
    return f"{value:,}"


def build_flow_data() -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    df = pd.read_parquet(
        DATA_PATH,
        columns=["region", "sub_event_type", "fatalities", "civilian_targeting"],
    )
    if not df["civilian_targeting"].astype(str).eq("Civilian targeting").all():
        raise ValueError("The analytical dataset is not exclusively civilian targeting.")

    region_totals = (
        df.groupby("region", observed=True)["fatalities"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
    )
    selected = df.loc[df["region"].isin(region_totals.index)].copy()

    top_subtypes: dict[str, set[str]] = {}
    for region in region_totals.index:
        top_subtypes[region] = set(
            selected.loc[selected["region"].eq(region)]
            .groupby("sub_event_type", observed=True)["fatalities"]
            .sum()
            .nlargest(3)
            .index.astype(str)
        )

    selected["flow_type"] = [
        str(subtype) if str(subtype) in top_subtypes[str(region)] else "Other"
        for region, subtype in zip(selected["region"], selected["sub_event_type"])
    ]
    flows = (
        selected.groupby(["region", "flow_type"], observed=True)["fatalities"]
        .sum()
        .reset_index()
    )
    flows = flows.loc[flows["fatalities"].gt(0)].copy()
    subtype_totals = flows.groupby("flow_type")["fatalities"].sum().sort_values(ascending=False)
    return flows, region_totals, subtype_totals


def draw_ribbon(
    ax: plt.Axes,
    source_x: float,
    target_x: float,
    source_top: float,
    source_bottom: float,
    target_top: float,
    target_bottom: float,
    color: str,
) -> None:
    bend = (target_x - source_x) * 0.46
    vertices = [
        (source_x, source_top),
        (source_x + bend, source_top),
        (target_x - bend, target_top),
        (target_x, target_top),
        (target_x, target_bottom),
        (target_x - bend, target_bottom),
        (source_x + bend, source_bottom),
        (source_x, source_bottom),
        (source_x, source_top),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CLOSEPOLY,
    ]
    ax.add_patch(
        PathPatch(
            MplPath(vertices, codes),
            facecolor=color,
            edgecolor="none",
            alpha=0.57,
            zorder=1,
        )
    )


def make_figure() -> plt.Figure:
    flows, region_totals, subtype_totals = build_flow_data()
    regions = list(region_totals.index.astype(str))
    subtype_order = [
        subtype
        for subtype in [
            "Air/drone strike",
            "Shelling/artillery/missile attack",
            "Attack",
            "Remote explosive/landmine/IED",
            "Mob violence",
            "Other",
        ]
        if subtype in subtype_totals.index
    ]
    flow_values = {
        (str(row.region), str(row.flow_type)): int(row.fatalities)
        for row in flows.itertuples()
    }
    scale = 0.285 / float(region_totals.max())
    source_x_left, source_x_right = 0.205, 0.218
    target_x_left, target_x_right = 0.775, 0.788

    source_segments: dict[tuple[str, str], tuple[float, float]] = {}
    source_nodes: dict[str, tuple[float, float]] = {}
    source_cursor = 0.84
    for region in regions:
        node_top = source_cursor
        for subtype in subtype_order:
            value = flow_values.get((region, subtype), 0)
            if not value:
                continue
            segment_top = source_cursor
            source_cursor -= value * scale
            source_segments[(region, subtype)] = (segment_top, source_cursor)
        source_nodes[region] = (node_top, source_cursor)
        source_cursor -= 0.05

    target_segments: dict[tuple[str, str], tuple[float, float]] = {}
    target_nodes: dict[str, tuple[float, float]] = {}
    target_cursor = 0.84
    for subtype in subtype_order:
        node_top = target_cursor
        for region in regions:
            value = flow_values.get((region, subtype), 0)
            if not value:
                continue
            segment_top = target_cursor
            target_cursor -= value * scale
            target_segments[(region, subtype)] = (segment_top, target_cursor)
        target_nodes[subtype] = (node_top, target_cursor)
        target_cursor -= 0.014

    fig, ax = plt.subplots(figsize=(16, 9.6), facecolor=BACKGROUND)
    ax.set_facecolor(BACKGROUND)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    for subtype in subtype_order:
        for region in regions:
            key = (region, subtype)
            if key not in source_segments:
                continue
            source_top, source_bottom = source_segments[key]
            target_top, target_bottom = target_segments[key]
            draw_ribbon(
                ax,
                source_x_right,
                target_x_left,
                source_top,
                source_bottom,
                target_top,
                target_bottom,
                COLORS[subtype],
            )

    for region, (top, bottom) in source_nodes.items():
        ax.add_patch(
            Rectangle(
                (source_x_left, bottom),
                source_x_right - source_x_left,
                top - bottom,
                facecolor=INK,
                edgecolor="none",
                zorder=3,
            )
        )
        center = (top + bottom) / 2
        ax.text(
            source_x_left - 0.018,
            center + 0.012,
            region,
            ha="right",
            va="center",
            fontsize=16,
            fontweight="bold",
            color=INK,
        )
        ax.text(
            source_x_left - 0.018,
            center - 0.024,
            f"{format_number(int(region_totals[region]))} fatalities",
            ha="right",
            va="center",
            fontsize=12,
            color=MUTED,
        )

    small_label_y = {
        "Remote explosive/landmine/IED": 0.255,
        "Mob violence": 0.185,
        "Other": 0.115,
    }
    for subtype, (top, bottom) in target_nodes.items():
        ax.add_patch(
            Rectangle(
                (target_x_left, bottom),
                target_x_right - target_x_left,
                top - bottom,
                facecolor=COLORS[subtype],
                edgecolor="none",
                zorder=3,
            )
        )
        center = (top + bottom) / 2
        label_y = small_label_y.get(subtype, center)
        if subtype in small_label_y:
            ax.plot(
                [target_x_right + 0.003, target_x_right + 0.014],
                [center, label_y],
                color=COLORS[subtype],
                linewidth=1.1,
                alpha=0.8,
                zorder=3,
            )
        ax.text(
            target_x_right + 0.018,
            label_y + 0.011,
            DISPLAY_LABELS[subtype],
            ha="left",
            va="center",
            fontsize=14,
            fontweight="bold",
            color=INK,
        )
        ax.text(
            target_x_right + 0.018,
            label_y - 0.022,
            f"{format_number(int(subtype_totals[subtype]))} fatalities",
            ha="left",
            va="center",
            fontsize=11,
            color=MUTED,
        )

    major_flow_labels = [
        ("Middle East", "Air/drone strike", 0.45, "47.9k"),
        ("Western Africa", "Attack", 0.48, "34.1k"),
        ("South America", "Attack", 0.56, "36.4k"),
    ]
    for region, subtype, x_position, label in major_flow_labels:
        source_top, source_bottom = source_segments[(region, subtype)]
        target_top, target_bottom = target_segments[(region, subtype)]
        progress = (x_position - source_x_right) / (target_x_left - source_x_right)
        source_center = (source_top + source_bottom) / 2
        target_center = (target_top + target_bottom) / 2
        y_position = source_center + (target_center - source_center) * progress
        ax.text(
            x_position,
            y_position,
            label,
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color=INK,
            bbox={"boxstyle": "round,pad=0.25", "facecolor": BACKGROUND, "edgecolor": "none", "alpha": 0.88},
            zorder=4,
        )

    ax.text(0.0, 0.955, "REGIONS", fontsize=10.5, fontweight="bold", color=MUTED, ha="left")
    ax.text(1.0, 0.955, "FORMS OF VIOLENCE", fontsize=10.5, fontweight="bold", color=MUTED, ha="right")
    fig.text(
        0.06,
        0.955,
        "Three regions, two anatomies of violence",
        ha="left",
        va="top",
        fontsize=30,
        fontweight="bold",
        color=INK,
    )
    fig.text(
        0.06,
        0.905,
        "Remote violence drives the civilian toll in the Middle East; direct attacks dominate Western Africa and South America",
        ha="left",
        va="top",
        fontsize=14,
        color=MUTED,
    )
    fig.text(
        0.06,
        0.04,
        "Civilian-targeting events only  •  1 Jan 2021–25 Aug 2025  •  Fatalities refer to the full ACLED event  •  Source: ACLED",
        ha="left",
        va="bottom",
        fontsize=10.5,
        color=MUTED,
    )
    fig.subplots_adjust(left=0.055, right=0.945, top=0.84, bottom=0.10)
    return fig


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    figure = make_figure()
    figure.savefig(OUTPUT_STEM.with_suffix(".png"), dpi=180, facecolor=BACKGROUND)
    figure.savefig(OUTPUT_STEM.with_suffix(".svg"), facecolor=BACKGROUND)
    plt.close(figure)
    print(f"Created {OUTPUT_STEM.with_suffix('.png').relative_to(PROJECT_DIR)}")
    print(f"Created {OUTPUT_STEM.with_suffix('.svg').relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
