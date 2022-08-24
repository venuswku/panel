## Create an Environment with Anaconda
Create a new environment named `mypanelintro` with all the required packages by entering the following commands in succession into Anaconda Prompt (Windows) or Terminal (Mac/Linux):
```
conda create -n mypanelintro
conda activate mypanelintro
conda install -c bokeh "ipywidgets_bokeh<8" -y
conda install -c conda-forge panel ipyleaflet jupyter -y
```

## Launch Jupyter Notebook as a Web Server
- Make sure your Anaconda environment is activated by running `conda activate mypanelintro` in your terminal.
- Run the command `panel serve --show --autoreload app.ipynb` in your terminal.
- A webpage with the URL http://localhost:5006/app will display all Panel objects marked with `.servable()`.
- Any changes in the notebook will automatically be reflected on the webpage.
- In order to serve on a webpage, make sure the installed `ipywidgets` package in your environment is lower than version `8`.
  - Check the version of your installed packages by running `conda list`.

## Learning Resources
[Panel Components](https://panel.holoviz.org/user_guide/Components.html)\
[Panel Dashboards Introduction](https://youtu.be/AXpjbJUVeb4)\
[Python Introduction to Panel Widgets and Dashboards](https://youtu.be/ulHnNXNmuig)
[ipyleaflet Documentation](https://ipyleaflet.readthedocs.io/en/latest/index.html)