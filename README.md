## Create an Environment with Anaconda
Create a new environment named `mypanelintro` with all the required packages by entering the following commands in succession into Anaconda Prompt (Windows) or Terminal (Mac/Linux):\
Skip the command `conda install "ipywidgets<8" -y` if you installed Panel with a version >= `0.14.0`.
```
conda create -n mypanelintro
conda activate mypanelintro
# Install Panel dependencies.
conda install "ipywidgets<8" -y
conda install -c bokeh ipywidgets_bokeh -y
conda install -c conda-forge panel -y
# Install other optional dependencies for experimenting with Panel.
conda install -c conda-forge ipyleaflet jupyter pandas geopandas -y
conda install -c pyviz hvplot bokeh -y
```

## Launch Jupyter Notebook as a Web Server
- Make sure your Anaconda environment is activated by running `conda activate mypanelintro` in your terminal.
- Run the command `panel serve --show --autoreload app.ipynb` in your terminal.
- A webpage with the URL http://localhost:5006/app will display all Panel objects marked with `.servable()`.
- Any changes in the notebook will automatically be reflected on the webpage. Just in case, refresh the webpage to make sure you see your latest changes.
- If you installed Panel with a version lower than `0.14.0`, make sure the installed `ipywidgets` package in your environment is lower than version `8.0.1`.
  - See reason for `ipywidgets<8` here: https://github.com/holoviz/panel/issues/3778#issue-1349757718.
  - Check the version of your installed packages by running `conda list`.

## Launch Jupyter Notebook
- Make sure your Anaconda environment is activated by running `conda activate mypanelintro` in your terminal.
- Run the command `jupyter notebook` in your terminal.
- Open the `app.ipynb` file when a webpage with the URL http://localhost:8888/tree appears.
- Run all the notebook cells from top to bottom. The Panel app will be outputted after the last cell is run.
- Reload the [`app.ipynb` webpage](http://localhost:8888/notebooks/app.ipynb) when you want to see your new changes.

## Learning Resources
Panel
- [Widgets](https://panel.holoviz.org/user_guide/Widgets.html)
- [Components](https://panel.holoviz.org/user_guide/Components.html)
- [Dashboards Introduction](https://youtu.be/AXpjbJUVeb4)
- [Python Introduction to Panel Widgets and Dashboards](https://youtu.be/ulHnNXNmuig)

`data` Folder
- [`data` Folder's GeoJSON Files](https://zenodo.org/record/7033367)
- [Sample `csv` (Comma Separated Values, aka Excel) File from CoastTrain](https://github.com/dbuscombe-usgs/CoastTrainMetaPlots/tree/main/metadata)
- [Sample Data from `bokeh`](https://docs.bokeh.org/en/latest/docs/reference/sampledata.html)
- [Elwha Topo-Bathy Data](https://www.sciencebase.gov/catalog/item/5a01f6d0e4b0531197b72cfe)

`bokeh.plotting`
- [`figure()` Documentation](https://docs.bokeh.org/en/latest/docs/reference/plotting/figure.html)
- [Plotting `pandas` DataFrame with `bokeh.plotting`](https://programminghistorian.org/en/lessons/visualizing-with-bokeh#the-bokeh-columndatasource)
- [Modifying Markers in Scatter Plot](https://docs.bokeh.org/en/2.4.0/docs/user_guide/data.html#mapping-marker-types)
- [`scatter()` to Use Built-In Markers](https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/scatter.html)
- [`DatetimeTickFormatter` to Format Ticks on Plot Axes](https://docs.bokeh.org/en/2.4.1/docs/reference/models/formatters.html#datetimetickformatter)

`pandas`
- [Filtering through DataFrame with `.loc`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html)

Other Documentation
- [`ipyleaflet`](https://ipyleaflet.readthedocs.io/en/latest/index.html)
- [`datetime`](https://docs.python.org/3/library/datetime.html#datetime-objects)
- [`ipywidgets`](https://ipywidgets.readthedocs.io/en/7.x/)