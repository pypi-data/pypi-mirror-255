import os
import threading
from time import sleep
import time
import pandas as pd
import panel as pn
from bokeh.models import Div

from .panel_components.yearly_range import yearly_range_plot
from .panel_components.heatmap import heatmap_plot
from panel.widgets.indicators import BooleanIndicator
from dateutil.parser import parse
from panel.io import server

import importlib.resources

from bokeh.core.validation import silence
from bokeh.core.validation.warnings import EMPTY_LAYOUT, MISSING_RENDERERS

# TODO: add links in sidebar (see chatGPT)


def render_panel(args, test=False):
    # get favicon
    # favicon_path = str(importlib.resources.path("static_data", "favicon.ico"))
    # logo_path = str(importlib.resources.path("static_data", "geoviz.jpg"))
    logo_path = "https://i.imgur.com/Loud9RB.jpeg"

    template = pn.template.BootstrapTemplate(
        title="GeoViz - " + str(args.data_file_name),
        collapsed_sidebar=True,
        logo=logo_path,
        # favicon=favicon_path,
    )

    if "time_column" in args.options:
        args.data[args.options["time_column"]] = pd.to_datetime(
            args.data[args.options["time_column"]]
        )

    # add components here
    mainColumn = addCorrectElements(args)

    template.main.append(
        pn.Tabs(("Visualizations", mainColumn), ("Pandas Profiling", pn.Column()))
    )

    if not test:
        silence(EMPTY_LAYOUT, True)
        silence(MISSING_RENDERERS, True)
        server = pn.serve(template)

    return template


def addCorrectElements(arguments):
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

    # TODO: one_year, months, one_year_months, threeD, POI (data gen), pandas_profiling?, NLP (data gen)
    if (
        "yearly_range" in arguments.options
        and arguments.options["yearly_range"]
        and "latitude_column" in arguments.options
        and "longitude_column" in arguments.options
    ):
        yearly_range_element = yearly_range_plot(arguments)
        mainColumn.append(yearly_range_element)

    return mainColumn
