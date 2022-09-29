from ipyleaflet import Map, basemap_to_tiles, GeoJSON, LayersControl, Popup, FullScreenControl, ScaleControl, LegendControl
from collections import defaultdict
from ipywidgets import Layout, HTML
import pandas as pd
import geopandas
import json
import math

class DataMap:
  def __init__(self, map_center: tuple, basemap_options: dict = {}, data: list[str] = [], legend: dict = None) -> None:
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
    #   "Date & Time Collected": ["Date", "Time", [" UTC"]],
    #   "Orthometric Height": [{"Ortho_Ht_m": "meters", "Ortho_ht_km": "kilometers", "ortho_ht_m": "meters"}]
    # }
    # ^ column names for the needed data are strings ""
    # ^ units or any other text are placed in lists []
    # ^ values that have different column names in different files are listed in dictionaries {}, where keys are possible column names and values are units for the value (empty string "" if you don't want to include units)
    self.popup_content_dict = {}
    # popup = popup that displays information about a data point
    self.popup = Popup(
      child = HTML(),
      min_width = 300, max_width = 500,
      auto_close = False, name = "Popup"
    )
    self.map.add_layer(self.popup)

    # basemaps = list containing all basemap names that the user could choose from
    self.basemaps = basemap_options.keys()
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
      self.all_layers[name] = tile_layer
    
    # Add all possible data layers to the map (initially no features) since map currently can't be updated once rendered on Panel app.
    # ^ Will modify GeoJSON layer's data property when its data needs to be displayed.
    for file in data:
      self.map.add_layer(GeoJSON(data={"type": "FeatureCollection", "features": []}, name=file, point_style={}, hover_style={}))

  def get_existing_property(self, possible_prop_names_and_units: dict, feature_info: dict) -> str:
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
      val_type = type(val)
      # If the value is a list, simply add the list value(s) to the returned result because it contains a unit or some literal text.
      if val_type is list:
        label_values += "".join(val)
      # Else if the value is a dictionary, which contains all the possible feature properties and corresponding units for a label, so find and add the value of the existing property.
      elif val_type is dict:
        label_values += self.get_existing_property(val, feature_info)
      # Else the value is a string, which contains the name of an existing dataframe column, so append feature_info[val]. 
      else:
        label_values += str(feature_info[val])
    return label_values

  def get_dataframe_col(self, possible_col_names: list[str], dataframe: pd.DataFrame) -> pd.DataFrame:
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
        return dataframe[col_name]

  def display_popup_info(self, feature: "geojson.Feature", **kwargs: dict) -> None:
    """
    Opens the popup at the location of the hovered/clicked GeoJSON feature.

    Args:
      feature (geojson.Feature): GeoJSON feature for the data point that had a mouse event
      kwargs (dict): Other keyword arguments of a mouse event
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
    for layer in self.map.layers:
      if layer.name == layer_name:
        # Convert the data file into a GeoJSON.
        dataframe = pd.read_csv(data_path)
        geodataframe = geopandas.GeoDataFrame(
          dataframe,
          geometry = geopandas.points_from_xy(
            self.get_dataframe_col(longitude_col_names, dataframe),
            self.get_dataframe_col(latitude_col_names, dataframe),
            crs = "EPSG:4326"
          )
        )
        geojson_str = geodataframe.to_json()
        # geojson = GeoJSON(
        #   data = json.loads(geojson_str),
        #   point_style = point_style,
        #   hover_style = hover_style,
        #   name = layer_name
        # )
        layer.data = json.loads(geojson_str)
        layer.point_style = point_style
        layer.hover_style = hover_style
        # Add mouse event handlers.
        self.popup_content_dict = info
        # geojson.on_click(self.display_popup_info)
        # geojson.on_hover(self.display_popup_info)
        layer.on_click(self.display_popup_info)
        layer.on_hover(self.display_popup_info)
        # # Add GeoJSON layer to map and save it.
        # self.map.add_layer(geojson)
        # self.all_layers[layer_name] = geojson
        break

    # Group data from the same location into clusters.
    # marker_cluster, cluster_location = MarkerCluster(name="Clusters"), None
    # for (index, row) in dataframe.iterrows():
    #   marker_lat, marker_long = get_latitude(row), get_longitude(row)
    #   cluster_lat, cluster_long = round(marker_lat, 4), round(marker_long, 4)
    #   marker = Marker(location=[marker_lat, marker_long], visible=
    # False)
    #   # Add new marker cluster to map when the coordinates don't belong to the current cluster.
    #   if (cluster_location is not None) and (not math.isclose(cluster_lat, cluster_location[0]) or not math.isclose(cluster_long, cluster_location[1])):
    #     # print("new cluster at " + str(cluster_location) + " is added to the map")
    #     elwha_map.add_layer(marker_cluster)
    #     marker_cluster, cluster_location = MarkerCluster(name="Clusters"), [cluster_lat, cluster_long]
    #   # Else add marker to the current cluster.
    #   else:
    #     if cluster_location is None: cluster_location = [cluster_lat, cluster_long]
    #     # print("marker at [" + str(marker_lat) + ", " + str(marker_long) + "] is added to the current cluster at " + str(cluster_location))
    #     marker_cluster.markers += (marker,)
    # elwha_map.add_layer(marker_cluster)     # need to add last marker cluster because last marker/row in dataframe will be added to last cluster but for loop never adds the cluster to the map
  
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

  def update_basemap(self, event: dict) -> None:
    """
    Updates the visibility of all basemap tile layers in order to display the newly selected basemap.

    Args:
      event (dict): information on an event that gets fired when the selected basemap value changes
    """
    newly_selected_basemap = event.new
    for basemap_name in self.basemaps:
      basemap_tile_layer = self.all_layers[basemap_name]
      # # Remove the filtering data callback function (only need to execute it once at the beginning of loading the default basemap).
      # basemap_tile_layer.on_load(callback=filter_data_on_map, remove=True)
      if basemap_tile_layer.name == newly_selected_basemap: basemap_tile_layer.visible = True
      else: basemap_tile_layer.visible = False