from matplotlib import pyplot as plt
import numpy as np
import panel as pn
import seaborn as sns
from bokeh.models import Div


def heatmap_plot(args):
    separated_df = args.data
    separated_df["Year"] = separated_df[args.options["time_column"]].dt.year
    separated_df["Month"] = separated_df[args.options["time_column"]].dt.month

    pivot_df = separated_df.pivot_table(
        index="Year", columns="Month", aggfunc="size", fill_value=0
    )
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.set(font_scale=0.4)
    sns.heatmap(pivot_df, cmap="inferno", annot=True, fmt="d", linewidths=0.5)
    plt.title("Monthly Incident Counts Over Different Years", fontsize=12)
    heatmap_app = pn.pane.Matplotlib(plt.gcf(), align="center")
    # Show the Panel app
    heatmap_app.servable()

    return heatmap_app
