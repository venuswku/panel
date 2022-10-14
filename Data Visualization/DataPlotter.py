import pandas as pd
from bokeh.tile_providers import get_provider, ESRI_IMAGERY
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool
import os
import random

class DataPlotter:
  def __init__(self, data_dir_path: str, category_colors: dict) -> None:
    """
    Creates a new instance of the DataPlotter class.

    Args:
      data_dir_path (str): Path to the root directory containing all category subfolders and their data files that need to be plotted
      category_colors (dict): Dictionary mapping names of data categories (keys) to their corresponding color (values)
    """
    # Create placeholder plots with no data so that it can be updated in a Panel modal later.
    self.time_series = figure(title = "Time-Series", x_axis_type = "datetime")
    self.time_series.xaxis.formatter = DatetimeTickFormatter(microseconds=["%b %Y"], milliseconds=["%b %Y"], seconds=["%b %Y"], minsec=["%b %Y"], months=["%b %Y"])

    self.original_dataset = figure(title = "Original Dataset that Data Point was Sampled From")
    self.original_dataset_hover_tool = HoverTool()
    self.original_dataset.add_tile(get_provider(ESRI_IMAGERY))
    self.original_dataset.add_tools(self.original_dataset_hover_tool)
    
    # results = list of created plots to display
    self.results = [self.time_series, self.original_dataset]

    # root_data_dir_path = Path to the root directory containing all category subfolders and their data files that need to be plotted
    self.root_data_dir_path = data_dir_path

    # category_colors = dictionary mapping names of data categories (keys) to their corresponding color (values)
    self.category_colors = category_colors

  def set_hover_tooltip(self, hover_tool: "bokeh.models.tools.HoverTool", tooltip_layout: dict, dataframe_cols: list[str], datetime_col: str = None) -> None:
    """
    Set tooltips that appear when hovering over a data point to reflect the given tooltip layout if specified.
    
    Args:
      hover_tool (bokeh.models.tools.HoverTool): Hover tool to modify its tooltip
      tooltip_layout (dict): Either None or dictionary with labels that appear in a tooltip as keys and column names corresponding to their data as values
      dataframe_cols (list[str]): List of column names existing in the plotted dataframe, which is used for the tooltip layout if None was passed for the tooltip_layout argument
      datetime_col (str): Optional name of the date or time column in the plotted dataframe, default is None
    """
    # Add all columns and their values from the data file to its tooltips.
    if tooltip_layout is not None: hover_tool.tooltips = [(label, "@" + col_name) for label, col_name in tooltip_layout.items()]
    else: hover_tool.tooltips = [(col, "@" + col) for col in dataframe_cols]
    # If datetime_col is specified, add a datetime formatter for the date or time value to be readable.
    if datetime_col is not None: hover_tool.formatters = {"@" + datetime_col: "datetime"}

  def plot_time_series(self, latitude: float, longitude: float, possible_lat_col_names, possible_long_col_names, possible_datetime_col_names: list[str], possible_y_axis_col_names: list[str], y_axis_label: str, x_axis_label: str = "Time") -> None:
    """
    Plots data at the given file path as a time-series graph.

    Args:
      latitude (float): Latitude of all data points that appear in the time series plot
      longitude (float): Longitude of all data points that appear in the time series plot
      possible_lat_col_names (list[str]): List of column names containing the latitude of the collected data (because data from different files might have different column names)
      possible_long_col_names (list[str]): List of column names containing the longitude of the collected data (because data from different files might have different column names)
      possible_datetime_col_names (list[str]): List of column names containing the date or time that the data was collected (because data from different files might have different column names)
      possible_y_axis_col_names (list[str]): List of column names containing the data values for the y-axis (because data from different files might have different column names)
      y_axis_label (str): Name for the plot's y-axis
      x_axis_label (str): Optional name for the plot's x-axis
    """
    # Clear the scatter plot and data tooltips (keep default tools).
    self.time_series.renderers = []
    self.time_series.toolbar.tools = self.time_series.toolbar.tools[:6]
    
    # Set x and y axis labels.
    self.time_series.xaxis.axis_label = x_axis_label
    self.time_series.yaxis.axis_label = y_axis_label
    
    # Get all data for different categories of data, which should be subfolders in the given data_path.
    data_categories = [file for file in os.listdir(self.root_data_dir_path) if os.path.isdir(self.root_data_dir_path + "/" + file)]

    # Update the time-series scatter plot with the data from self.root_data_dir_path.
    markers = ["circle", "circle_cross", "circle_dot", "circle_x", "circle_y", "diamond", "diamond_cross", "diamond_dot", "hex", "hex_dot", "inverted_triangle", "plus", "square", "square_cross", "square_dot", "square_pin", "square_x", "star", "star_dot", "triangle", "triangle_dot", "triangle_pin"]
    max_decimals = 4
    rounded_lat, rounded_long = round(latitude, max_decimals), round(longitude, max_decimals)
    self.time_series.title.text = "Time-Series for Data Collected at {} (Latitude), {} (Longitude)".format(rounded_lat, rounded_long)
    for category in data_categories:
      data_category_marker = random.choice(markers)
      data_category_path = self.root_data_dir_path + "/" + category
      data_category_files = os.listdir(data_category_path)
      for file in data_category_files:
        dataframe = pd.read_csv(data_category_path + "/" + file)
        # Plot data that contain one of the specified y-axis columns.
        existing_y_axis_col_names = [col_name for col_name in possible_y_axis_col_names if col_name in dataframe.columns]
        if len(existing_y_axis_col_names) > 0:
          # Filter for data with the same latitude and longitude as the given lat-long coordinates when rounded.
          [latitude_col_name] = [col_name for col_name in possible_lat_col_names if col_name in dataframe.columns]
          [longitude_col_name] = [col_name for col_name in possible_long_col_names if col_name in dataframe.columns]
          dataframe = dataframe.loc[(round(dataframe[latitude_col_name], max_decimals) == rounded_lat) & (round(dataframe[longitude_col_name], max_decimals) == rounded_long)]
          
          # Display non-empty filtered dataframes.
          if len(dataframe.index) > 0:
            # Convert the filtered dataframe into ColumnDataSource, which is compatible for plotting.
            [datetime_col_name] = [col_name for col_name in possible_datetime_col_names if col_name in dataframe.columns]
            y_axis_col_name = existing_y_axis_col_names[0]
            dataframe[datetime_col_name] = pd.to_datetime(dataframe[datetime_col_name])
            data_source = ColumnDataSource(dataframe)
            
            # Plot the filtered data.
            file_scatter_plot = self.time_series.scatter(
              x = datetime_col_name,
              y = y_axis_col_name,
              source = data_source,
              legend_label = category,
              color = self.category_colors[category],
              size = 12, fill_alpha = 0.4,
              marker = data_category_marker
            )
    
            # Add the corresponding tooltip for the file's data points on hover.
            file_hover_tool = HoverTool(renderers=[file_scatter_plot])
            self.time_series.add_tools(file_hover_tool)
            self.set_hover_tooltip(
              hover_tool = file_hover_tool,
              tooltip_layout = None,
              dataframe_cols = dataframe.columns,
              datetime_col = datetime_col_name
            )

          # Get the average/mean y-axis value for each data file.
          # avg = dataframe[y_axis_col_name].mean()
          # for renderer in self.time_series.renderers:
          #   if hasattr(renderer, "glyph"):
          #     print(renderer.data_source.data)
    
    # Customize plot's legend after adding data to scatter plot implicitly creates legend.
    self.time_series.legend.location = "bottom_right"
    self.time_series.legend.click_policy = "hide"     # clicking on a category in the legend hides its data
  
  def plot_original_dataset(self, data_path: str, x_axis_col_name: str, y_axis_col_name: str, datetime_col_name: str, tooltip_vals: dict = None, x_axis_label: str = "Latitude", y_axis_label: str = "Longitude", data_point_color: str = "blue") -> None:
    """
    Plots original dataset from the given data path in a map plot.

    Args:
      data_path (str): Path to a directory containing data that needs to be plotted
      x_axis_col_name (str): Name of the column containing the latitude or some other data value that the user prefers for the x-axis
      y_axis_col_name (str): Name of the column containing the longitude or some other data value that the user prefers for the y-axis
      datetime_col_name (str): Name of the column containing the date or time that the data was collected
      tooltip_vals (dict): Optional dictionary with labels that appear in a tooltip as keys and column names corresponding to their data as values
      x_axis_label (str): Optional name for the plot's x-axis, default is "Latitude"
      y_axis_label (str): Optional name for the plot's y-axis, default is "Longitude"
      data_point_color (str): Optional color for the plot's data points, default is "blue"
    """
    # Clear the scatter plot.
    self.original_dataset.renderers = []

    # Update the scatter plot with the given data.
    self.original_dataset.title.text = "Original Dataset that Data Point was Sampled From: {}".format(data_path)
    dataframe = pd.read_csv(data_path)
    new_source = ColumnDataSource(dataframe)
    self.original_dataset.xaxis.axis_label = x_axis_label
    self.original_dataset.yaxis.axis_label = y_axis_label
    self.original_dataset.scatter(
      x = x_axis_col_name,
      y = y_axis_col_name,
      source = new_source,
      color = data_point_color
    )

    # Set tooltips for the plot's data points on hover.
    self.set_hover_tooltip(
      hover_tool = self.original_dataset_hover_tool,
      tooltip_layout = tooltip_vals,
      dataframe_cols = dataframe.columns,
      datetime_col = datetime_col_name
    )
  
  def plot_data_point_details(self, data: dict, latitude_cols: list[str], longitude_cols: list[str], datetime_cols: list[str], y_axis_cols: list[str], y_axis_label: str) -> None:
    """
    Creates a time-series plot for all data collected at the same latitude and longitude of the selected data point.
    Also creates another plot with all the geojson data that the selected data point was sampled from.

    Args:
      data (dict): Dictionary with details (file path, feature with popup info, etc.) about the hovered/clicked GeoJSON feature
      latitude_cols (list[str]): List of column names containing the latitude of the collected data (because data from different files might have different column names)
      longitude_cols (list[str]): List of column names containing the longitude of the collected data (because data from different files might have different column names)
      datetime_cols (list[str]): List of column names containing the date or time of the collected data (because data from different files might have different column names)
      y_axis_cols (list[str]): List of column names containing the time-series plot's y-axis values of the collected data (because data from different files might have different column names)
      y_axis_label (str): Label that appears for the y-axis of the time-series plot
    """
    # Gets the name of an existing dataframe column from the provided list of all possible column names.
    def get_existing_col_name(possible_col_names, dataframe_cols):
      for col_name in possible_col_names:
        if col_name in dataframe_cols: return col_name
      return None

    # Plot time-series for all collected data at the hovered/clicked data point's latitude-longitude coordinates.
    [selected_feature_long, selected_feature_lat] = data["feature"]["geometry"]["coordinates"]
    self.plot_time_series(
      latitude = selected_feature_lat,
      longitude = selected_feature_long,
      possible_lat_col_names = latitude_cols,
      possible_long_col_names = longitude_cols,
      possible_datetime_col_names = datetime_cols,
      possible_y_axis_col_names = y_axis_cols,
      y_axis_label = y_axis_label
    )
    
    # Plot original dataset that the hovered/clicked data point was sampled from.
    path = data["path"]
    dataframe_cols = data["feature"]["properties"].keys()
    [data_color] = [color for data_type, color in self.category_colors.items() if data_type in path]
    self.plot_original_dataset(
      data_path = path,
      x_axis_col_name = get_existing_col_name(latitude_cols, dataframe_cols),
      y_axis_col_name = get_existing_col_name(longitude_cols, dataframe_cols),
      datetime_col_name = get_existing_col_name(datetime_cols, dataframe_cols),
      data_point_color = data_color
    )