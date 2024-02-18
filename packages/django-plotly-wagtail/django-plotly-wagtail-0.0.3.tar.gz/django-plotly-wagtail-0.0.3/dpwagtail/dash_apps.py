"""
Example dash apps for development and testing purposes.
"""


import dash

from dash import dcc, html
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash


app = DjangoDash("SimpleExample")


app.layout = html.Div([dcc.RadioItems(id="rad_choice",
                                      options=[{'label': 'Red', 'value': 0},
                                               {'label': 'Blue', 'value': 1},
                                               ],
                                      value='1'),
                       dcc.RadioItems(id="rad_choice_2",
                                      options=[{'label': 'Red', 'value': 0},
                                               {'label': 'Blue', 'value': 1},
                                               ],
                                      value='0'),
                       html.Div(id='rad_out'),
                       ])


@app.callback(Output('rad_out', 'children'),
              Input('rad_choice', 'value'),
              Input('rad_choice_2', 'value'),
              )
def generate_desc(selection, alt_selection):
    return f"Radio selection is {selection} and {alt_selection}"
