## GeoViz

GeoViz is an Exploratory Data Analysis tool designed to empower less-technical data analysts in visualizing and interpreting spatio-temporal data. It offers a user-friendly, interactive web interface built on Panel, ensuring simplicity and maximal explainability. The software provides visualizations, including 3D geographical coordinates, seasonality analysis, heatmap displays, and categorization/clustering using Natural Language Processing (NLP). With a focus on simplicity and shareability, GeoViz enhances data analysis for a broader audience.

The documentation can be found at our [readthedocs page](https://rincon-geoviz.readthedocs.io/en/latest/index.html).

### Example Usage

First, install GeoViz:

```bash
pip install rrcgeoviz
```

Once done, create an options.json file for your spatio-temporal CSV dataset. Here's a basic example:

```json
{
    "latitude_column": "latitude",
    "longitude_column": "longitude",
    "time_column": "date",
    "poi_analysis": true,
    "month_year_heatmap": true
}
```

Finally, run GeoViz with the following command:

```bash
rrcgeoviz path/to/dataset.csv --options path/to/options.json
```

A tab should open in your browser with a heatmap and Points of Interest (POI) analysis!

## Brief overview of how it works (for contributers)

When running from the command line, the main() function in src/rrcgeoviz/geoviz_cli.py runs. The options and dataset are stored in an Arguments object (found in the same file) and passed to the render_panel() function at src/rrcegeoviz/panel/main_panel.py.

Render_panel creates a [Bootstrap Panel](https://panel.holoviz.org/reference/templates/Bootstrap.html) template which has a "main" element. Based on the options in the Arguments, different panel components (e.g. heatmap, POI, etc.) are added to the "main" element in addCorrectElements(), called by render_panel().

Code that *generates* data should be called in a generateData() function called by main() before render_panel(). All that the panel components should do is create visualizations of the data, *not* create it!

Here's a general flow of how to add new components:
1. If new data is required (e.g. distance to nearest POI) create a new data generation function file in src/rrcgeoviz/datagenerators.
2. If a new data generator was made, add a call to it in generateData().
3. Create the panel component in src/rrcgeoviz/panel/panel_components. Look at other components in the directory for a sense of what they look like.
4. Add a check for the relevant option in addCorrectElements(), looking at other examples to see how it's done. Be sure to add checks for other options required for it to work (e.g. time_column).

That's pretty much it!

