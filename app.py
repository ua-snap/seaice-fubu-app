import dash, os, glob, json, io, requests
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import cufflinks
import pandas as pd
import numpy as np
from collections import defaultdict

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# #  NSIDC-0051 Derived FUBU Data Explorer Tool                         # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def load_data():
    # load the data
    url = 'https://www.snap.uaf.edu/webshared/Michael/data/seaice_noaa_indicators/sic_daily_vals.csv'
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')), index_col=0, parse_dates=True)
    # df = pd.read_csv('sic_daily_vals.csv', index_col=0, parse_dates=True)
    url = 'https://www.snap.uaf.edu/webshared/Michael/data/seaice_noaa_indicators/winter_threshold_vals.csv'
    s = requests.get(url).content
    threshold = pd.read_csv(io.StringIO(s.decode('utf-8')), index_col=0, parse_dates=True)

    BUstart_lu_mark = {'1979':'1979-7-14','1980':'1980-7-7','1981':'1981-5-20','1982':'1982-5-27','1983':np.nan,'1984':'1984-6-30',
    '1985':'1985-7-11','1986':'1986-7-7','1987':'1987-5-4','1988':np.nan,'1989':'1989-7-2','1990':'1990-6-30',
    '1991':'1991-6-5','1992':'1992-7-3','1993':'1993-5-3','1994':np.nan,'1995':'1995-7-6','1996':'1996-7-5',
    '1997':'1997-7-5','1998':'1998-7-10','1999':'1999-4-27','2000':'2000-5-25','2001':'2001-7-14','2002':'2002-7-13',
    '2003':'2003-6-11','2004':'2004-5-11','2005':'2005-5-4','2006':'2006-7-8','2007':'2007-5-26','2008':'2008-7-7',
    '2009':'2009-6-2','2010':'2010-5-17','2011':'2011-5-14','2012':'2012-3-23',}

    # BUstart_lu_mike = { '1979': 'nan', '1980': '1980-7-08', '1981': '1981-6-19', '1982': '1982-6-07', '1983': 'nan',
    #  '1984': 'nan', '1985': 'nan', '1986': '1986-6-08', '1987': '1987-6-16', '1988': 'nan', '1989': '1989-7-09', 
    #  '1990': '1990-7-10','1991': 'nan', '1992': '1992-6-27', '1993': 'nan', '1994': 'nan', '1995': '1995-7-06', 
    #  '1996': '1996-7-09', '1997': '1997-7-07', '1998': '1998-5-20', '1999': '1999-4-28', '2000': 'nan', 
    #  '2001': 'nan', '2002': '2002-7-13', '2003': '2003-6-12', '2004': '2004-5-07', '2005': '2005-5-19', 
    #  '2006': 'nan', '2007': '2007-4-19', '2008': '2008-3-17', '2009': '2009-6-22', '2010': '2010-5-17', 
    #  '2011': '2011-5-12', '2012': 'nan'}
    BUstart_lu_mike = {'1979': np.nan,'1980': '1980-7-8','1981': '1981-6-19','1982': '1982-6-7','1983': np.nan,'1984': np.nan,
    '1985': np.nan,'1986': '1986-6-8','1987': '1987-6-16','1988': np.nan,'1989': '1989-7-9','1990': '1990-7-10',
    '1991': np.nan,'1992': '1992-6-27','1993': np.nan,'1994': np.nan,'1995': '1995-7-6','1996': '1996-7-9',
    '1997': '1997-7-7','1998': '1998-5-20','1999': '1999-4-28','2000': np.nan,'2001': np.nan,'2002': '2002-7-13',
    '2003': '2003-6-12','2004': '2004-5-7','2005': '2005-5-19','2006': np.nan,'2007': '2007-4-19','2008': '2008-3-17',
    '2009': '2009-6-22','2010': '2010-5-17','2011': '2011-5-12','2012': np.nan }

    return df, threshold, BUstart_lu_mark, BUstart_lu_mike

# load data
df, threshold, BUstart_lu_mark, BUstart_lu_mike = load_data()

mdown = '''
### Vertical and Horizontal lines reference:
    Black line = Winter Threshold (current year +1)
    Red line = Mark's BreakUp Start
    Green line = Michael's BreakUp Start
'''


app = dash.Dash(__name__)
server = app.server
server.secret_key = os.environ['SECRET-SNAP-KEY']
# server.secret_key = 'secret_key'
app.config.supress_callback_exceptions = True
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
app.title = 'SeaIce-FUBU'

years = df.index.map(lambda x: x.year).unique().tolist()
years = [i for i in years if i <= 2012]

# # BUILD PAGE LAYOUT
app.layout = html.Div([

                    html.Div([
                        html.H2('Explore NSIDC-0051 Sea Ice Concentration -- Break-Up Start'),
                        # html.H4('   with Computed Freeze-up/Break-Up Dates')
                        ]),
                    html.Div([
                        html.Div([
                            html.Label('Choose Year', style={'font-weight':'bold'})], className='two columns'),
                        html.Div([
                            dcc.Dropdown(
                                id='year-dropdown',
                                options=[ {'label':i, 'value':i} for i in years ],
                                value='1980',
                                multi=False )
                            ], className='three columns')
                    ], className='row'),
                    html.Div([dcc.Graph( id='my-graph' ) ] ),
                    html.Div([dcc.Markdown(mdown)])
                ])


@app.callback( Output('my-graph', 'figure'), 
            [Input('year-dropdown', 'value')])
def update_graph( year ):
    # pull data for the year we want to examine
    df_year = df.loc[str(year)+'-02-01':str(year)+'-08-01'].copy()*100
    threshyear = str(int(year)+1)
    thresh, = (threshold.loc[threshyear]['sic'].copy()*100)
    print(thresh)
    BUstart_mark = BUstart_lu_mark[str(year)]
    BUstart_mike = BUstart_lu_mike[str(year)]

    # make a plotly json object directly using cufflinks
    title = 'NSIDC-0051 Sea Ice Concentration {}'.format(year)

    # return a plotly figure using cufflinks
    # title = 'Sea Ice Concentration {} AK'.format(year)
    # vline1 = {'x':BUstart_mark,'color':'rgb(30,30,30)'}
    # vline2 = {'x':BUstart_mike,'color':'rgb(11,102,35)'}

    # working with threshold lines...
    # black
    threshline = {'line': {'color': '#000000', 'dash': 'solid', 'width': 2},
                       'type': 'line',
                       'x0': 0,
                       'x1': 1,
                       'xref': 'paper',
                       'y0': thresh,
                       'y1': thresh,
                       'yref': 'y'}
    # red
    markline = {'line': {'color': 'rgb(209, 25, 25)', 'dash': 'solid', 'width': 2},
                                   'type': 'line',
                                   'x0': BUstart_mark,
                                   'x1': BUstart_mark,
                                   'xref': 'x',
                                   'y0': 0,
                                   'y1': 1,
                                   'yref': 'paper',
                                   'text':'mark'}
    # green                                   # 
    mikeline = {'line': {'color': '#3daf41', 'dash': 'solid', 'width': 2},
                                   'type': 'line',
                                   'x0': BUstart_mike,
                                   'x1': BUstart_mike,
                                   'xref': 'x',
                                   'y0': 0,
                                   'y1': 1,
                                   'yref': 'paper'}

    shapes = {'threshline':threshline,'markline':markline,'mikeline':mikeline}
    if not isinstance(BUstart_mark, str):
        _ = shapes.pop('markline')
    if not isinstance(BUstart_mike, str):
        _ = shapes.pop('mikeline')

    return { 'data':[ 
                go.Bar(
                    x=df_year.index.tolist(),
                    y=df_year.sic.tolist(),
                    name='SIC',
                    ),
                ],
            'layout': { 
                    'title': title,
                    'xaxis': dict(title='Time'),
                    'yaxis': dict(title='% Concentration', range=[0,100]),
                    'shapes': list(shapes.values())
                        }
                    }


if __name__ == '__main__':
    app.run_server( debug=False )
