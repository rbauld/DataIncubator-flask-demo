"""
This test application was built using this tutorial: http://biobits.org/bokeh-flask.html
In addition to the candle plot example on the bokeh site: https://bokeh.pydata.org/en/latest/docs/gallery/candlestick.html
"""


from flask import Flask, render_template, request, redirect
import datetime
import dateutil.relativedelta
import urllib2
import pandas as pd
from math import pi
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from bokeh.resources import INLINE
import os

api_key = os.environ.get('API_KEY')

def get_market_list():
    uri = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.csv?api_key=' + api_key + '&date=2017-12-20'
    test = pd.read_csv(uri)
    return list(test['ticker'].unique())


def get_market_data(ticker):
    """Gets market data from given ticker for last month"""
    current_date = datetime.date.today()
    past_date = current_date + dateutil.relativedelta.relativedelta(months=-1)
    uri = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.csv?api_key=' + api_key + '&ticker={}' + '&date.gte={}' + '&date.lte={}'
    uri = uri.format(*(ticker, past_date.isoformat(), current_date.isoformat()))
    return pd.read_csv(uri)


def create_figure(ticker):
    data_df = get_market_data(ticker)

    df = data_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    inc = df.close > df.open
    dec = df.open > df.close
    w = 12 * 60 * 60 * 1000  # half day in ms

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title="MSFT Candlestick")
    p.xaxis.major_label_orientation = pi / 4
    p.grid.grid_line_alpha = 0.3

    p.segment(df.date, df.high, df.date, df.low, color="black")
    p.vbar(df.date[inc], w, df.open[inc], df.close[inc], fill_color="#D5E1DD", line_color="black")
    p.vbar(df.date[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")

    return p

app = Flask(__name__)

market_list = get_market_list()
current_feature_name = "A"

# Index page
@app.route('/')
def index():

    current_feature_name = request.args.get("feature_name")

    if current_feature_name is None:
        current_feature_name = "A"

    # Create the plot
    plot = create_figure(current_feature_name)

    # Embed plot into HTML via Flask Render
    script, div = components(plot)

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    return render_template("embed.html", script=script, div=div,
                           js_resources=js_resources,
                           css_resources=css_resources,
                           current_feature_name=current_feature_name,
                           feature_names=market_list)

if __name__ == '__main__':
    app.run(port=33507)
