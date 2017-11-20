from bokeh.plotting import figure, curdoc
from bokeh.models import Range1d
from bokeh.models.sources import ColumnDataSource
from bokeh.palettes import Dark2

import psycopg2
import pandas as pd
import numpy as np


p = figure(title="STOCKSTREAMER v0.0",
           plot_width=1000, plot_height=680,
           x_range=Range1d(0, 1), y_range=Range1d(-50, 1200),
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

name_mapper = dict(AAPL='Apple', AMZN='Amazon', BABA='Alibaba',
                   FB='Facebook', GOOGL='Google')

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


# Adjust the x view based upon the range of the data
time_range = xs[0].max() - xs[0].min()
p.x_range.start = np.min(xs[0]) - time_range * 0.1
p.x_range.end = np.max(xs[0])

curdoc().add_root(p)

