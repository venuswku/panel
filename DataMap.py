from collections import defaultdict
from ipywidgets import Layout, HTML
from ipyleaflet import Map, basemap_to_tiles, GeoData, GeoJSON, LayersControl, Popup, FullScreenControl, ScaleControl, LegendControl

class DataMap:
  def __init__(self, map_center=[48.148, -123.553], data_types=[], legend=None):
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
      center=map_center,
      zoom=15, max_zoom=18, layout=Layout(height="100vh")
    )
    self.map.add_control(ScaleControl(position="bottomleft"))
    if legend:
      self.map.add_control(
        LegendControl(
          name=legend["name"],
          position="bottomright",
          legend=legend["colors"]
        )
      )
    self.map.add_control(FullScreenControl())
    self.map.add_control(LayersControl(position="topright"))

    # popup = popup that displays information about a data point
    self.popup = Popup(
      location=None,
      child=HTML(),
      min_width=300, max_width=500,
      auto_close=False, name="Popup"
    )
    self.map.add_layer(self.popup)

  