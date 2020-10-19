# Import all libraries necessary

import os
import pandas as pd 
import plotly.express as px
import numpy as np 
from datetime import datetime as dt 
import json
import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_daq as daq

# external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/slate/bootstrap.min.css']

app = dash.Dash(__name__,
     meta_tags=[{'name': 'viewport',
                 'content': 'width=device-width, initial-scale=1.0'}]

)
server = app.server

# Initialise DataFrame and clean the data

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

monthn = []

for e in fdf['Month']:
    if e == 1:
        monthn.append('January')
    elif e == 2:
        monthn.append('Febuary')
    elif e == 3:
        monthn.append('March')
    elif e == 4:
        monthn.append('April')
    elif e == 5:
        monthn.append('May')
    elif e == 6:
        monthn.append('June')
    elif e == 7:
        monthn.append('July')
    elif e == 8:
        monthn.append('August')
    elif e == 9:
        monthn.append('September')
    elif e == 10:
        monthn.append('October')
    elif e == 11:
        monthn.append('November')
    else:
        monthn.append('December')

fdf['Monthn'] = monthn

Timedf = fdf.copy()
Timedf['Time'] = Timedf['Time'].str[:2]
Timedf['Time'] = Timedf['Time'].replace('0','00')

top7 = fdf.groupby(['Artist'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = False).head(7)['Artist'].tolist()

top10 = fdf.groupby(['Genre'])['Play Count'].sum().reset_index().sort_values('Play Count', ascending = False).head(10)['Genre'].tolist()

song50 = fdf.groupby(['Artist','Song'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = True).head(50)['Song'].tolist()

# Layout of my dash application

app.layout = html.Div(
    children = [
        html.Div(
            className = 'row',
            children = [
                html.Div(
                    className = 'four columns div-user-controls',
                    children = [
                        # Image of Apple logo
                        html.Img(
                            className = 'logo', src = app.get_asset_url('Apple_Music_Logo.png')
                        ),
                        html.P(
                            dcc.Markdown(
                                '''
                                *BETA*
                                '''
                            ),
                        ),    
                        # Card containing information and the control panel                
                        html.Div(
                            className= 'card',
                            children=[
                                dcc.Tabs(id='manhattan-tabs',value='what-is',children=[
                                    dcc.Tab(
                                        label='About',
                                        value='what-is',
                                        className='tab-style',
                                        selected_className='tab-select',
                                        children=html.Div(className = 'left', children=[
                                            html.Div(
                                                className='center',
                                                children=[
                                                    html.H2('''Clint's Music - Data App'''),
                                                ],
                                            ),
                                            html.Div(
                                                className= 'left',
                                                children = [
                                                    html.P(
                                                        dcc.Markdown(
                                                            '''
                                                            This web app shows the music listening history  
                                                            from my Apple Music subscription.
                                                            ''' 
                                                        ),
                                                    ),
                                                ],
                                            ),
                                            html.Br(),
                                            html.Div(
                                                className='center',
                                                children=[
                                                    html.H2('''How to use this app'''),
                                                ],
                                            ),
                                            html.P(
                                                dcc.Markdown(
                                                    '''
                                                    - Select the *'Control Panel'* tab above.
                                                    - Select which *graph layout* you'd like to view followed by a genre.
                                                    - To view more detail about an artist or song, hover over the data.
                                                    '''
                                                ),
                                            ),
                                            html.Br(),
                                            html.P(
                                                dcc.Markdown(
                                                    '''
                                                    - This web app uses *Python, HTML & CSS.*  
                                                    *Web app source code link coming soon.*
                                                    '''
                                                ),
                                            ),
                                        ]),
                                    ),
                                    dcc.Tab(
                                        label='Control Panel',
                                        value='Control Panel',
                                        className='tab-style',
                                        selected_className='tab-select',
                                        children=[
                                            html.Div(
                                                className='center',
                                                children=[
                                                    html.Br(),
                                                    html.H4('Select a graph layout')
                                                ],
                                            ),
                                            html.Div(
                                                className='center',
                                                children=[
                                                    html.Br(),
                                                    daq.ToggleSwitch(
                                                        id='type-toggle',
                                                        label=['Song', 'Time-Series'],
                                                        value=False,
                                                        color = '#333',
                                                        theme = {
                                                            'dark': True
                                                        },
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                id='slider-container',
                                                className='center',
                                                children=[
                                                    html.Br(),
                                                    dcc.Slider(
                                                        id='sslider',
                                                        className='rc',
                                                        disabled= False,
                                                        min=2017,
                                                        max=2020,
                                                        value=2017,
                                                        marks={
                                                            2017: {'label': '2017'},
                                                            2018: {'label': '2018'},
                                                            2019: {'label': '2019'},
                                                            2020: {'label': '2020'},
                                                        }
                                                    ), 
                                                ],
                                            ),
                                            html.Div(
                                                className='center',
                                                children=[
                                                    html.Br(),
                                                    html.H4('Select a Genre'),
                                                ],
                                            ),
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
                                        ],
                                    ),
                                ]),
                            ],
                        ),
                    ],
                ),
                # Layout for the graphs
                html.Div(
                    className='eight columns div-for-charts',
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
                        html.Div(
                            children=[
                                html.H3(
                                    id='song-ti',
                                    children=[
                                    ],
                                    style = {'display': 'block'}
                                ),
                                html.H3(
                                    id='song-ti-2',
                                    children=[
                                    ],
                                    style = {'display': 'block'}
                                ),
                            ],
                        ),
                        dcc.Graph(
                            id='song-time-graph',
                            style={"height" : "40vh", "width" : "100%"}
                        ),
                    ],
                ),
            ],
        ),
    ],
)
# ----------------------------------------------

# Update artist graph based on genre, graph layout and slider selected 
@app.callback(
    Output('artist-graph', 'figure'),
    [Input('genre-dropdown', 'value'),
    Input('type-toggle', 'value'),
    Input('sslider', 'value')]
)

def update_artist_graph(genre_selected, toggle, year_sel):

    print(genre_selected)
    print(type(genre_selected))
    if toggle == False:

        tdf = fdf[fdf['Genre'] == genre_selected]
        tdf = tdf.groupby(['Artist', 'Genre'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = False)
        top7 = tdf.groupby(['Artist'])['Play Count'].sum().reset_index().sort_values('Play Count', ascending = False).head(7)['Artist'].tolist()
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
            custom_data = ['Artist', 'Genre'],
            text = 'Play Count'
        )

        fig.update_traces(hovertemplate = '<br>'.join([
            'Artist: <b>%{x}</b>',
            'Genre: <b>%{customdata[1]}</b>',
            'Play Count: <b>%{y}</b>'])
        )
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

    if toggle == True:

        if genre_selected:

        # pdf = fdf[fdf['Genre'] == genre_selected]
        # pdf = pdf[pdf['Year'] == year_sel]
        # pdf = pdf.groupby(['Artist', 'Genre', 'Year', 'Month', 'Monthn'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = False)
        # top7 = pdf.groupby(['Artist'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = False).head(7)['Artist'].tolist()
        # ppf = pdf[pdf['Artist'].isin(top7)]
        # ppf = ppf.iloc[0,0]
        # pdf = pdf[pdf['Artist'] == ppf]

            tdf = fdf[fdf['Year'] == year_sel]
            tdf = tdf[tdf['Genre'] == genre_selected]
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
                custom_data = ['Artist', 'Genre'],
                text = 'Play Count'
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

# Update song/graph graph title when graph layout is chosen
@app.callback([
    Output('song-ti-2', 'style'),
    Output('song-ti', 'style')],
    [Input('type-toggle', 'value')]
)

def update_title(toggle):
    if toggle == True:

        return {'display': 'block'}, {'display': 'none'}

    if toggle == False:

        return {'display': 'none'}, {'display': 'block'}

# Update the song/time graph with genre, graph layout, year slider and artist graph outcome
@app.callback(
    Output('song-time-graph', 'figure'),
    [Input('genre-dropdown', 'value'),
    Input('artist-graph', 'hoverData'),
    Input('artist-graph', 'clickData'),
    Input('type-toggle', 'value'),
    Input('sslider', 'value')]
)

def update_song_graph(genre_selected, hoverData, clickData, toggle, year_sel):

    if toggle == False:

        if genre_selected:

            sdf = fdf[fdf['Genre'] == genre_selected]
            sdf = sdf.groupby(['Artist', 'Song', 'Genre'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = False)

        if clickData:

            genre_name = clickData['points'][0]['customdata'][0]
            sdf = fdf[fdf['Artist'] == genre_name]
            sdf = sdf.groupby(['Artist','Song','Genre'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = False)

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
            custom_data = ['Song', 'Genre', 'Artist'],
            text = 'Play Count'
        )
        fig.update_layout(
            yaxis={'categoryorder':'category ascending'},
            margin = dict(b=200),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale = False
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
        fig.update_yaxes(
            {'showgrid': False}
            )

        return fig

    if toggle == True:

        if genre_selected:

            pdf = fdf[fdf['Genre'] == genre_selected]
            pdf = pdf[pdf['Year'] == year_sel]
            pdf = pdf.groupby(['Month','Artist', 'Genre', 'Year', 'Monthn'])['Play Count'].count().reset_index().sort_values('Month', ascending = True)
            top7 = pdf.groupby(['Artist'])['Play Count'].sum().reset_index().sort_values('Play Count', ascending = False).head(7)['Artist'].tolist()
            pdf = pdf[pdf['Artist'].isin(top7)]

        if hoverData:

            genre_name = hoverData['points'][0]['customdata'][0]
            pdf = fdf[fdf['Artist'] == genre_name]
            pdf = pdf[pdf['Genre'] == genre_selected]
            pdf = pdf[pdf['Year'] == year_sel]
            pdf = pdf.groupby(['Artist', 'Genre', 'Year', 'Month', 'Monthn'])['Play Count'].count().reset_index()
        #top15 = sdf.groupby(['Song'])['Play Count'].count().reset_index().sort_values('Play Count', ascending = False).head(15)['Song'].tolist()
        #sdf = sdf[sdf['Song'].isin(top15)]

        if clickData:

            genre_name = clickData['points'][0]['customdata'][0]
            pdf = fdf[fdf['Artist'] == genre_name]
            pdf = pdf[pdf['Genre'] == genre_selected]
            pdf = pdf[pdf['Year'] == year_sel]
            pdf = pdf.groupby(['Artist', 'Genre', 'Year', 'Month', 'Monthn'])['Play Count'].count().reset_index()

        fig = px.line(
            pdf,
            x = 'Month',
            y = 'Play Count',
            color='Artist',
            custom_data= ['Artist', 'Genre', 'Year', 'Month', 'Monthn', 'Play Count'],
            template = 'plotly_dark'
            )

        fig.update_traces(
            hovertemplate = '<br>'.join([
                'Artist: <b>%{customdata[0]}</b>',
                'Genre: <b>%{customdata[1]}</b>',
                'Month: <b>%{customdata[4]}</b>',
                'Year: <b>%{customdata[2]}</b>',
                'Play Count: <b>%{customdata[5]}</b>'
            ]),
            mode='lines+markers'
        )

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale = False,
        )
        fig.update_yaxes(
            {'showgrid': False}
            )

        fig.update_xaxes(
            {'showgrid': False},
            ticktext = [
                'January',
                'February',
                'March',
                'April',
                'May',
                'June',
                'July',
                'August',
                'September',
                'October',
                'November',
                'December'
            ],
            tickvals = [
                '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
                '9',
                '10',
                '11',
                '12'
            ]
        )

        return fig


# Reset artist graph data to prevent conflict with song/title graph        
@app.callback(
    [Output('artist-graph', 'hoverData'),
    Output('artist-graph', 'clickData')],
    [Input('genre-dropdown', 'value'),
    Input('type-toggle', 'value')])

def update_selected_data(toggle, clickData):
    if clickData:

        return None, None

    if toggle:
        
        return None, None

# Dynamic artist title based on data selected
@app.callback(
    Output('artist-title','children'),
    [Input('genre-dropdown', 'value')])

def update_artist_title(artitle):
    if artitle:
        return 'Top ' + str(artitle) + ' Artists'

# Dynamic song title based on data selected
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

# Dynamic time title based on data selected
@app.callback(
    Output('song-ti-2', 'children'),
    [Input('artist-graph', 'hoverData'),
    Input('artist-graph', 'clickData'),
    Input('sslider', 'value'),
    Input('genre-dropdown', 'value')])

def update_song_title(hoverData, clickData, year_sel, Gselect):

    if Gselect:
        sel = 'Top ' + str(Gselect) + ' artists listened to during ' + str(year_sel)


    if hoverData:
        genre_name = hoverData['points'][0]['customdata'][0]
        sel = str(year_sel) + ' recap of ' + str(genre_name)

    if clickData:
        genre_name = clickData['points'][0]['customdata'][0]
        sel = str(year_sel) + ' recap of ' + str(genre_name)

    return sel

# Show/Hide the year slider based on graph layout toggle selected
@app.callback(
    Output('sslider', 'disabled'),
    [Input('type-toggle', 'value')]
)

def update_slider(toggle):

    if toggle == False:
        
        return True

if __name__ == '__main__':
    app.run_server(debug = True, use_reloader = False)