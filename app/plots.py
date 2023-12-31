import plotly.graph_objects as go
import statistics
import plotly
import numpy as np

# Convert Plotly figure to JSON
def JSON_plot(fig):

    # official method - https://www.geeksforgeeks.org/create-a-bar-chart-from-a-dataframe-with-plotly-and-flask/
    # data = [fig]
    # graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    # offline method - https://stackoverflow.com/questions/60803088/plotly-graph-empty-in-flask
    graphJSON = plotly.offline.plot(fig, 
                    config={"displayModeBar": False}, 
                    show_link=False, include_plotlyjs=False, 
                    output_type='div')

    return graphJSON

# Y-max of Plotly
# https://stackoverflow.com/questions/66583626/plotlyget-the-values-from-a-histogram-plotlyget-the-values-from-a-trace
def fig_y_max(fig):
    f = fig.full_figure_for_development(warn=False)

    xbins = f.data[0].xbins
    plotbins = list(np.arange(start=xbins['start'], stop=xbins['end']+xbins['size'], step=xbins['size']))
    counts, bins = np.histogram(list(f.data[0].x), bins=plotbins)
    
    return max(counts)

def tts_figure(df):

    # Dataset: most recent year
    df_all = df
    period = df["Period"].unique()[::-1].tolist()[0] # most recent year
    df = df_all.loc[df_all['Period'] == period]

    # Generate Metrics
    metrics = {'internal_hirings':df.shape[0],
               'department':df['Department/agency'].iloc[0],
                'period': df.Period.iloc[0],
                'tts_minimum': min(df['Time to staff']),
                'tts_maximum': max(df['Time to staff']),
                'tts_average': int(statistics.mean(df['Time to staff'])),
                'tts_median': int(statistics.median(df['Time to staff']))
           }

    ## Histogram

    # resource: https://plotly.com/python/table-subplots/
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=2, cols=1,
                        vertical_spacing=0.15,
                        specs=[[{"type": "histogram"}],
                                [{"type": "table"}]])

    fig.add_trace(go.Histogram(x=df['Time to staff'], nbinsx=50, marker_color='#336b95',showlegend=False),
                            row=1, col=1
                            )
    # Custom Y-axis
    y_max = fig_y_max(fig)+1
    fig.update_layout(yaxis_range=[0,y_max])

    # y/x axis ticks and black lines
    fig.update_yaxes(showgrid=False,ticks="outside",tickson="boundaries",ticklen=5,showline=True, linecolor='black')
    fig.update_xaxes(showgrid=False,ticks="outside",tickson="boundaries",ticklen=5,showline=True, linecolor='black')


    # Median Line
    x_median = int(statistics.median(df['Time to staff']))
    fig.add_shape(
            go.layout.Shape(type='line', xref='x', yref='y',
            x0=x_median, y0=0, x1=x_median, y1=10, line={'dash': 'dash'}),)

    fig.update_layout(xaxis_title="Number of Days", yaxis_title="Number of cases") # titles
    fig.update_layout(bargap=0.01) # spacing

    fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)') # white background

    # Median Text
    x_middle = max(df['Time to staff'])/2
    text_median = f"--- Median ({x_median} days)"

    fig.add_trace(go.Scatter(
        x=[x_middle],
        y=[y_max],
        mode="lines+text",
        name="Lines and Text",
        text=[text_median],
        textposition="bottom center",
        showlegend=False
    ))

    ## Table
    # setup
    df_table = df[['Reference number', 'Time to staff', 'Type', 'Department/agency']]
    df_all_table = df_all[['Reference number', 'Time to staff', 'Type', 'Department/agency']]

    # formatting
    headerColor = 'grey'
    rowEvenColor = 'lightgrey'
    rowOddColor = 'white'

    fig.add_trace(go.Table(
        header={"values": df_table.columns},
        cells={"values": df_table.T.values},
        domain=dict(x=[0, 1],
                    y=[0, 1])),
        row=2, col=1)

    ## Dropdown
    # Selectable Dropdown
    # https://stackoverflow.com/questions/71622776/plotly-update-button-to-filter-dataset
    fig.update_layout(
        updatemenus=[
            # Internal/External Menu
            {
            # specify position of menu
            "x":-0.2,"y":0.98,
            # specify values to update
                "buttons": [
                    {
                        "label": c,
                        "method": "update",
                        "args": [{
                            # histogram
                            "y": [df_all.loc[df_all['Type'] == c, 'Time to staff']], 
                            # table       
                            "cells": {"values": df_all_table.loc[df_all['Type'] == c].T.values}}],
                    }
                    for c in ['Internal','External'] # reversed order list
                ]  
            },
            
            # Year Menu
            {"x":-0.2,"y":0.87,
                "buttons": [
                    {
                        "label": c,
                        "method": "update",
                        "args": [{
                            "y": [df_all.loc[df_all['Period'] == c, 'Time to staff']],       
                            "cells": {"values": df_all_table.loc[df_all['Period'] == c].T.values}}],
                    }
                    for c in df_all["Period"].unique()[::-1].tolist()
                ]  
            }
            
            ])

    # dropdown text
    fig.add_annotation(x=-0.37, y=y_max, xref='paper', showarrow=False,
                text="<b>Type of hiring:<b>")

    fig.add_annotation(x=-0.37, y=y_max-1.5, xref='paper', showarrow=False,
                text="<b>Time period:<b>")

    fig.update_layout(
        margin=dict(l=50,t=50),
        height=800)

    return fig, metrics
