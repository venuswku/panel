import pandas as pd
from bokeh.tile_providers import get_provider, ESRI_IMAGERY
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool
import json
import os

class DataPlotter:
  def __init__(self):
    # Create placeholder plots with no data so that it can be updated in a Panel modal later.
    self.time_series = figure(title = "Time-Series", x_axis_type = "datetime", tools = "hover")
    # self.time_series_hover_tool = HoverTool()
    # self.time_series.add_tools(self.time_series_hover_tool)

    self.all_data = figure(title = "All Data")
    self.all_data_hover_tool = HoverTool()
    self.all_data.add_tile(get_provider(ESRI_IMAGERY))
    self.all_data.add_tools(self.all_data_hover_tool)
    
    # results = list of created plots to display
    self.results = [self.time_series, self.all_data]

  def set_hover_tooltip(self, hover_tool: "bokeh.models.tools.HoverTool", tooltip_layout: dict, dataframe_cols: list[str]) -> None:
    """
    Set tooltips that appear when hovering over a data point to reflect the given tooltip layout if specified.
    
    Args:
      hover_tool (bokeh.models.tools.HoverTool): Hover tool to modify its tooltip
      tooltip_layout (dict): Either None or dictionary with labels that appear in a tooltip as keys and column names corresponding to their data as values
      dataframe_cols (list[str]): List of column names existing in the plotted dataframe, which is used for the tooltip layout if None was passed for the tooltip_layout argument
    """
    if tooltip_layout is not None: hover_tool.tooltips = [(label, "@" + col_name) for label, col_name in tooltip_layout.items()]
    else: hover_tool.tooltips = [(col, "@" + col) for col in dataframe_cols]

  def plot_time_series(self, latitude: float, longitude: float, possible_lat_col_names, possible_long_col_names, data_path: str, possible_datetime_col_names: list[str], possible_y_axis_col_names: list[str], data_category_colors: dict, y_axis_label: str, x_axis_label: str = "Time") -> None:
    """
    Plots data at the given file path as a time-series graph.

    Args:
      latitude (float): Latitude of all data points that appear in the time series plot
      longitude (float): Longitude of all data points that appear in the time series plot
      possible_lat_col_names ():
      possible_long_col_names ():
      data_path (str): Path to a directory containing all data that needs to be plotted
      possible_datetime_col_names (list[str]): List of column names containing the date or time that the data was collected (because data from different files might have different column names)
      possible_y_axis_col_names (list[str]): List of column names containing the data values for the y-axis (because data from different files might have different column names)
      data_category_colors (dict): Dictionary mapping data categories (keys) to their color on the plot (values)
      y_axis_label (str): Name for the plot's y-axis
      x_axis_label (str): Optional name for the plot's x-axis
    """
    # Clear the scatter plot.
    self.time_series.renderers = []
    
    self.time_series.xaxis.axis_label = x_axis_label
    self.time_series.yaxis.axis_label = y_axis_label
    
    # Get all data for different categories of data, which should be subfolders in the given data_path.
    data_categories = [file for file in os.listdir(data_path) if os.path.isdir(file)]
    
    # Update the time-series scatter plot with the data from the given data_path.
    rounded_lat, rounded_long = round(latitude, 4), round(longitude, 4)
    for category in data_categories:
      data_category_path = data_path + "/" + category
      data_category_files = os.listdir(data_category_path)
      for file in data_category_files:
        # Only plot data that are collected at the same latitude and longitude as the given lat-long coordinates.
        dataframe = pd.read_csv(data_category_path + "/" + file)
        
        [latitude_col_name] = [col_name for col_name in possible_lat_col_names if col_name in dataframe.columns]
        [longitude_col_name] = [col_name for col_name in possible_long_col_names if col_name in dataframe.columns]
        dataframe = dataframe[(round(dataframe[latitude_col_name], 4) == rounded_lat) & (round(dataframe[longitude_col_name], 4) == rounded_long)]
        
        [datetime_col_name] = [col_name for col_name in possible_datetime_col_names if col_name in dataframe.columns]
        [y_axis_col_name] = [col_name for col_name in possible_y_axis_col_names if col_name in dataframe.columns]
        dataframe[datetime_col_name] = pd.to_datetime(dataframe[datetime_col_name])
        data_source = ColumnDataSource(dataframe)
        
        self.time_series.scatter(
          x = datetime_col_name,
          y = y_axis_col_name,
          source = data_source,
          legend_label = category,
          color = data_category_colors[category],
          size = 12, fill_alpha = 0.4,
          # marker = factor_mark("species", MARKERS, SPECIES)
        )

    # # Set tooltips for the plot's data points on hover.
    # self.set_hover_tooltip(
    #   hover_tool = self.time_series_hover_tool,
    #   tooltip_layout = None,
    #   dataframe_cols = dataframe.columns
    # )
  
  def plot_data(self, data_path: str, x_axis_col_name: str, y_axis_col_name: str, tooltip_vals: dict = None, x_axis_label: str = "Latitude", y_axis_label: str = "Longitude", data_point_color: str = "blue") -> None:
    """
    Plots all data from the given date path in a map plot.

    Args:
      data_path (str): Path to a directory containing data that needs to be plotted
      x_axis_col_name (str): Name of the column containing the latitude or some other data value that the user prefers for the x-axis
      y_axis_col_name (str): Name of the column containing the longitude or some other data value that the user prefers for the y-axis
      tooltip_vals (dict): Optional dictionary with labels that appear in a tooltip as keys and column names corresponding to their data as values
      x_axis_label (str): Optional name for the plot's x-axis, default is "Latitude"
      y_axis_label (str): Optional name for the plot's y-axis, default is "Longitude"
      data_point_color (str): Optional color for the plot's data points, default is "blue"
    """
    # Clear the scatter plot.
    self.all_data.renderers = []
    
    # Update the scatter plot with the given data.
    dataframe = pd.read_csv(data_path)
    new_source = ColumnDataSource(dataframe)
    self.all_data.xaxis.axis_label = x_axis_label
    self.all_data.yaxis.axis_label = y_axis_label
    self.all_data.scatter(
      x = x_axis_col_name,
      y = y_axis_col_name,
      source = new_source,
      color = data_point_color,
      size = 12, fill_alpha = 0.4
    )

    # Set tooltips for the plot's data points on hover.
    self.set_hover_tooltip(
      hover_tool = self.all_data_hover_tool,
      tooltip_layout = tooltip_vals,
      dataframe_cols = dataframe.columns
    )