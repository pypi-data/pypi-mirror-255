import pandas as pd
import pytest

from chartgpt.chartgpt import ChartGPT


@pytest.fixture(scope="module")
def sample_cg():
    """Initialize the model."""
    cg = ChartGPT(api_key="fake")
    return cg


def test_plotly_code_run(sample_cg):
    code = """
import plotly.express as px

fig = px.bar(df, x="State", y="Population")
fig"""

    df = pd.DataFrame(
        {
            "State": ["New York", "California", "Texas"],
            "Population": [19.5, 39.5, 29.5],
        }
    )
    assert (
        str(sample_cg.run_code(code, df))
        == "Figure({\n    'data': [{'alignmentgroup': 'True',\n              'hovertemplate': 'State=%{x}<br>Population=%{y}<extra></extra>',\n              'legendgroup': '',\n              'marker': {'color': '#636efa', 'pattern': {'shape': ''}},\n              'name': '',\n              'offsetgroup': '',\n              'orientation': 'v',\n              'showlegend': False,\n              'textposition': 'auto',\n              'type': 'bar',\n              'x': array(['New York', 'California', 'Texas'], dtype=object),\n              'xaxis': 'x',\n              'y': array([19.5, 39.5, 29.5]),\n              'yaxis': 'y'}],\n    'layout': {'barmode': 'relative',\n               'legend': {'tracegroupgap': 0},\n               'margin': {'t': 60},\n               'template': '...',\n               'xaxis': {'anchor': 'y', 'domain': [0.0, 1.0], 'title': {'text': 'State'}},\n               'yaxis': {'anchor': 'x', 'domain': [0.0, 1.0], 'title': {'text': 'Population'}}}\n})"  # noqa: E501
    )
