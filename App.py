import os
import pandas as pd 
import plotly.express as px 
import plotly.graph_objects as go 
import numpy as np 
from datetime import datetime as dt 
import json

import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/slate/bootstrap.min.css']

app = dash.Dash(__name__, 
meta_tags={
    'name': 'viewport', 'content':'width=device-width, initial-scale=1'
})
server = app.server

CURRENT_DIR = os.path.dirname(__file__)
file_path = os.path.join(CURRENT_DIR, 'Apple Music Activity v2.csv')

df = pd.read_csv(file_path)
df.dropna(thresh = 2)

fdf = df.groupby(['Apple Music Subscription', 'Artist Name', 'Content Name', 'Content Provider', 'Content Specific Type', 'End Reason Type', 'Event Start Timestamp', 'Feature Name', 'Genre'])['Store Country Name'].count().reset_index()
fdf = fdf.replace("`|’", "'", regex=True)
fdf = fdf.rename(columns = {'Store Country Name':'Play Count','Artist Name':'Artist','Content Name':'Song'})
fdf.loc[fdf['Genre'].str.contains('Metal'), 'Genre'] = 'Metal'
fdf.loc[fdf['Genre'].str.contains('Rock'), 'Genre'] = 'Rock'
fdf.loc[fdf['Genre'].str.contains('Rap'), 'Genre'] = 'Hip Hop/Rap'
fdf.loc[fdf['Genre'].str.contains('Hip'), 'Genre'] = 'Hip Hop/Rap'
fdf.loc[fdf['Genre'].str.contains('Country'), 'Genre'] = 'Country'
fdf.loc[fdf['Genre'].str.contains('Alternative'), '"genre'] = 'Alternative'
fdf.loc[fdf['Genre'].str.contains('R&B'), 'Genre'] = 'R&B/Soul'
fdf.loc[fdf['Genre'].str.contains('Pop'), 'Genre'] = 'Pop'
fdf = fdf[fdf['Apple Music Subscription'] == True]

fdf['Date'] = pd.to_datetime(fdf['Event Start Timestamp'])
fdf['Year'] = fdf['Date'].apply(lambda datetime: datetime.year)
fdf['Month'] = fdf['Date'].apply(lambda datetime: datetime.month)
fdf['Weekday'] = fdf['Date'].apply(lambda datetime: datetime.weekday())
fdf['Time'] = fdf['Event Start Timestamp'].str.split('T').str[-1]
fdf['Time'] = fdf['Time'].str[:5]

weekdayn = []

for n in fdf['Weekday']:
    if n == 6:
        weekdayn.append('Sunday')
    elif n == 0:
        weekdayn.append('Monday')
    elif n == 1:
        weekdayn.append('Tuesday')
    elif n == 2:
        weekdayn.append('Wednesday')
    elif n == 3:
        weekdayn.append('Thursday')
    elif n == 4:
        weekdayn.append('Friday')
    else:
        weekdayn.append('Saturday')

fdf['Weekday Name'] = weekdayn

Timedf = fdf.copy()
Timedf['Time'] = Timedf['Time'].str[:2]
Timedf['Time'] = Timedf['Time'].replace('0','00')


top10 = fdf.groupby(['Genre'])['Play Count'].sum().reset_index().sort_values('Play Count', ascending = False).head(10)['Genre'].tolist()

song50 = fdf.groupby(['Artist','Song'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = True).head(50)['Song'].tolist()

app.layout = html.Div(
    children = [
        html.Div(
            className = 'row',
            children = [
                html.Div(
                    className = 'four columns div-user-controls bg-grey',
                    children = [
                        html.Img(
                            className = 'logo', src = app.get_asset_url('Apple_Music_Logo.png')
                        ),
                        
                        html.Div(
                            className= 'card',
                            children=[
                                html.H2('''Clint's Music - Data App'''),
                                html.P(
                                    dcc.Markdown(
                                        '''
                                        This web app shows the music listening history  
                                        from my Apple Music subscription.
                                        ''' 
                                    ),
                                ),
                                html.Br(),
                                html.H2('''How to use this app:'''),
                                html.P(
                                    dcc.Markdown(
                                        '''
                                        - Select a genre from the ten listed below.
                                        - Once selected, the two graphs will update.
                                        - The top graph visualises the top 7 artists of the genre selected.
                                        - The bottom graph visualises the top 10 songs of the genre **OR** artist selected.
                                        - To view the top ten songs by an artist, hover over an artist on the artist graph to view the top ten songs.
                                        '''
                                    ),
                                ),
                                html.Br(),
                            ],
                        ),
                        html.Br(),
                        html.Div(
                            className= 'row',
                            children=[
                                html.H4('Select a Genre:'),
                                html.Div(
                                    className = 'radio-toolbar',
                                    children = [
                                        dbc.RadioItems(
                                            className = 'radio-toolbar',
                                            id = 'genre-dropdown',
                                            options = [
                                                {'label': i, 'value': i} for i in top10
                                            ],
                                            value = top10[0],
                                        ),
                                    ],
                                ),
                                html.Br(),
                                html.Div(
                                    className= 'paragraph',
                                    children = [
                                        html.P(
                                            dcc.Markdown(
                                                '''
                                                ###### **This web app was designed using:**
                                                - Python, HTML & CSS  
                                                '''
                                            ),
                                        ),
                                        html.P(
                                            dcc.Markdown(
                                                '''
                                                *Web app source code link coming soon.*
                                                '''
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className='eight columns div-for-charts',
                    children=[
                        html.Div(
                            className='card-graph',
                            children=[
                                html.H3(
                                    id='artist-title',
                                    children=[
                                    ],
                                ),
                                dcc.Graph(
                                    id='artist-graph',
                                    hoverData={'points': [{'customdata': []}]},
                                    style={"height" : "40vh", "width" : "100%"}
                                ),
                            ],
                        ),
                        html.Div(
                            className='card-graph',
                            children=[
                                html.H3(
                                    id='song-ti',
                                    children=[
                                    ],
                                ),
                                dcc.Graph(
                                    id='song-graph',
                                    style={"height" : "40vh", "width" : "100%"}
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)
# ----------------------------------------------
@app.callback(
    Output('artist-graph', 'figure'),
    [Input('genre-dropdown', 'value')]
)

def update_artist_graph(genre_selected):
    print(genre_selected)
    print(type(genre_selected))

    tdf = fdf[fdf['Genre'] == genre_selected]
    tdf = tdf.groupby(['Artist', 'Genre'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = False)
    # top5 = tdf.groupby(['Artist'])['Play Count'].sum().reset_index().sort_values('Play Count', ascending = False).head(5)['Artist'].tolist()

    # tdf = tdf[tdf['Artist'].isin(top5)]
    fig = px.bar(
        tdf,
        x = 'Artist',
        y = 'Play Count',
        color = 'Play Count',
        color_continuous_scale = [(0,"#EA00FF"), (1,"#BD00FF")],
        template = 'plotly_dark',
        orientation = 'v',
        custom_data = ['Artist', 'Genre']
    )
    fig.update_traces(hovertemplate = '<br>'.join([
        'Artist: <b>%{x}</b>',
        'Genre: <b>%{customdata[1]}</b>',
        'Play Count: <b>%{y}</b>',
    ]))
    fig.update_xaxes(
        range=(-.5,6.5)
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale = False,
        margin = dict(b = 160)
    )
    fig.update_yaxes(
        {'showgrid': False}
    )


    return fig

# Clear Hover Data if Click Data is used

@app.callback(
    Output('song-graph', 'figure'),
    [Input('genre-dropdown', 'value'),
    Input('artist-graph', 'hoverData')]
)

def update_song_graph(genre_selected, hoverData):


    if genre_selected:

        sdf = fdf[fdf['Genre'] == genre_selected]
        sdf = sdf.groupby(['Artist', 'Song', 'Genre'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = False)
    if hoverData:

        genre_name = hoverData['points'][0]['customdata'][0]
        sdf = fdf[fdf['Artist'] == genre_name]
        sdf = sdf.groupby(['Artist','Song','Genre'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = False)
    #top15 = sdf.groupby(['Song'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = False).head(15)['Song'].tolist()
    #sdf = sdf[sdf['Song'].isin(top15)]

    fig = px.bar(
        sdf,
        x = 'Song',
        y = 'Play Count',
        color = 'Play Count',
        color_continuous_scale = [(0,"#EA00FF"), (1,"#BD00FF")],
        orientation = 'v',
        template = 'plotly_dark',
        custom_data = ['Song', 'Genre', 'Artist']
    )
    fig.update_layout(
        yaxis={'categoryorder':'category ascending'},
        margin = dict(b=200)
    )
    fig.update_traces(
        hovertemplate = '<br>'.join([
        'Song: <b>%{x}</b>',
        'Artist: <b>%{customdata[2]}</b>',
        'Genre: <b>%{customdata[1]}</b>',
        'Play Count: <b>%{y}</b>']),
    )
    fig.update_xaxes(
        range=(-.5,9.5)
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale = False,
    )
    fig.update_yaxes(
        {'showgrid': False}
        )

    return fig

@app.callback(
    Output('artist-graph', 'hoverData'),
    [Input('genre-dropdown', 'value')])

def update_selected_data(clickData):
    if clickData:
        return None

@app.callback(
    Output('artist-title','children'),
    [Input('genre-dropdown', 'value')])

def update_artist_title(artitle):
    if artitle:
        return 'Top ' + str(artitle) + ' Artists'

@app.callback(
    Output('song-ti', 'children'),
    [Input('artist-graph', 'hoverData'),
    Input('genre-dropdown', 'value')])

def update_song_title(hoverData, Gselect):

    if Gselect:
        sel = 'Top songs of ' + str(Gselect)


    if hoverData:
        genre_name = hoverData['points'][0]['customdata'][0]
        sel = 'Top songs by ' + str(genre_name)

    return sel

if __name__ == '__main__':
    app.run_server(debug = True, use_reloader = False)