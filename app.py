"""Conversion Forkprint: upload-driven Dash dashboard, three Plotly charts, one original D3 React component."""
from __future__ import annotations
import io
import pathlib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, no_update
from shopper_custom import ConversionForkprint
from data_utils import normalize, parse_upload, filter_data, summary, fork_data, MONTHS, LABELS

BASE = pathlib.Path(__file__).resolve().parent
DATAFILE = BASE/'data'/'online_shoppers_intention.csv'
DEFAULTFILE = DATAFILE
TEAL = '#0d9488'
AMBER = '#d68d54'
NAVY = '#285d8c'
PLOT_BG = '#ffffff'

# D3 script from CDN: internet required for the custom glyph. For air-gapped usage,
# download d3.v7.min.js into /assets/d3.v7.min.js and remove external_scripts.
app = Dash(__name__, title='Conversion Forkprint', suppress_callback_exceptions=False,
           external_scripts=['https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js'])
server = app.server


def load_default():
    if not DEFAULTFILE.exists():
        return None
    return normalize(pd.read_csv(DEFAULTFILE))


def encode(df):
    return df.to_json(orient='split', date_format='iso')


def decode(raw):
    if not raw:
        return None
    return normalize(pd.read_json(io.StringIO(raw), orient='split'))


initial = load_default()
initial_json = encode(initial) if initial is not None else None


def panel(title, description, graph):
    return html.Section([html.Div(title, className='panel-title'), html.P(description, className='panel-description'), graph], className='panel plot-container')


app.layout = html.Div(className='shell', children=[
    dcc.Store(id='session-data', data=initial_json),
    html.Header(className='masthead', children=[
        html.Div([html.Div('Decision intelligence · E-commerce', className='eyebrow'),
                html.H1('Online Shopping Conversion Analytics'),
                html.P('Explore visitor behavior, acquisition channels, and observed purchase outcomes.', className='subtitle')]),
        html.Div('Audience: e-commerce conversion analysts. Historical session-level associations, not causal evidence. Upload any UCI-schema CSV to recompute every visualization.', className='aside')]),
    html.Section(className='controls', children=[
        html.Div(className='panel', children=[html.Label('Dataset upload', className='control-label'),
                                              dcc.Upload(id='upload-csv', children=html.Div(
                                                  'Choose or drop CSV', className='upload'), multiple=False),
                                              html.Div(f'Using bundled UCI CSV ({len(initial):,} sessions).' if initial is not None else 'Upload a CSV to get started.', id='upload-status', className='status')]),
        html.Div(className='panel', children=[html.Label('Visitor type', className='control-label'),
                                              dcc.Dropdown(id='visitor-filter', multi=True, placeholder='All visitors', options=sorted(initial['VisitorType'].unique()) if initial is not None else [])]),
        html.Div(className='panel', children=[html.Label('Month', className='control-label'),
                                              dcc.Dropdown(id='month-filter', multi=True, placeholder='All available months', options=[m for m in MONTHS if initial is not None and m in initial['Month'].unique()])]),
        html.Div(className='panel', children=[html.Label('Day type', className='control-label'),
                                              dcc.RadioItems(id='day-filter', options=[{'label': ' All', 'value': 'all'}, {'label': ' Weekend', 'value': 'weekend'}, {'label': ' Weekday', 'value': 'weekday'}], value='all', inline=True)])]),
    html.Section(className='kpis', children=[
        html.Div(className='panel', children=[html.Div(
            'Selected sessions', className='kpi-label'), html.Div(id='kpi-sessions', className='kpi-value')]),
        html.Div(className='panel', children=[html.Div(
            'Purchasing sessions', className='kpi-label'), html.Div(id='kpi-purchases', className='kpi-value')]),
        html.Div(className='panel', children=[html.Div('Observed conversion', className='kpi-label'), html.Div(id='kpi-conversion', className='kpi-value')])]),
    html.Section(className='plots', children=[
        panel(html.Span('Conversion by visitor type', id='title-bar'), 'Compare conversion rates across visitor groups. Hover for segment-level rates and counts.',
              dcc.Graph(id='visitor-bar', config={'displayModeBar': False})),
        panel(html.Span('Browsing duration versus exit rate', id='title-scatter'), 'Product-page duration versus exit rate, colored by purchase outcome. Hover for session details.', html.Div([dcc.Graph(id='engagement-scatter', config={'displayModeBar': False}),
                                                                                                                                                                                                html.Label(
            'Duration axis:', className='control-label'),
            dcc.RadioItems(id='scatter-axis', options=[{'label': ' 99th percentile (zoom)', 'value': 'zoom'}, {
                           'label': ' Full range', 'value': 'full'}], value='zoom', inline=True, className='control-select'),
            html.P(id='scatter-note', className='info-note')])),
        panel(
            html.Span('Monthly purchase conversion', id='title-line'),
            'Monthly conversion for represented months.',
            html.Div([
                dcc.Graph(
                    id='monthly-line',
                    config={'displayModeBar': False}
                ),

                html.P(
                    'Line breaks indicate months with no sessions in the '
                    'dataset or current selection. A value of 0% means '
                    'sessions occurred, but none resulted in a purchase.',
                    className='info-note'
                )
            ])
        )]),
    html.Section(className='panel custom-panel', children=[
        html.Div(className='custom-top', children=[html.Div([html.Div('Conversion Forkprint: channel–visitor purchase patterns', className='panel-title'),
                                                             html.P('Each channel × visitor fork encodes purchase fraction by branch deflection, and session volume by stem thickness. Select a fork to filter the other three charts.', className='panel-description')]),
                                                   html.Button('Clear fork selection', id='clear-fork', n_clicks=0)]),
        html.Div(className='fork-legend', children=[html.Span([html.I(className='dot', style={'background': TEAL}), 'Purchase arm']), html.Span([html.I(className='dot', style={
                 'background': AMBER}), 'Non-purchase arm']), html.Span('Stem thickness ∝ √(session count) · labels: purchases/sessions · low n: fewer than 30')]),
        html.P(
            'Swipe horizontally to compare Returning, New, '
            'and Other visitors. Scroll vertically to view '
            'all traffic sources.',
            className='mobile-scroll-hint'
        ),

        ConversionForkprint(
            id='forkprint',
            data=[],
            selected=None
        ),
        html.P(id='fork-selection', className='note'),
        html.P('How to read: the green arm deflects upward proportional to purchase share, orange downward proportional to non-purchase share. An arm is absent when its count is zero. Fixed glyph dimensions preserve comparability across filters. Scroll to view all sources.', className='info-note')]),
    html.Footer('Source: UCI Online Shoppers Purchasing Intention (CC BY 4.0). A session is not an identified person. Use selection filters to explore associations, not causes.', className='foot')
])


@app.callback(Output('session-data', 'data'), Output('upload-status', 'children'),
              Input('upload-csv', 'contents'), State('upload-csv', 'filename'), prevent_initial_call=True)
def upload(contents, filename):
    try:
        df = parse_upload(contents)
        return encode(df), f'Loaded validated upload: {len(df):,} sessions, {len(df.columns)} attributes.'
    except Exception as exc:
        return no_update, 'Upload rejected: '+str(exc)


@app.callback(Output('visitor-filter', 'options'), Output('month-filter', 'options'),
              Output('visitor-filter', 'value'), Output('month-filter', 'value'),
              Input('session-data', 'data'))
def options(data):
    df = decode(data)
    if df is None:
        return [], [], [], []
    return sorted(df['VisitorType'].unique()), [m for m in MONTHS if m in set(df['Month'])], [], []


def figure_base():
    fig = go.Figure()
    fig.update_layout(paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG, margin=dict(l=42, r=18, t=20, b=40), font=dict(color='#273b55'),
                      hoverlabel=dict(bgcolor='#142d47', font_color='white'), height=350)
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor='#e6edf5', zeroline=False)
    return fig


def blank(msg):
    fig = figure_base()
    fig.add_annotation(x=.5, y=.5, xref='paper',
                       yref='paper', text=msg, showarrow=False)
    return fig


@app.callback(Output('kpi-sessions', 'children'), Output('kpi-purchases', 'children'), Output('kpi-conversion', 'children'),
              Output('visitor-bar', 'figure'), Output('engagement-scatter',
                                                      'figure'), Output('monthly-line', 'figure'),
              Output('forkprint', 'data'), Output(
                  'fork-selection', 'children'),
              Output('scatter-note', 'children'), Output('title-bar', 'children'), Output(
                  'title-scatter', 'children'), Output('title-line', 'children'),
              Input('session-data', 'data'), Input('visitor-filter',
                                                   'value'), Input('month-filter', 'value'),
              Input('day-filter', 'value'), Input('forkprint', 'selected'), Input('scatter-axis', 'value'))
def update(data, visitors, months, day, selected, axis_mode):
    df = decode(data)
    if df is None:
        return '—', '—', '—', blank('Upload a UCI-schema CSV'), blank('Upload a CSV'), blank('Upload a CSV'), [], 'No dataset loaded.', '', 'Conversion by visitor type', 'Browsing duration versus exit rate', 'Monthly purchase conversion'
    
    base = filter_data(df, visitors, months, day)

    # Reference volume is calculated from the complete uploaded dataset,
    # not from the currently filtered subset.
    global_max_sessions = int(
        df.groupby(['TrafficType', 'VisitorType']).size().max()
    )

    glyphs = fork_data(base, scale_max=global_max_sessions)
    chart_df = base
    select_label = 'Click a fork to focus the other charts.'
    if isinstance(selected, dict) and 'traffic' in selected and 'visitor' in selected:
        chart_df = chart_df[(chart_df['TrafficType'] == str(selected['traffic'])) & (
            chart_df['VisitorType'] == selected['visitor'])]
        select_label = f"Fork selected: traffic {selected['traffic']}, {selected['visitor']}. Click it again or Clear fork selection to reset."
    # KPIs reflect the same selected population as the three standard plots.
    s = summary(chart_df)
    if chart_df.empty:
        return '0', '0', '0.0%', blank('No selected sessions'), blank('No selected sessions'), blank('No selected sessions'), glyphs, select_label, 'No sessions match this combination.', 'No matching visitor sessions', 'No matching browsing sessions', 'No matching monthly sessions'
    by = chart_df.groupby('VisitorType')['Revenue'].agg(
        ['mean', 'size']).sort_values('mean')
    
    bar = figure_base()

    display_labels = [
        LABELS.get(visitor, visitor)
        for visitor in by.index
    ]

    bar.add_trace(
        go.Bar(
            x=by['mean'] * 100,
            y=display_labels,
            orientation='h',
            marker_color=TEAL,
            customdata=np.stack([by['size'].values], axis=1),
            hovertemplate=(
                '%{y}<br>'
                'Conversion: %{x:.1f}%<br>'
                'Sessions: %{customdata[0]:,}'
                '<extra></extra>'
            )
        )
    )

    bar.update_layout(
        yaxis_title=None,
        xaxis_title='Purchasing sessions (%)',
        showlegend=False
    )

    bar.update_xaxes(
        range=[0, max(5, float(by['mean'].max() * 100) * 1.25)],
        ticksuffix='%'
    )
    # Show every point (Scattergl supports this size); changing the x-axis alters only
    # viewport, not the data, and makes any points outside the zoom explicit.
    scatter_df = chart_df
    scatter = figure_base()
    for purchased, color, label in [(0, NAVY, 'No purchase'), (1, AMBER, 'Purchased')]:
        g = scatter_df[scatter_df['Revenue'] == purchased]
        scatter.add_trace(go.Scattergl(x=g['ProductRelated_Duration'], y=g['ExitRates'], mode='markers', name=label,
                                       marker=dict(color=color, size=6, opacity=.35), customdata=np.stack([g['ProductRelated'].values, g['PageValues'].values], axis=1),
                                       hovertemplate='Product duration: %{x:,.1f}s<br>Exit rate: %{y:.1%}<br>Product pages: %{customdata[0]}<extra>'+label+'</extra>'))
    duration = scatter_df['ProductRelated_Duration']
    cutoff = max(100., float(duration.quantile(.99)))
    beyond = int((duration > cutoff).sum())
    if axis_mode == 'full':
        max_x = max(100., float(duration.max())*1.05)
        note = f'Full duration range; all {len(scatter_df):,} sessions are plotted. The right-hand tail can compress dense points.'
    else:
        max_x = cutoff*1.1
        hidden = int((duration > max_x).sum())
        note = f'All {len(scatter_df):,} sessions are loaded; {hidden:,} beyond the visible duration window. Choose Full range to see outliers.'
    scatter.update_xaxes(
        title='Product-related page duration (s)', range=[0, max_x])
    scatter.update_yaxes(title='Exit rate', tickformat='.0%')
    scatter.update_layout(legend=dict(
        orientation='h', y=1.13, x=0), margin=dict(l=50, r=15, t=35, b=45))
    # Monthly purchase conversion
    monthly = (
        chart_df.groupby('Month')['Revenue']
        .agg(['mean', 'size', 'sum'])
        .reindex(MONTHS)
    )

    # Missing months remain None so Plotly leaves gaps.
    y = [
        None if pd.isna(v) else float(v) * 100
        for v in monthly['mean']
    ]

    monthly_tooltips = []

    for month in MONTHS:
        row = monthly.loc[month]

        if pd.isna(row['size']):
            monthly_tooltips.append('')
            continue

        sessions = int(row['size'])
        purchases = int(row['sum'])
        conversion = float(row['mean']) * 100

        tooltip = (
            f'{month}<br>'
            f'Conversion: {conversion:.1f}%<br>'
            f'Purchases: {purchases:,}<br>'
            f'Sessions: {sessions:,}'
        )

        if sessions < 30:
            tooltip += '<br>Small sample: interpret carefully'

        monthly_tooltips.append(tooltip)

    line = figure_base()

    line.add_trace(
        go.Scatter(
            x=MONTHS,
            y=y,
            mode='lines+markers',
            connectgaps=False,
            line=dict(color=TEAL, width=3),
            marker=dict(size=9, color=TEAL),
            text=monthly_tooltips,
            hovertemplate='%{text}<extra></extra>'
        )
    )
    line.update_yaxes(title='Conversion rate (%)', ticksuffix='%')
    line.update_xaxes(title='Recorded month', type='category',
                      categoryorder='array', categoryarray=MONTHS)
    labels = {'Returning_Visitor': 'returning visitors',
              'New_Visitor': 'new visitors', 'Other': 'other visitors'}
    if len(by) > 1:
        leader = by['mean'].idxmax()
        bar_title = f'{labels.get(leader, leader).capitalize()} have the highest observed conversion in this selection'
    else:
        bar_title = 'Observed conversion for the selected visitor group'

    # Use a takeaway title only when the current filtered data supports it.
    if len(scatter_df) >= 100 and duration.nunique() >= 5:
        duration_groups = pd.qcut(
            duration,
            q=5,
            labels=False,
            duplicates='drop'
        )

        comparison = (
            scatter_df.assign(duration_group=duration_groups)
            .groupby('duration_group')
            .agg(
                conversion=('Revenue', 'mean'),
                exit_rate=('ExitRates', 'mean'),
                sessions=('Revenue', 'size')
            )
            .sort_index()
        )

        shortest = comparison.iloc[0]
        longest = comparison.iloc[-1]

        if (
            len(comparison) >= 2
            and longest['conversion'] > shortest['conversion']
            and longest['exit_rate'] < shortest['exit_rate']
        ):
            scatter_title = (
                'Longer product browsing is associated with '
                'fewer exits and more purchases'
            )
        else:
            scatter_title = (
                'Browsing duration shows varying exit and purchase patterns'
            )
    else:
        scatter_title = 'Browsing outcomes in the selected sessions'
    valid_months = monthly.dropna(subset=['mean'])

    if len(valid_months) > 1:
        peak = valid_months['mean'].idxmax()
        peak_sessions = int(valid_months.loc[peak, 'size'])

        if peak_sessions < 30:
            line_title = (
                f'{peak} has the highest observed conversion '
                '(small sample)'
            )
        else:
            line_title = (
                f'{peak} has the highest observed conversion '
                'in this selection'
            )

    else:
        line_title = 'Observed purchase conversion in selected months'
    return f"{s['sessions']:,}", f"{s['purchases']:,}", f"{100*s['conversion']:.1f}%", bar, scatter, line, glyphs, select_label, note, bar_title, scatter_title, line_title


@app.callback(
    Output('forkprint', 'selected'),
    Input('clear-fork', 'n_clicks'),
    Input('session-data', 'data'),
    Input('visitor-filter', 'value'),
    Input('month-filter', 'value'),
    Input('day-filter', 'value'),
    prevent_initial_call=True
)
def reset_fork(n_clicks, data, visitors, months, day):
    return None


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)
