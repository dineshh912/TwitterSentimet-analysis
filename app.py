import dash
from dash.dependencies import Output, Event, Input, State
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import sqlite3
import pandas as pd
import time


app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div(
        className = 'container-fluid',
        children =[html.H2('Live Twitter Sentiment', className = 'header-title')],
        ),
    html.Div(
        className = 'row search',
        children = [
            html.Div(
                className = 'col-md-4 mb-4',
                children = [html.H5('SearchTerm :', className = 'keyword')]
                     ),
            html.Div(
                className = 'col-md-4 mb-4',
                children = [
                    dcc.Input(id='sentiment_term', className = 'form-control', value='Twitter', type='text'),
                    html.Div(['example'], id='input-div', style={'display': 'none'}),
                    ]
                ),
            html.Div(
                className = 'col-md-4 mb-4',
                children = [
                    html.Button('Submit', id="submit-button" ,className = 'btn btn-success'),
                    ]
                ),
            ]
        ),
    html.Div(
        className = 'row',
        children = [
            html.Div(
                className = 'col-md-8 mb-8',
                children = [
                    dcc.Graph(id='live-graph', animate=False),
                    ]
                ),
            html.Div(
                className = 'col-md-4 mb-4',
                children = [
                    dcc.Graph(id='sentiment-pie', animate=False),
                    ]
                ),
            ]
        ),
    
      dcc.Interval(id='graph-update',
                   interval=1*1000
                ),
            ]
     )


@app.callback(Output('input-div', 'children'),
              [Input('submit-button', 'n_clicks')],
              state=[State(component_id='sentiment_term', component_property='value')])
def update_div(n_clicks, input_value):
    return input_value

@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'interval'),
               Input('input-div', 'children')],
              events=[Event('graph-update', 'interval')])
def update_graph_scatter(n, input_value):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 1000", conn ,params=('%' + input_value + '%',))
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()

        df['date'] = pd.to_datetime(df['unix'],unit='ms')
        df.set_index('date', inplace=True)

        df = df.resample('100ms').mean()
        df.dropna(inplace=True)
        
        X = df.index
        Y = df.sentiment_smoothed

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines+markers'
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[min(Y),max(Y)]),
                                                    title='{}'.format(input_value))}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')            

external_css = ["https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"]

for css in external_css:
    app.css.append_css({"external_url": css})


external_js = ['https://code.jquery.com/jquery-3.3.1.slim.min.js',
               'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js',
               'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js']

for js in external_js:
    app.scripts.append_script({'external_url': js})


if __name__ == '__main__':
    app.run_server(debug=True)
