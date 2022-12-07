from dash import dash_table
from dash import dcc
from dash import html
from dash import Dash
import numpy as np
import pandas as pd
import plotly.express as px

steam_data = pd.read_csv('steam.csv')
steam_data2 = pd.read_csv('steam2.csv')
steam_data3 = pd.read_csv('steam3.csv')
app = Dash(__name__)

count_dif_game = steam_data.groupby('Name of the games')['Name of the games'].agg('count')

# Average hours users spend on steam
average = steam_data3['Average']

# Tables
raw_table = dash_table.DataTable(
    data=steam_data.to_dict('records'),
    columns=[{"id": i, "name": i} for i in steam_data.columns],
    style_cell={'textAlign': 'center', 'backgroundColor': '#141414', 'font-family': 'Courier New', 'border': '#141414',
                'width': '25%'},
    fixed_rows={'headers': True},
    style_header={
        'backgroundColor': '#000010',
        'fontWeight': 'bold',
        'font-family': 'Courier New'
    },
    style_as_list_view=True,
    style_table={'height': '400px'}
)
game_hour_table = dash_table.DataTable(
    data=steam_data2.to_dict('records'),
    columns=[{"id": i, "name": i} for i in steam_data2.columns],
    style_cell={'textAlign': 'center', 'backgroundColor': '#141414', 'font-family': 'Courier New', 'border': '#141414',
                'width': '25%'},
    fixed_rows={'headers': True},
    style_header={
        'backgroundColor': '#000010',
        'fontWeight': 'bold',
        'font-family': 'Courier New'
    },
    style_as_list_view=True,
    style_table={'height': '400px'}
)
player_hours_played_table = dash_table.DataTable(
    data=steam_data3.to_dict('records'),
    columns=[{"id": i, "name": i} for i in steam_data3.columns],
    style_cell={'textAlign': 'center', 'backgroundColor': '#141414', 'font-family': 'Courier New', 'border': '#141414',
                'width': '25%'},
    fixed_rows={'headers': True},
    style_header={
        'backgroundColor': '#000010',
        'fontWeight': 'bold',
        'font-family': 'Courier New'
    },
    style_as_list_view=True,
    style_table={'height': '400px'}
)
# free vs purchased games
total_purchases = steam_data.groupby('Purchases')['Purchases'].agg('count')
purch_chart = px.bar(steam_data, x="Purchases", y=steam_data.Purchases.index, color='Purchases', barmode="group",
                     color_discrete_sequence=['#4bb2f9'], labels={'index': 'Total Count'}, template='plotly_dark',
                     height=350)
purch_chart.update_layout(paper_bgcolor="#121212", font_color='#84c9fb', font_family="Courier New")

# hours played vs game titles
simplified_steam_data2 = steam_data2.nlargest(100, ['Total Hours'])

titles_pie = px.pie(steam_data2.nlargest(10, ['Total Hours']), values='Total Hours', names="Unique Titles",
                    template='plotly_dark', color_discrete_sequence=px.colors.sequential.GnBu_r, height=350)
titles_pie.update_layout(legend={'xanchor': 'left', 'yanchor': 'top'}, font_color='#84c9fb', font_family="Courier New")

titles_multi = px.line(x=simplified_steam_data2['Unique Titles'], y=simplified_steam_data2['Total Hours'],
                       color=px.Constant("Average Hours"), labels=dict(x="Unique Games", y="Total Hours", color="Time"),
                       template='plotly_dark', height=350)
titles_multi.add_bar(x=simplified_steam_data2['Unique Titles'], y=simplified_steam_data2['Total Hours'],
                     name="Aggregate")
titles_multi.update_layout(font_color='#84c9fb', font_family="Courier New")

# Hours vs player and average
player_hours = px.bar(steam_data3, x=steam_data3['Total Hours'], y=steam_data3['Unique Users'], orientation='h',
                      template='plotly_dark', height=350)
player_hours.update_layout(font_color='#84c9fb', font_family="Courier New")

# the layout
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Datasets',
                style={'backgroundColor': '#272727', 'color': '#84c9fb', 'font-family': 'Courier New'},
                children=[html.Div([
                    html.Div([
                        html.H3("Raw Data Table", style={'padding-left': '45%'}),
                        raw_table
                    ], style={'align-items': 'center', 'height': '45%'}),
                    html.Div([
                        html.Div([
                            html.H3("Game vs Time Table"),
                            game_hour_table
                        ], style={'flex': '45%'}),
                        html.Div([
                            html.H3("Player vs Hour"),
                            player_hours_played_table
                        ], style={'flex': '45%'})
                    ], style={'align-items': 'center', 'display': 'flex'}),
                ])
                ]),
        dcc.Tab(label='Visualizations',
                style={'backgroundColor': '#272727', 'color': '#84c9fb', 'font-family': 'Courier New'},
                children=[html.Div([
                    html.Div([
                        html.Div([
                            html.H3("Free vs Purchased"),
                            dcc.Graph(figure=purch_chart, style={'align-items': 'center'}),
                        ], style={'margin': '15px', 'align-items': 'center', 'flex': '45%'}),
                        html.Div([
                            html.H3("Players vs Hours"),
                            dcc.Graph(figure=player_hours),
                        ], style={'margin': '15px', 'align-items': 'center', 'flex': '45%'}),
                    ], style={'display': 'flex'}),
                    html.Div([
                        html.Div([
                            html.H3("Game Titles vs Hours"),
                            dcc.Graph(figure=titles_pie),
                        ], style={'margin': '15px', 'align-items': 'center', 'flex': '45%'}),
                        html.Div([
                            html.H3("Game Titles vs Hours"),
                            dcc.Graph(figure=titles_multi),
                        ], style={'margin': '15px', 'align-items': 'center', 'flex': '45%'}),
                    ], style={'display': 'flex'}),
                ])
                ]),
        dcc.Tab(label='Game Recommendation Engine',
                style={'backgroundColor': '#272727', 'color': '#84c9fb', 'font-family': 'Courier New'},
                children=[html.Div([
                    html.H1("Recommendation Generator"),
                    html.P("Given a user_id, this engine will check all game titles played by users in the 200k sized"
                           "database and recommends a game to the user. Note that the more games the user played, the"
                           "more accurate the results will be."),
                    html.Div([
                        dcc.Input(id="get-report", type="text", placeholder="Enter a user ID"),
                        html.Button(id='submit-button-get', children='Submit', type='submit'),
                    ]),
                    html.Div(id='output_div-get')
                ], style={'align-items': 'center'})
                ])
    ])
], style={'backgroundColor': '#121212', 'color': '#84c9fb', 'height': '100vh', 'width': '98vw',
          'font-family': 'Courier New'})


if __name__ == '__main__':
    app.run_server()
