from dash import Input, Output, Dash, dcc, html, State
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
from dash_bootstrap_templates import load_figure_template
import geopandas as gpd
import datetime
import dash_daq as daq
from random import randrange

external_stylesheets = [dbc.themes.DARKLY]
load_figure_template('darkly')

mapbox_access_token = 'pk.eyJ1IjoiYWxpc2hvYmVpcmkiLCJhIjoiY2ozYnM3YTUxMDAxeDMzcGNjbmZyMmplZiJ9.ZjmQ0C2MNs1AzEBC_Syadg'
px.set_mapbox_access_token(mapbox_access_token)

merged_fylde_importgpd = gpd.read_file('merged_fylde.geojson')
merged_fylde = pd.read_csv('merged_fylde.csv')
substations = pd.read_csv('substations.csv')
generation = pd.read_csv('renewables.csv')
generation['lat'] = generation['Coords'].str.split(',', expand=True)[0].astype('float')
generation['lon'] = generation['Coords'].str.split(',', expand=True)[1].astype('float')
battery = pd.read_csv('battery.csv')
battery['lat'] = battery['Coords'].str.split(',', expand=True)[0].astype('float')
battery['lon'] = battery['Coords'].str.split(',', expand=True)[1].astype('float')

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='graph1', style={'height':'100vh'}),
        ], md=9, lg=9),
        dbc.Col([
            html.Div(dbc.ButtonGroup([
                dbc.Button('Average', id='btn_general', n_clicks_timestamp='0', className='btn btn-primary btn-lg'),
                dbc.Button('Prediction', id='btn_predict', n_clicks_timestamp='0', className='btn btn-success btn-lg'),
                dbc.Button('Total', id='btn_news', n_clicks_timestamp='0', className='btn btn-light btn-lg'),
            ], vertical=True)
                    , className='d-grid gap-2', style={'height':'15%'}),
            html.Div([
                dbc.Card(dbc.CardBody(html.Ul(id='card1'))), 
                html.Div([
                    dcc.Dropdown(id='drop', value=0, options=[{'label':generation.loc[i]['Type'], 'value':i} for i in generation.index], style={'color':'black', 'width':200}), 
                    html.P(id='card2')], style={'display':'flex', 'padding':5}), 
                html.Div([
                    dcc.Dropdown(id='drop2', value=0, options=[{'label':battery.loc[i]['Type'], 'value':i} for i in battery.index], style={'color':'black', 'width':200}), 
                    html.Div(id='card2a')], style={'display':'flex', 'padding':5}), 
                html.Div(id='card3')
            ], style={'height':'42%'}),
            html.Div(dbc.Accordion([
                dbc.AccordionItem(dcc.Graph(id='card4'), style={'display':'flex'}, title='Demand Today'), 
                dbc.AccordionItem(dcc.Checklist(options=[{'label':i, 'value':i} for i in generation['ID']],
                                                value=list(generation['ID']),
                                                labelStyle={'display': 'inline-block'},
                                                id='checklist'
                                               ), style={'display':'flex'}, title='Generation'),
                dbc.AccordionItem(html.Div([
                    daq.Tank(value=battery.loc[0]['Today'],max=battery.loc[0]['Capacity'],width=50,height=130,label=str(battery.loc[0]['ID']),labelPosition='bottom'),
                    daq.Tank(value=battery.loc[1]['Today'],max=battery.loc[1]['Capacity'],width=50,height=130,label=str(battery.loc[1]['ID']),labelPosition='bottom'),
                    daq.Tank(value=battery.loc[2]['Today'],max=battery.loc[2]['Capacity'],width=50,height=130,label=str(battery.loc[2]['ID']),labelPosition='bottom'),
                    daq.Tank(value=battery.loc[3]['Today'],max=battery.loc[3]['Capacity'],width=50,height=130,label=str(battery.loc[3]['ID']),labelPosition='bottom'),
                ], style={'display':'flex'}), style={'display':'flex'}, title='Storage')
            ]), style={'height':'25vh'}),
            html.Div([
                dcc.Slider(value=int(generation['day'+str(randrange(1,10))].sum()*1000), min=70000, max=100000, id='slider', tooltip={"placement": "bottom", "always_visible": True}),
                #daq.LEDDisplay(id='our-LED-display',size=16, label="Time of Day",value=datetime.datetime.now().hour, backgroundColor='black'),
                dcc.Slider(id='our-LED-display-slider',min=0,max=23,step=1,value=datetime.datetime.now().hour, tooltip={"placement": "bottom", "always_visible": True}),
                html.Div([
                    daq.LEDDisplay(id='live-led', size=32, backgroundColor='black'),
                    daq.LEDDisplay(value=datetime.datetime.now().hour, size=32, backgroundColor='black'),
                ], style={'display':'flex', 'margin':'10px'})
            ]),         
        ], md=3, lg=3),
        
    ]),
    
    dbc.Tooltip("Mean Consumption by Area", target='btn_general'),
    dbc.Tooltip("Electricity shortage", target='btn_predict'),
    dbc.Tooltip("Not yet set", target='btn_news'),
    dbc.Tooltip("Information on each area", target='card1'),
    dbc.Tooltip("Select energy generator", target='drop'),
    dbc.Tooltip("Energy generator info", target='card2'),
    dbc.Tooltip("Select energy storage", target='drop2'),
    dbc.Tooltip("Turn battery charging on/off", target='card2a'),
    dbc.Tooltip("Alerts - generated automatically and can be closed", target='card3'),
    dbc.Tooltip("Typical day of target area", target='card4'),
    dbc.Tooltip("Slide to specify electricity generation amount", target='slider'),
    dbc.Tooltip("Slide to select time of the day", target='our-LED-display-slider'),
    dbc.Tooltip("Actual Live Generation", target='live-led'),
    
    
])

@app.callback(
    Output('graph1', 'figure'),
    [Input('btn_general', 'n_clicks_timestamp'),
    Input('btn_predict', 'n_clicks_timestamp'),
    Input('btn_news', 'n_clicks_timestamp'),
    Input('slider', 'value'),
    Input('our-LED-display-slider', 'value')]
)
def update_map1(n1, n2, n3, mw, time):
    if int(n1) > int(n2) and int(n1) > int(n3):
        fig = px.choropleth_mapbox(merged_fylde_importgpd,
                   geojson = merged_fylde_importgpd['geometry'],
                   locations = merged_fylde_importgpd.index,
                   color = 'Mean consumption\n(kWh per meter)',
                   hover_name = merged_fylde_importgpd['LSOA11CD'],
                   center={"lat": 53.85, "lon": -2.8573},
                   mapbox_style="open-street-map",
                   zoom=10,
                   color_continuous_scale="dense",
                    
                   )
    elif int(n2) > int(n1) and int(n2) > int(n3):
        times = ['8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','0','1','2','3','4','5','6','7']
        butt = pd.Series([pd.Series(merged_fylde['dailyavg'][x].replace('[', '').replace(']', '').split(',')).astype('float')[int(times.index(str(time)))] for x in range(0,len(merged_fylde))])
        if (mw-butt.sum())<0:        
            surplus = abs(mw-butt.sum())
        else:
            surplus = 0
        chosen = range(400,840)[pd.Series([abs(surplus-(butt[butt>y]-y).sum()) for y in range(400,840)]).argmin()]
        fig = px.choropleth_mapbox(merged_fylde_importgpd,
                   geojson = merged_fylde_importgpd['geometry'],
                   locations = merged_fylde_importgpd.index,
                   color = chosen-butt,
                   hover_name = merged_fylde_importgpd['LSOA11CD'],
                   center={"lat": 53.85, "lon": -2.8573},
                   mapbox_style="open-street-map",
                   zoom=10,
                   color_continuous_scale="dense_r",
                         range_color=[-100,0]
                   )
    elif int(n3) > int(n1) and int(n3) > int(n2):
        fig = px.choropleth_mapbox(merged_fylde_importgpd,
                   geojson = merged_fylde_importgpd['geometry'],
                   locations = merged_fylde_importgpd.index,
                   color = 'Total \nconsumption\n(kWh)',
                   hover_name = merged_fylde_importgpd['LSOA11CD'],
                   center={"lat": 53.85, "lon": -2.8573},
                   mapbox_style="open-street-map",
                   zoom=10,
                   color_continuous_scale="dense",
                                   opacity=0.5
                   )
    else:
        fig = px.choropleth_mapbox(merged_fylde_importgpd,
                   geojson = merged_fylde_importgpd['geometry'],
                   locations = merged_fylde_importgpd.index,
                   color = 'Total \nconsumption\n(kWh)',
                   hover_name = merged_fylde_importgpd['LSOA11CD'],
                   center={"lat": 53.85, "lon": -2.8573},
                   mapbox_style="open-street-map",
                   zoom=10,
                   color_continuous_scale="dense",
                                   opacity=0.5
                   )
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    fig.update_traces(colorbar=dict(x=-2, y=0, len=0.2))
    fig.add_trace(px.scatter_mapbox(substations[substations['VOLTAGE_HIGH']==400], lat='lat', lon='lon', color_discrete_sequence=['yellow'], size='VOLTAGE_HIGH', size_max=20).data[0])
    fig.add_trace(px.scatter_mapbox(substations[substations['VOLTAGE_HIGH']==275], lat='lat', lon='lon', color_discrete_sequence=['red'], size='VOLTAGE_HIGH', size_max=15).data[0])
    fig.add_trace(px.scatter_mapbox(substations[substations['VOLTAGE_HIGH']==132], lat='lat', lon='lon', color_discrete_sequence=['orange'], size='VOLTAGE_HIGH', size_max=10).data[0])
    fig.add_trace(px.scatter_mapbox(generation, lat='lat', lon='lon', size='Today', color_discrete_sequence=['pink'], text=generation['Type']+generation['ID'].astype('str')).data[0])
    fig.add_trace(px.scatter_mapbox(battery, lat='lat', lon='lon', color_discrete_sequence=['black'], text=battery['Type']+battery['ID'].astype('str')).data[0])
    return fig

@app.callback(
    [Output('card1', 'children'),
     Output('card2', 'children'),
    Output('card2a', 'children')],
    [Input('graph1', 'clickData'),
     Input('drop', 'value'),
    Input('drop2', 'value')]
)
def update_card(clicked, drop, drop2):
    if clicked is None:
        chosen = 5
    else:
        chosen = clicked['points'][0]['pointNumber']
    #if clicked is not None:
    return [html.Li(merged_fylde_importgpd.loc[chosen]['LSOA11CD']), html.Li(merged_fylde_importgpd.loc[chosen]['LSOA11NM']), html.Li('No of meters: '+str(int(merged_fylde_importgpd.loc[chosen]['Number\nof meters\n']))), html.Li('Total use (annual): '+str(int(merged_fylde_importgpd.loc[chosen]['Total \nconsumption\n(kWh)'])/1000)+' MWh'), html.Li('Mean usage (annual): '+str(int(merged_fylde_importgpd.loc[chosen]['Mean consumption\n(kWh per meter)']))+' kWh'), html.Li('Mean usage (daily): '+'{:.2f}'.format(merged_fylde_importgpd['Mean consumption\n(kWh per meter)'][chosen]/365)+' kWh')], generation.loc[drop]['Today'], [daq.BooleanSwitch(id='switch1',on=False,persistence=True),battery.loc[drop2]['Today']]
    #else:
    #    return 'hi', 'hi2'
    
@app.callback(
    [Output('card3', 'children'),
     Output('card4', 'figure')],
    Input('graph1', 'clickData')
)
def update_card3(clicked):
    if clicked is None:
        chosen = 5
    else:
        chosen = clicked['points'][0]['pointNumber']
    fig = px.line(x=['8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','0','1','2','3','4','5','6','7'], y=pd.Series(merged_fylde['dailyavg'][chosen].replace('[', '').replace(']', '').split(',')).astype('float'), height=250)
    fig.update_traces(line_width=5)
    fig.update_layout(margin=dict(l=0, r=20, t=20, b=0))
    return html.Div([
        dbc.Alert("Hello! I am an alert",id="alert-fade",dismissable=True,is_open=True,className='alert alert-primary'),
        dbc.Alert("Hello! I am an alert",id="alert-fade",dismissable=True,is_open=True,className='alert alert-warning'),
    ]), fig
     
@app.callback(
    Output('our-LED-display', 'value'),
    Input('our-LED-display-slider', 'value')
)
def update_output(value):
    return str(value)    

@app.callback(
    Output('live-led', 'value'),
    Input('checklist', 'value')
)
def update_led(value):
    #return generation['Today'].sum(), 
    return generation['day'+str(randrange(1,10))][[x-1 for x in value]].sum()
    #return generation['Today'][list(generation['ID'].index(list(value.values)))].sum()

    

if __name__=='__main__':
    app.run_server(debug=True, port=8064)