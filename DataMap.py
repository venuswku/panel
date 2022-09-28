from collections import defaultdict
from ipywidgets import Layout, HTML
from ipyleaflet import Map, basemaps, basemap_to_tiles, GeoJSON, LayersControl, Popup, FullScreenControl, ScaleControl, LegendControl
import pandas as pd
import geopandas
import json

class DataMap(object):
  def __init__(self, map_center: list = [0, 0], basemap_options: dict = {}, legend: dict = None) -> None:
    """
    Creates a new instance of the DataMap class.

    Args:
      basemap_options (dict): Dictionary mapping basemap names (keys) to basemap layers (values)
    """

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
    
    # all_layers = {name1: layer1, name2: layer2, ...} dictionary to store all possible layers that could be on the map
    # ^ e.g. {
    #   "ew15_july_topo.txt": GeoJSON layer 1,
    #   "ew16_july_topo.txt": GeoJSON layer 2,
    #   "Default": default tile layer,
    #   "Satellite": satellite tile layer,
    #   ...
    # }
    self.all_layers = defaultdict(lambda: None)

    # popup_content_dict = dictionary mapping labels that appear on the popup (keys) to lists containing dataframe column names or units that match the label (values)
    # ^ e.g. {
    #   "Date & Time Collected": ["Date", "Time", (" UTC")],
    #   "Orthometric Height": [{"Ortho_Ht_m": "meters", "Ortho_ht_km": "kilometers", "ortho_ht_m": "meters"}]
    # }
    # ^ column names for the needed data are strings ""
    # ^ units or any other text are placed in tuples ()
    # ^ values that have different column names in different files are listed in dictionaries {}, where keys are possible column names and values are units for the value (empty string "" if you don't want to include units)
    self.popup_content_dict = {}
    # popup = popup that displays information about a data point
    self.popup = Popup(
      location = None,
      child = HTML(),
      min_width = 300, max_width = 500,
      auto_close = False, name = "Popup"
    )
    self.map.add_layer(self.popup)

    # Add and save all basemaps to the map first in order to update the visibility of their tile layers later.
    for name, basemap in basemap_options.items():
      tile_layer = basemap_to_tiles(basemap)
      tile_layer.show_loading, tile_layer.name = True, name
      # # When the default tile/basemap layer finishes loading, filter for the default selected data type layers.
      # if name == basemap_select.value: tile_layer.on_load(filter_data_on_map)
      # # Make the other unselected basemaps invisible.
      # else: tile_layer.visible = False
      tile_layer.visible = False
      self.map.add_layer(tile_layer)

  def get_existing_property(possible_prop_names_and_units: dict, feature_info: dict) -> str:
    """
    Gets the value and optional unit of an existing property from a GeoJSON feature.

    Args:
      possible_prop_names_and_units (dict): Dictionary mapping possible names for the existing property (keys) to optional units corresponding to the property (values)
      feature_info (dict): Dictionary mapping all properties for a GeoJSON feature to their values

    Returns:
      str: Value of the existing property and its optional unit
    """
    for prop_name, prop_unit in possible_prop_names_and_units.items():
      if prop_name in feature_info:
        return str(feature_info[prop_name]) + " " + prop_unit
    return "N/A"

  def get_label_vals(self, values: list[any], feature_info: dict) -> str:
    """
    Gets label values that are displayed in the popup.

    Args:
      values (list[any]): 
      feature_info (dict): Dictionary mapping all properties for a GeoJSON feature to their values

    Returns:
      str: Values for a label in the popup
    """
    label_values = ""
    for val in values:
      type = type(val)
      # If the value is a tuple, simply add the tuple value(s) to the returned result because it contains a unit or some literal text.
      if type is tuple:
        label_values += "".join(val)
      # Else if the value is a dictionary, which contains all the possible feature properties and corresponding units for a label, so find and add the value of the existing property.
      elif type is dict:
        label_values += self.get_existing_property(feature_info, val)
      # Else the value is a string, which contains the name of an existing dataframe column, so append feature_info[val]. 
      else:
        label_values += feature_info[val]
    return label_values

  def get_dataframe_col(possible_col_names: list[str], dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Gets the specified column of a dataframe.

    Args:
      possible_col_names (list[str]): List of possible names for the specified column
      dataframe (pandas.DataFrame): Two-dimensional (N columns by N rows) data structure that the specified column should be stored in

    Returns:
      pandas.DataFrame: Specified data column
    """
    for col_name in possible_col_names:
      if col_name in dataframe:
        print("found", col_name)
        return dataframe[col_name]

  def display_popup_info(self, feature: "geojson.Feature", **kwargs: dict) -> None:
    """
    Opens the popup at the location of the hovered/clicked GeoJSON feature.

    Args:
      feature (geojson.Feature): GeoJSON feature for the data point that had a mouse event
      kwargs (dict): Other arguments of a mouse event
    """
    self.popup.location = list(reversed(feature["geometry"]["coordinates"]))
    self.popup.child.value = ""
    for label, values in self.popup_content_dict.items():
      self.popup.child.value += "<b>{}</b> {}<br>".format(label, self.get_label_vals(values, feature["properties"]))
    self.popup.open_popup(location=self.popup.location)
  
  def create_geojson_layer(self, data_path: str, layer_name: str, info: dict, longitude_col_names: list[str], latitude_col_names: list[str], point_style: dict = {}, hover_style: dict = {}) -> None:
    """
    Creates and adds a GeoJSON layer containing data points to the map.

    Args:
      data_path (str): Path to the file that contains the layer's data points
      layer_name (str): Name of the newly added GeoJSON layer
      info (dict): Content displayed in a popup when hovering or clicking on a data point
      longitude_col_names (list[str]): Possible names of the column containing the longitude of each data point
      latitude_col_names (list[str]): Possible names of the column containing the latitude of each data point
      point_style (dict): Styling for each data point in the GeoJSON layer
      hover_style (dict): Styling for each data point in the GeoJSON layer when a user hovers over it with their cursor
    """
    # Convert the data file into a GeoJSON.
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
    self.all_layers[layer_name] = geojson
  
  def add_geojson_layer(self, layer_name: str) -> None:
    """
    Adds a GeoJSON layer to the map.

    Args:
      layer_name (str): Name of a layer to add to the map
    """
    if layer_name in self.all_layers:
      self.map.add_layer(self.all_layers[layer_name])

  def remove_geojson_layer(self, layer_name: str) -> None:
    """
    Removes a GeoJSON layer from the map.

    Args:
      layer_name (str): Name of a layer to remove from the map
    """
    if layer_name in self.all_layers:
      self.map.remove_layer(self.all_layers[layer_name])

  # def filter_data_on_map(event):
  #   """
  #   Filters data based on what data the user wants to view.
    
  #   """
  #   selected_data_types = elwha_data_multi_choice.value
  #   (selected_start_date, selected_end_date) = data_date_range_slider.value
  #   start_month, start_day, start_year = selected_start_date.month, selected_start_date.day, selected_start_date.year
  #   end_month, end_day, end_year = selected_end_date.month, selected_end_date.day, selected_end_date.year
  #   for data_type in elwha_data_types:
  #     for layer in elwha_map_layers[data_type]:
  #       # Add the data layer if it isn't in map yet.
  #       if (data_type in selected_data_types) and (layer not in elwha_map.layers):
  #         # print("display", layer.name)
  #         elwha_map.add_layer(layer)
  #       # Else remove the data layer if user didn't select to display it and its data is in the map.
  #       elif (data_type not in selected_data_types) and (layer in elwha_map.layers):
  #         # print("remove", layer.name)
  #         elwha_map.remove_layer(layer)
  #   print("filter")