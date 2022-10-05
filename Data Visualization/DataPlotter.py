import pandas as pd
from bokeh.tile_providers import get_provider
from ipyleaflet import basemaps
from bokeh.models import ColumnDataSource, GeoJSONDataSource
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool
import json
import random

class DataPlotter:
  def __init__(self):
    # Create placeholder plots with no data so that it can be updated in a Panel modal later.
    self.time_series = figure(title = "Time-Series", x_axis_type = "datetime")
    self.time_series_hover_tool = HoverTool()
    self.time_series.add_tools(self.time_series_hover_tool)

    self.all_data = figure(title = "Original Data")
    self.all_data_hover_tool = HoverTool()
    self.all_data.add_tile(get_provider(basemaps.OpenStreetMap.Mapnik))
    self.all_data.add_tools(self.all_data_hover_tool)
    
    # results = list of created plots to display
    self.results = [self.time_series, self.all_data]

  def set_hover_tooltip(self, hover_tool: "bokeh.models.tools.HoverTool", tooltip_layout: dict, dataframe_cols: list[str]) -> None:
    """
    Set tooltips that appear when hovering over a data point to reflect the given tooltip layout if specified.
    
    Args:
      hover_tool ():
      tooltip_layout (dict):
      dataframe_cols (list[str]): List of column names existing in the plotted dataframe
    """
    if tooltip_layout is not None: hover_tool.tooltips = [(label, "@" + col_name) for label, col_name in tooltip_vals.items()]
    else: hover_tool.tooltips = [(col, "@" + col) for col in dataframe_cols]

  def plot_time_series(self, data_path: str, datetime_col_name: str, y_axis_label: str, y_axis_col_name: str, tooltip_vals: dict = None, x_axis_label: str = "Time") -> None:
    """
    Plots data at the given file path as a time-series graph.

    Args:
      data_path (str): Path to a directory containing data that needs to be plotted
      datetime_col_name (str): Name of the column containing the date or time that the data was collected
      y_axis_label (str): Name for the plot's y-axis
      y_axis_col_name (str): Name of the column containing data values for the y-axis
      tooltip_vals (dict): Optional dictionary with labels that appear in a tooltip as keys and column names corresponding to their data as values
      x_axis_label (str): Optional name for the plot's x-axis
    """
    # Clear the scatter plot.
    self.time_series.renderers = []
    
    # Update the time-series scatter plot with the given data.
    dataframe = pd.read_csv(data_path)
    dataframe[datetime_col_name] = pd.to_datetime(dataframe[datetime_col_name])
    new_source = ColumnDataSource(dataframe)
    self.time_series.xaxis.axis_label = x_axis_label
    self.time_series.yaxis.axis_label = y_axis_label
    self.time_series.scatter(
      x = datetime_col_name, y = y_axis_col_name,
      source = new_source,
      size = 12, fill_alpha = 0.4,
      # legend_field = "species",
      # marker = factor_mark("species", MARKERS, SPECIES),
      # color = factor_cmap("species", "Category10_3", SPECIES)
    )

    # Set tooltips for the plot's data points on hover.
    self.set_hover_tooltip(
      hover_tool = self.time_series_hover_tool,
      tooltip_layout = tooltip_vals,
      dataframe_cols = dataframe.columns
    )
  
  def plot_data(self, geojson_data: "GeoJSON", x_axis_col_name: str, y_axis_col_name: str, tooltip_vals: dict = None, x_axis_label: str = "Latitude", y_axis_label: str = "Longitude", data_point_color: str = "blue") -> None:
    """
    Plots all given GeoJSON data in a map plot.

    Args:
      geojson_data (GeoJSON): Feature collection containing all data features that need to be plotted
      x_axis_col_name (str): Name of the column containing the latitude or some other data value that the user prefers for the x-axis
      y_axis_col_name (str): Name of the column containing the longitude or some other data value that the user prefers for the y-axis
      tooltip_vals (dict): Optional dictionary with labels that appear in a tooltip as keys and column names corresponding to their data as values
      x_axis_label (str): Optional name for the plot's x-axis, default is "Latitude"
      y_axis_label (str): Optional name for the plot's y-axis, default is "Longitude"
      data_point_color (str): Optional color for the plot's data points, default is "blue"
    """
    # Clear the scatter plot.
    self.all_data.renderers = []
    
    # Update the scatter plot with the given GeoJSON data.
    new_geojson_source = GeoJSONDataSource(geojson=json.dumps(geojson_data))
    self.all_data.xaxis.axis_label = x_axis_label
    self.all_data.yaxis.axis_label = y_axis_label
    self.all_data.scatter(
      x = x_axis_col_name, y = y_axis_col_name,
      source = new_geojson_source,
      color = data_point_color, size = 12, fill_alpha = 0.4
    )

    # Set tooltips for the plot's data points on hover.
    self.set_hover_tooltip(
      hover_tool = self.all_data_hover_tool,
      tooltip_layout = tooltip_vals,
      dataframe_cols = [property for property in geojson_data["features"][0]["properties"]]
    )
    