import dash
import plotly.express as px
import numpy as np

from dash import dcc
from dash import html
from config import sky

app = dash.Dash(__name__)

candidates = sky.get('admissions/candidates')
candidates.current_status = candidates.current_status.fillna('Needs Checklist')

checklist = sky.get('admissions/checkliststatus')

finished_application = checklist.loc[np.where(checklist.ordinal >= 3), 'status_name'].tolist()
incomplete_application = checklist.loc[np.where(checklist.ordinal < 3), 'status_name'].tolist()

candidates.loc[candidates.current_status.isin(finished_application), 'application_status'] = 'Finished Application'
candidates.loc[~candidates.current_status.isin(finished_application), 'application_status'] = 'Incomplete Application'

candidates['grade_level'] = candidates.entering_grade.str.extract(r'(\d*)')

financial_aid = sky.getAdvancedList(73845)['user_id'].astype('int64').tolist()

candidates.loc[candidates.user_id.isin(financial_aid), 'financial_aid'] = True
candidates.loc[~candidates.user_id.isin(financial_aid), 'financial_aid'] = False

candidates.loc[candidates.financial_aid]

fig = px.bar(
    candidates.merge(
        candidates.groupby('grade_level').count()['user_id'].rename('count').reset_index()
    ),
    x = 'grade_level',
    color = 'application_status'
)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)