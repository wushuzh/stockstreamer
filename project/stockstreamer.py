from bokeh.plotting import figure, curdoc
from bokeh.models import Range1d, NumeralTickFormatter, DatetimeTickFormatter
from bokeh.models.sources import ColumnDataSource
from bokeh.palettes import Dark2
from bokeh.models.tools import (
    BoxZoomTool,
    HoverTool,
    PanTool,
    ResetTool,
    WheelZoomTool
)

import psycopg2
import pandas as pd
import numpy as np


hover = HoverTool(tooltips=[('Stock Name', '@stock_name'),
                            ('Time', '@timestamp'),
                            ('Price', '@y')])
tools = [PanTool(), BoxZoomTool(), ResetTool(), WheelZoomTool(), hover]

p = figure(title="STOCKSTREAMER v0.0",
           plot_width=1000, plot_height=680,
           x_range=Range1d(0, 1), y_range=Range1d(-50, 1200),
           tools=tools,
           toolbar_location='below', toolbar_sticky=False)

dburl = "postgres://postgres:postgres@192.168.99.100:5432/stocks"
conn = psycopg2.connect(dburl)

image_urls = pd.read_sql("""
    SELECT * FROM stock_image_urls;
    """, conn)
image_urls.set_index('stock_name', inplace=True)

stock_highlow = pd.read_sql("""
    SELECT * FROM stock_highlow;
    """, conn)
stock_highlow.set_index('stock_name', inplace=True)


def get_data():
    """helper function to return stock data from last 7 days
    """
    df = pd.read_sql("""
    SELECT * FROM stock_prices
    WHERE time >= NOW() - '7 day'::INTERVAL
    """, conn)

    df['important_indices'] = df.groupby('stock_name')['price'].diff() != 0
    df['important_indices'] = (df['important_indices'] != 0) \
        | (df.groupby('stock_name')['important_indices'].shift(-1))

    df = df.loc[df.important_indices, ]

    grouped = df.groupby('stock_name')
    unique_names = df.stock_name.unique()
    ys = [grouped.get_group(stock)['price'] for stock in unique_names]
    xs = [grouped.get_group(stock)['time'] for stock in unique_names]
    max_ys = [np.max(y) for y in ys]

    return (xs, ys, max_ys, unique_names)


xs, ys, max_ys, unique_names = get_data()
lines = []
recs = []

name_mapper = dict(AAPL='Apple', AMZN='Amazon', BABA='Alibaba',
                   FB='Facebook', GOOGL='Google')

# set axis labels and other figure properties
p.yaxis.axis_label = "Price ($US)"
p.yaxis.axis_label_text_font_size = '12pt'
p.yaxis[0].formatter = NumeralTickFormatter(format="$0")
p.xaxis[0].formatter = DatetimeTickFormatter()
p.background_fill_color = "#F0F0F0"
p.title.text_font = "times"
p.title.text_font_size = "16pt"

line_colors = Dark2[6]
line_dashes = ['solid'] * 6

for i, (x, y, max_y, name) in enumerate(zip(xs, ys, max_ys, unique_names)):
    source = ColumnDataSource(dict(
        x=x,
        y=y,
        timestamp=[a.strftime('%Y-%m-%d %H-%M-%S') for a in x],
        stock_name=[name_mapper[name]] * len(x)))

    lines.append(p.line(
        x='x',
        y='y',
        line_alpha=1,
        line_color=line_colors[i],
        line_dash=line_dashes[i],
        line_width=2,
        source=source))

    # The `hbar` parameters are scalars instead of lists,
    # but we create a ColumnDataSource so they can be easily modified later
    hbar_source = ColumnDataSource(dict(
        y=[(stock_highlow.loc[name, 'high_val52wk']
            + stock_highlow.loc[name, 'low_val52wk']
            ) / 2],
        left=[0],
        right=[x.max()],
        height=[[(stock_highlow.loc[name, 'high_val52wk']
                  - stock_highlow.loc[name, 'low_val52wk'])]],
        fill_alpha=[0.1],
        fill_color=[line_colors[i]],
        line_color=[line_colors[i]]))

    recs.append(p.hbar(y='y', left='left', right='right', height='height',
                       fill_alpha='fill_alpha', fill_color='fill_color',
                       line_alpha=0.1, line_color='line_color',
                       line_dash='solid', line_width=0.1,
                       source=hbar_source))


# Adjust the x view based upon the range of the data
time_range = xs[0].max() - xs[0].min()
p.x_range.start = np.min(xs[0]) - time_range * 0.1
p.x_range.end = np.max(xs[0])

curdoc().add_root(p)


def update_figure():
    xs, ys, max_ys, unique_names = get_data()
    for i, (x, y, max_y, name) in enumerate(zip(xs, ys, max_ys, unique_names)):
        lines[i].data_source.data.update(
            x=x,
            y=y,
            stock_name=[name_mapper[name]] * len(x),
            timestamp=[a.strftime('%Y-%m-%d %H-%M-%S') for a in x])
        recs[i].data_source.data.update(left=[0], right=[x.max()])


update_figure()
curdoc().add_periodic_callback(update_figure, 5000)

