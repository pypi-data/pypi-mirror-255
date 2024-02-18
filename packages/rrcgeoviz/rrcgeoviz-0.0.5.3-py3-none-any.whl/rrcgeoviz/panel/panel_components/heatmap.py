from matplotlib import pyplot as plt
import panel as pn
import seaborn as sns


def heatmap_plot(args):
    # given args (an Arguments object with data and options), return a servable panel component
    separated_df = args.data
    separated_df["Year"] = separated_df[args.options["time_column"]].dt.year
    separated_df["Month"] = separated_df[args.options["time_column"]].dt.month

    pivot_df = separated_df.pivot_table(
        index="Year", columns="Month", aggfunc="size", fill_value=0
    )
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    sns.set(font_scale=0.4)
    sns.heatmap(pivot_df, cmap="inferno", annot=True, fmt="d", linewidths=0.5)
    plt.title("Monthly Incident Counts Over Different Years", fontsize=12)

    heatmap_app = pn.pane.Matplotlib(plt.gcf())
    heatmap_checkbox = pn.widgets.Checkbox(name="Heatmap Plot", value=True)
    heatmap = pn.Column(
        heatmap_checkbox,
        pn.Column(
            heatmap_app,
            visible=heatmap_checkbox.param.value,
        ),
    )
    # Show the Panel app
    heatmap.servable()

    return heatmap
