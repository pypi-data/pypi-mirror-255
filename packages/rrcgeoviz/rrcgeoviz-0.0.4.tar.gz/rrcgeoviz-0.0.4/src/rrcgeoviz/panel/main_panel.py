import threading
from time import sleep
import time
import pandas as pd
import panel as pn
from bokeh.models import Div
from .panel_components.heatmap import heatmap_plot
from panel.widgets.indicators import BooleanIndicator
from dateutil.parser import parse
from panel.io import server

# TODO: add links in sidebar (see chatGPT)


def render_panel(args, data_dict=None, test=False):
    template = pn.template.BootstrapTemplate(
        title="GeoViz - " + str(args.data_file_name),
        collapsed_sidebar=True,
        logo="https://th.bing.com/th/id/OIG.MuHhZlwjBdkZD4AELDyV?pid=ImgGn",
    )

    if "time_column" in args.options:
        args.data[args.options["time_column"]] = pd.to_datetime(
            args.data[args.options["time_column"]]
        )

    # add components here
    mainColumn = addCorrectElements(args, data_dict)

    template.main.append(
        pn.Tabs(("Visualizations", mainColumn), ("Pandas Profiling", pn.Column()))
    )

    if not test:
        server = pn.serve(template)

    return template


def addCorrectElements(arguments, data_dict):
    """Actually add the right elements to the display.
    A dictionary of generated data and the arguments are available for purchase at the gift store.
    """

    mainColumn = pn.Column(sizing_mode="stretch_width")

    # month/year heatmap
    if (
        "month_year_heatmap" in arguments.options
        and arguments.options["month_year_heatmap"]
        and "time_column" in arguments.options
    ):
        heatmap_element = heatmap_plot(arguments)
        mainColumn.append(heatmap_element)

    return mainColumn
