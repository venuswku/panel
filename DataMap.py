from collections import defaultdict
from ipywidgets import Layout, HTML
from ipyleaflet import Map, basemap_to_tiles, GeoJSON, LayersControl, Popup, FullScreenControl, ScaleControl, LegendControl
import pandas as pd
import geopandas
import json

class DataMap:
  def __init__(self, map_center: list = [48.148, -123.553], data_types: list = [], legend: dict = None):
    # all_possible_layers = {layer_type: [(name1, layer1), (name2, layer2), ...]} dictionary to store all layers that could be on the map
    # ^ e.g. {
    #   "Topography": [
    #     ("ew15_july_topo.txt", GeoJSON layer 1),
    #     ("ew16_july_topo.txt", GeoJSON layer 2,
    #     ...
    #   ],
    #   "Basemap": [
    #     ("Default", default tile layer),
    #     ("Satellite", satellite tile layer),
    #     ...
    #   ]
    # }
    self.all_possible_layers = defaultdict(list)
    
    # data_types = list of directories to get map data from
    self.data_types = data_types

    # map = map containing data that user wants to visualize
    self.map = Map(
      center = map_center,
      zoom = 15, max_zoom = 18, layout = Layout(height="100vh")
    )
    self.map.add_control(ScaleControl(position="bottomleft"))
    if legend:
      self.map.add_control(
        LegendControl(
          name = legend["name"],
          position = "bottomright",
          legend = legend["colors"]
        )
      )
    self.map.add_control(FullScreenControl())
    self.map.add_control(LayersControl(position="topright"))

    # popup_content_dict = dictionary mapping labels that appear on the popup (keys) to lists containing dataframe column names or units that match the label (values)
    # ^ e.g. {
    #   "Date & Time Collected": ["Date", "Time", (" UTC")],
    #   "Sample Type": ["type"]
    # }
    # ^ column names for the needed data are strings ""
    # ^ units or any other text are placed in tuples ()
    self.popup_content_dict = {}
    # popup = popup that displays information about a data point
    self.popup = Popup(
      location = None,
      child = HTML(),
      min_width = 300, max_width = 500,
      auto_close = False, name = "Popup"
    )
    self.map.add_layer(self.popup)

  def get_label_vals(self, values: list[any], feature_info: dict) -> str:
    """
    
    """
    label_values = ""
    for val in values:
      # If the value is a tuple, simply add the tuple value(s) to the returned result because it contains a unit or some literal text.
      if type(val) is tuple:
        label_values += "".join(val)
      else:
        label_values += feature_info[val]
    return label_values

  def display_popup_info(self, feature: "geojson.Feature", **kwargs) -> None:
    """
    Opens the popup at the location of the hovered/clicked GeoJSON feature.

    Args:
      feature (): GeoJSON feature for the data point that had a mouse event
      kwargs: Other arguments of a mouse event
    """
    self.popup.location = list(reversed(feature["geometry"]["coordinates"]))
    self.popup.child.value = ""
    for label, values in self.popup_content_dict.items():
      self.popup.child.value += "<b>{}</b> {}<br>".format(label, self.get_label_vals(values, feature["properties"]))
    self.popup.open_popup(location=self.popup.location)

  def get_dataframe_col(dataframe: pd.DataFrame, possible_col_names: list[str]) -> pd.DataFrame:
    """
    Gets the specified column of a dataframe.

    Args:
      dataframe (pandas.DataFrame): Two-dimensional data structure that the specified column should be stored in
      possible_col_names (list[str]): List of possible names for the specified column

    Returns:
      pandas.DataFrame: Specified data column
    """
    for col_name in possible_col_names:
      if col_name in dataframe:
        return dataframe[col_name]
  
  def add_geojson_layer(self, data_path: str, layer_name: str, info: dict, longitude_col_names: list[str], latitude_col_names: list[str], point_style: dict = {}, hover_style: dict = {}) -> None:
    """
    Adds a GeoJSON layer containing data points to the map.

    Args:
      data_path (str): Path to the file that contains the layer's data points
      layer_name (str): Name of the newly added GeoJSON layer
      info (dict): Content displayed in a popup when hovering or clicking on a data point
      longitude_col_names (list[str]): Possible names of the column containing the longitude of each data point
      latitude_col_names (list[str]): Possible names of the column containing the latitude of each data point
      point_style (dict): Styling for each data point in the GeoJSON layer
      hover_style (dict): Styling for each data point in the GeoJSON layer when a user hovers over it with their cursor
    """
    dataframe = pd.read_csv(data_path)
    geodataframe = geopandas.GeoDataFrame(
      dataframe,
      geometry = geopandas.points_from_xy(
        self.get_dataframe_col(dataframe, longitude_col_names),
        self.get_dataframe_col(dataframe, latitude_col_names)
      )
    )
    geojson_str = geodataframe.to_json()
    geojson = GeoJSON(
      data = json.loads(geojson_str),
      point_style = point_style,
      hover_style = hover_style,
      name = layer_name
    )
    # Add mouse event handlers.
    self.popup_content_dict = info
    geojson.on_click(self.display_popup_info)
    geojson.on_hover(self.display_popup_info)
    # Add GeoJSON layer to map and save it.
    self.map.add_layer(geojson)