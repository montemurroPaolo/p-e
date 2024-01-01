import pandas as pd
from django_plotly_dash import DjangoDash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from django.conf import settings


file_path = os.path.join(settings.BASE_DIR, "pe_data_hour.csv")

if os.path.exists(file_path):
    app = DjangoDash(name="ThePlot")
    data = pd.read_csv(file_path)
    # Assuming you have data with columns 'name', 'date', and 'pe30d'

    app.layout = html.Div([
        html.Div([
            html.Label('Select Tokens to Plot:'),
            dcc.Dropdown(
                id='token-dropdown',
                options=[{'label': token, 'value': token} for token in data['name'].unique()],
                multi=True,
                value=data['name'].unique()[:5],  # Default selected tokens
            )
        ]),
        html.Div([
            dcc.Graph(id='line-plot', animate=True, style={'height': 800})
        ])
    ])

    # Define callback to update the plot based on selected tokens
    @app.callback(
        Output('line-plot', 'figure'),
        [Input('token-dropdown', 'value')]
    )
    def update_plot(selected_tokens):
        filtered_df = data[data['name'].isin(selected_tokens)]
        fig = px.line(filtered_df, x='date', y='pe30d', color='name', markers=True, line_shape='linear')
        fig.update_layout(title='Historical pe30d Over Time',
                        xaxis_title='Date',
                        yaxis_title='pe30d',
                        legend_title='Token Name',
                        hovermode='closest',
                        template='plotly_dark')
        return fig