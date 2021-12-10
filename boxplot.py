import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import plotly.express as px

import pandas as pd


app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Alfian Pasomba'
server = app.server

app.layout = html.Div([
    dbc.Row(dbc.Col(
        [dbc.Row(dbc.Col(html.H2("Boxplot"), id="header", width={"size": 12})),

         dbc.Row(dbc.Col(
                 dcc.Upload(
                     id='upload-data',
                     children=html.Div([
                         html.A("Upload File CSV")
                     ]),
                     multiple=True
                 ), id="upload", width={"size": 10, "offset": 1})
                 ),

            html.Div(id='output-datatable'),

            dbc.Row(id="output-div"),

            dbc.Row(dbc.Col(html.P("alfian pasomba"), id="footer", width={"size": 12}))],
        id="container", width={"size": 10, "offset": 2}, md={"size": 8, "offset": 2})
    )
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'Terjadi error saat mengupload data'
        ], id="error")

    return html.Div([

        dbc.Row(dbc.Col(html.Hr(), width={"size": 10, "offset": 1})),

        dbc.Row(dbc.Col([html.P(filename),
                         dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=10,
            style_table={'overflowX': 'auto', "borderRadius": '5px'}
        ),
            dcc.Store(id='stored-data', data=df.to_dict('records'))], id="tabel", width={"size": 10, "offset": 1})),

        dbc.Row(dbc.Col(html.Hr(), width={"size": 10, "offset": 1})),

        dbc.Row(dbc.Col([html.P("Judul Boxplot"),
                         dcc.Input(id="judul"),
                html.P("Pilih Sumbu X"),
                dcc.Dropdown(id='xaxis-data',
                             options=[{'label': x, 'value': x} for x in df.columns]),
                html.P("Pilih Sumbu Y"),
                dcc.Dropdown(id='yaxis-data',
                             options=[{'label': x, 'value': x} for x in df.columns]),
                html.Button(id="submit-button", children="Buat Boxplot")], id="input", width={"size": 10, "offset": 1})),

        dbc.Row(dbc.Col(html.Hr(), width={"size": 10, "offset": 1}))
    ])


@app.callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output('output-div', 'children'),
              Input('submit-button', 'n_clicks'),
              State('stored-data', 'data'),
              State('xaxis-data', 'value'),
              State('yaxis-data', 'value'),
              State("judul", "value"))
def make_graphs(n, data, x_data, y_data, judul):
    if n is None:
        return dash.no_update
    else:
        bar_fig = px.box(data, x=x_data, y=y_data, title=judul)
        # print(data)
        return dbc.Col(html.Div(dcc.Graph(figure=bar_fig)), id="output",
                       width={"size": 10, "offset": 1})


if __name__ == '__main__':
    app.run_server(debug=True)
