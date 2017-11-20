from bokeh.plotting import figure, curdoc
from bokeh.models import Range1d


p = figure(title="STOCKSTREAMER v0.0",
           plot_width=1000, plot_height=680,
           x_range=Range1d(0, 1), y_range=Range1d(-50, 1200),
           toolbar_location='below', toolbar_sticky=False)

curdoc().add_root(p)
