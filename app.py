import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash import Dash
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib
import matplotlib.pyplot as plt

# Recommender for games
df = pd.read_csv("steam-200k.csv")
df.columns = ["user_id", "game", "activity", "hours", "unknown"]

df_users = df[["user_id", "game"]][df["activity"] == "play"].groupby("user_id", axis=0).count().reset_index()
df_users["game"][df_users["game"] < 10].hist()
user_games_dict = df[["user_id", "game"]][df["activity"] == "play"].groupby("user_id", axis=0).count().to_dict()
# Once we got a dict from the entire dataframe, we create a new dict with only "true gamers"
true_gamers_dict = {}
for user in user_games_dict["game"]:
    if user_games_dict["game"][user] > 2:  # if he plays more than two games,
        true_gamers_dict[user] = user_games_dict["game"][user]  # he is a "true gamer"


# a function which will return 1 if user is "true gamer" and 0 if not.
def top_gamer(x):
    if x in true_gamers_dict:
        return 1
    else:
        return 0


# Now, we create a new column on the dataframe, mapping user's id in order to take only "true gamers"
df["gamer"] = df["user_id"].map(lambda x: top_gamer(x))
# Finally, we can work with our own dataframe
af = df.copy()
df_gamers = af[af["gamer"] == 1][af["activity"] == "play"]
# And print the number of different users we have, just to be sure
# print("Top users:", len(df_gamers["user_id"].unique()))
df_recom = df_gamers[["user_id", "game", "hours"]]  # taking only neccessary columns

vectors = {}  # this dict object will contain the vectors

for index in df_recom.index:  # we map the dataset in order to get our own dict
    row = df_recom.loc[index, :]
    user_id = row["user_id"]
    game = row["game"]
    hours = row["hours"]
    if user_id not in vectors:
        vectors[user_id] = {}
    else:
        pass
    vectors[user_id][game] = hours

# NOTE: I chose this user because its me.
# print(vectors[103804924])
user_example = 103804924

######################################################################################################################
# Seperator for app layout and game recommendation engine functions
######################################################################################################################
# Data viz
steam_data = pd.read_csv('steam.csv')
steam_data2 = pd.read_csv('steam2.csv')
steam_data3 = pd.read_csv('steam3.csv')
app = Dash(__name__)
server = app.server
count_dif_game = steam_data.groupby('Name of the games')['Name of the games'].agg('count')

# Average hours users spend on steam
average = steam_data3['Average']

# Tables
original_table = dash_table.DataTable(
    data=df.to_dict('records'),
    columns=[{"id": i, "name": i} for i in df.columns],
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
                        ], style={'flex': '45%', 'margin-top': '30px'}),
                        html.Div([
                            html.H3("Player vs Hour"),
                            player_hours_played_table
                        ], style={'flex': '45%'})
                    ], style={'align-items': 'center', 'display': 'flex'}),
                    html.Div([
                        html.H3("Original Data Table", style={'padding-left': '45%'}),
                        original_table
                    ], style={'align-items': 'center'})
                ])
                ]),
        dcc.Tab(label='Visualizations',
                style={'backgroundColor': '#272727', 'color': '#84c9fb', 'font-family': 'Courier New'},
                children=[html.Div([
                    html.Div([
                        html.Div([
                            html.H3("Free vs Purchased"),
                            dcc.Graph(figure=purch_chart, style={'align-items': 'center'}),
                        ], style={'margin': '15px', 'align-items': 'center'}),
                        html.Div([
                            html.H3("Players vs Hours"),
                            dcc.Graph(figure=player_hours),
                        ], style={'margin': '15px', 'align-items': 'center'}),
                    ]),
                    html.Div([
                        html.Div([
                            html.H3("Game Titles vs Hours"),
                            dcc.Graph(figure=titles_pie),
                        ], style={'margin': '15px', 'align-items': 'center'}),
                        html.Div([
                            html.H3("Game Titles vs Hours"),
                            dcc.Graph(figure=titles_multi),
                        ], style={'margin': '15px', 'align-items': 'center'}),
                    ]),
                ])
                ]),
        dcc.Tab(label='Game Recommendation Engine',
                style={'backgroundColor': '#272727', 'color': '#84c9fb', 'font-family': 'Courier New'},
                children=[html.Div([
                    html.H1("Recommendation Generator"),
                    html.P("Given a user_id, this engine will check all game titles played by users in the 200k sized"
                           " database and recommends a game to the user. Note that the more games the user played, the"
                           " more accurate the results will be."),
                    html.Div([
                        dcc.Textarea(
                            id='textarea-state-example',
                            placeholder="Enter a user ID",
                            style={'width': '100%', 'height': 100, 'color': '#84c9fb', 'font-family': 'Courier New',
                                   'background': '#272727'},
                        ),
                        html.Button('Submit', id='textarea-state-example-button', n_clicks=0),
                        html.Div(id='textarea-state-example-output',
                                 style={'whiteSpace': 'pre-line', 'color': '#84c9fb', 'width': '100%', 'height': 300,
                                        'background': '#272727', 'margin-top': '20px'})
                    ]),
                    html.Div(id='output_div-get')
                ], style={'align-items': 'center', 'height': '100vh'})
                ])
    ])
], style={'backgroundColor': '#121212', 'color': '#84c9fb', 'width': '98vw',
          'font-family': 'Courier New'})


@app.callback(
    Output('textarea-state-example-output', 'children'),
    Input('textarea-state-example-button', 'n_clicks'),
    State('textarea-state-example', 'value')
)
def update_output(n_clicks, value):
    if n_clicks > 0:
        longString = ""
        try:
            value = int(value)
        except:
            return 'Invalid input! \n{}'.format(value)
        finally:
            res = corr_users(value)
            if len(res) < 1:
                return dash.no_update, 'No recommendations for: {}'.format(value)
            for i in res:
                longString += i + " | "
        return 'Results: \n{}'.format(longString)


def corr_users(random_id):
    best = []  # list saving tuples
    for user in vectors:  # for every user in the dict
        possible_recom = []  # possible games to recom
        matched_games = []  # games played in common
        vector_1 = vectors[random_id]  # our user's vector as dict
        vector_2 = vectors[user]  # another user's vector as dict

        given_vector = []  # user's vector of hours played for the matched games
        matched_vector = []  # another user's vector of hours played for the matched games
        if user != random_id:
            # we are matching up the games in common
            for game in vector_2:  # for each game played by an strange user
                if game in vector_1:  # if our user plays it too
                    matched_games.append(game)  # we append it as matched game
                else:  # if not
                    possible_recom.append(game)  # it's a possible recommendation

            for game in matched_games:
                # we construct the vectors with the number of hours that both users played the matched
                given_vector.insert(0, vector_1[game])
                matched_vector.insert(0, vector_2[game])

        if len(matched_games) > 4:
            # if we have enough games matched we can play with this number
            # in order to get better results
            # we calculate similarity
            corr = np.corrcoef(x=given_vector, y=matched_vector, rowvar=True)[0][1]
            dic = {}  # we need a dict for possible recoms
            for game in possible_recom:
                dic[game] = vector_2[game]
            best.append((corr, dic))
        else:
            pass

    print("You were matched up with this number of gamers:", len(best))

    if len(best) == 0:
        print("Warning: No matches")

    else:  # If there are matches:
        res = []
        print("Coincidence levels are: ")  # print every correlation levels we found
        res.append("Coincidence levels are:")
        for i in best:
            print(str(i[0]))
            res.append(str(i[0]))

        best_positive = sorted(best, key=lambda x: x[0], reverse=True)[0]  # The most  correlated tuple
        second_positive = sorted(best, key=lambda x: x[0], reverse=True)[1]  # The second most correlated tuple
        second_recom = max(second_positive[1])
        first_recom = max(best_positive[1])
        recoms = (first_recom, second_recom)
        print("We recommend : ")
        res.append("We recommend: ")
        print("-" + recoms[0] + "  Coincidence: " + str(best_positive[0] * 100)[:5] + "%")
        print("-" + recoms[1] + "  Coincidence: " + str(abs(second_positive[0] * 100))[:5] + "%")
        res.append("-" + recoms[0] + "  Coincidence: " + str(best_positive[0] * 100)[:5] + "%")
        res.append("-" + recoms[1] + "  Coincidence: " + str(abs(second_positive[0] * 100))[:5] + "%")
        return res


if __name__ == '__main__':
    app.run_server(debug=True)
