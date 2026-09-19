from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "processed" / "acled_civilian_targeting_2021_2025.parquet"
OUTPUT_DIR = PROJECT_DIR / "outputs" / "eda_figures"
OUTPUT_STEM = OUTPUT_DIR / "10_region_subevent_bars"

BACKGROUND = "#F7F3EE"
INK = "#17233C"
MUTED = "#6E7480"
GRID = "#DED8D0"
COLORS = {
    "Air/drone strike": "#E76F51",
    "Attack": "#9B2C47",
    "Shelling/artillery/missile attack": "#6C5CE7",
    "Remote explosive/landmine/IED": "#D49A22",
    "Mob violence": "#238A8D",
}
DISPLAY_LABELS = {
    "Air/drone strike": "Air/drone strikes",
    "Attack": "Direct attacks on civilians",
    "Shelling/artillery/missile attack": "Shelling, artillery & missiles",
    "Remote explosive/landmine/IED": "IEDs & landmines",
    "Mob violence": "Mob violence",
}


def format_number(value: int) -> str:
    return f"{value:,}"


def load_chart_data() -> tuple[pd.DataFrame, pd.Series]:
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
    grouped = (
        df.loc[df["region"].isin(region_totals.index)]
        .groupby(["region", "sub_event_type"], observed=True)["fatalities"]
        .sum()
        .reset_index()
    )
    top_three = (
        grouped.sort_values(["region", "fatalities"], ascending=[True, False])
        .groupby("region", observed=True, group_keys=False)
        .head(3)
    )
    return top_three, region_totals


def make_figure() -> plt.Figure:
    data, region_totals = load_chart_data()
    regions = list(region_totals.index.astype(str))
    maximum = int(data["fatalities"].max())
    axis_maximum = ((maximum + 9_999) // 10_000) * 10_000 + 7_000

    figure, axes = plt.subplots(
        nrows=3,
        ncols=1,
        figsize=(14, 10),
        sharex=True,
        facecolor=BACKGROUND,
    )

    for axis, region in zip(axes, regions):
        subset = (
            data.loc[data["region"].eq(region)]
            .sort_values("fatalities", ascending=True)
            .copy()
        )
        labels = [DISPLAY_LABELS[str(value)] for value in subset["sub_event_type"]]
        colors = [COLORS[str(value)] for value in subset["sub_event_type"]]
        values = subset["fatalities"].astype(int).tolist()

        axis.set_facecolor(BACKGROUND)
        bars = axis.barh(labels, values, color=colors, height=0.58)
        axis.set_xlim(0, axis_maximum)
        axis.xaxis.set_major_locator(MultipleLocator(10_000))
        axis.xaxis.set_major_formatter(FuncFormatter(lambda value, _: "0" if value == 0 else f"{value / 1000:.0f}k"))
        axis.grid(axis="x", color=GRID, linewidth=0.8)
        axis.set_axisbelow(True)
        axis.tick_params(axis="y", length=0, labelsize=12, colors=INK, pad=10)
        axis.tick_params(axis="x", length=0, labelsize=10, colors=MUTED)
        for spine in axis.spines.values():
            spine.set_visible(False)

        axis.text(
            0,
            1.20,
            region,
            transform=axis.transAxes,
            ha="left",
            va="center",
            fontsize=17,
            fontweight="bold",
            color=INK,
        )
        axis.text(
            1,
            1.20,
            f"{format_number(int(region_totals[region]))} total fatalities",
            transform=axis.transAxes,
            ha="right",
            va="center",
            fontsize=11,
            color=MUTED,
        )
        for bar, value in zip(bars, values):
            axis.text(
                value + axis_maximum * 0.012,
                bar.get_y() + bar.get_height() / 2,
                format_number(value),
                ha="left",
                va="center",
                fontsize=11,
                fontweight="bold",
                color=INK,
            )

    axes[0].tick_params(axis="x", labelbottom=False)
    axes[1].tick_params(axis="x", labelbottom=False)
    axes[-1].set_xlabel("Reported fatalities", fontsize=11, color=MUTED, labelpad=12)

    figure.text(
        0.07,
        0.965,
        "Different regions, different forms of violence",
        ha="left",
        va="top",
        fontsize=28,
        fontweight="bold",
        color=INK,
    )
    figure.text(
        0.07,
        0.918,
        "Top three sub-event types by fatalities in the three most affected regions",
        ha="left",
        va="top",
        fontsize=14,
        color=MUTED,
    )
    figure.text(
        0.07,
        0.027,
        "Civilian-targeting events only  •  1 Jan 2021–25 Aug 2025  •  Fatalities refer to the full ACLED event  •  Source: ACLED",
        ha="left",
        va="bottom",
        fontsize=10,
        color=MUTED,
    )
    figure.subplots_adjust(left=0.27, right=0.94, top=0.84, bottom=0.10, hspace=0.62)
    return figure


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
