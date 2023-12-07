from .utils import *
from django.shortcuts import render
import pandas as pd
import plotly.express as px

def home(request):
    csv_file_hour_path = "{}/pe_data_hour.csv".format(settings.BASE_DIR)
    
    merged = pd.read_csv(csv_file_hour_path)

    plot_pe = Plot_pe(merged).to_html()

    context = {
        "plot_pe":plot_pe
    }

    return render(request, 'home.html', context)

def dash_plot(request):
    import pandas as pd
    import dash
    from dash import dcc, html
    from dash.dependencies import Input, Output
    import plotly.express as px

    # Assuming you have inner_df with columns 'name', 'date', and 'pe30d'

    # Create Dash app
    app = dash.Dash(__name__)

    # Define layout
    app.layout = html.Div([
        html.Label('Select Tokens to Plot:'),
        dcc.Dropdown(
            id='token-dropdown',
            options=[{'label': token, 'value': token} for token in inner_df['name'].unique()],
            multi=True,
            value=inner_df['name'].unique()[:5],  # Default selected tokens
        ),
        dcc.Graph(id='line-plot')
    ])

    # Define callback to update the plot based on selected tokens
    @app.callback(
        Output('line-plot', 'figure'),
        [Input('token-dropdown', 'value')]
    )
    def update_plot(selected_tokens):
        filtered_df = inner_df[inner_df['name'].isin(selected_tokens)]
        fig = px.line(filtered_df, x='date', y='pe30d', color='name', markers=True, line_shape='linear')
        fig.update_layout(title='Historical pe30d Over Time',
                        xaxis_title='Date',
                        yaxis_title='pe30d',
                        legend_title='Token Name',
                        hovermode='closest',
                        template='plotly_dark')
        return fig

    # Run the app
    if __name__ == '__main__':
        app.run_server(debug=True)
