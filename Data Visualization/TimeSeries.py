import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool

class TimeSeries:
  def __init__(self):
    # Create placeholder plot with no data so that it can be rendered in a Panel modal.
    self.plot = figure(title = "Time-Series", x_axis_type="datetime")
    
    # Add placeholder hover tool to display data info in tooltips when hovering over a data point.
    self.hover_tool = HoverTool()
    self.plot.add_tools(self.hover_tool)

  def plot_data(self, data_path: str, datetime_col_name: str, y_axis_label: str, y_axis_col_name: str, tooltip_vals: dict, x_axis_label: str = "Time") -> None:
    """
    Plots given data as a time-series graph.

    Args:
      data_path (str): path to a directory containing data that needs to be plotted
      datetime_col_name (str): name of the column containing the date or time that the data was collected
      y_axis_label (str): name for the plot's y-axis
      y_axis_col_name (str): name of the column containing data values for the y-axis
      tooltip_vals (dict): Dictionary with labels that appear in a tooltip as keys and column names corresponding to their data as values
      x_axis_label (str): optional name for the plot's x-axis

    """
    # Plot the given data on the scatter plot.
    dataframe = pd.read_csv(data_path)
    dataframe[datetime_col_name] = pd.to_datetime(dataframe[datetime_col_name])
    new_source = ColumnDataSource(dataframe)
    self.plot.xaxis.axis_label = x_axis_label
    self.plot.yaxis.axis_label = y_axis_label
    self.plot.scatter(
      x = datetime_col_name, y = y_axis_col_name, source = new_source,
      size = 12, fill_alpha = 0.4,
      # legend_field = "species",
      # marker = factor_mark("species", MARKERS, SPECIES),
      # color = factor_cmap("species", "Category10_3", SPECIES)
    )
    
    # Modify tooltips to reflect given data.
    # self.hover_tool.tooltips = [(label, "@" + col_name) for label, col_name in tooltip_vals.items()]
    self.hover_tool.tooltips = [(col, "@" + col) for col in dataframe.columns]