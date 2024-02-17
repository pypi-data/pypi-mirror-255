# ChartGPT

Welcome to the ChartGPT documentation! This documentation provides an overview of the ChartGPT library and guides you on how to use it to generate visualizations for your Pandas dataframes.

## Introduction

ChartGPT is a lightweight and user-friendly tool designed to assist you in visualizing your Pandas dataframes. Whether you are working in a Jupyter notebook or developing a Dash app, ChartGPT makes it effortless to generate stunning charts and plots. 📈

## Installation

You can install ChartGPT using pip:

```bash
pip install chartgpt
```

## Usage

ChartGPT provides an intuitive interface for generating charts from your dataframes.

### Jupyter Notebook

To use ChartGPT in a Jupyter notebook, you can follow these steps:

Import the `chartgpt` module:

```python
import chartgpt as cg
```

Read your data into a Pandas dataframe. For example:

```python
import pandas as pd
df = pd.read_csv('data.csv')
```

Create a `Chart` object by passing the dataframe and your API key (if applicable):

```python
chart = cg.Chart(df)
```

By default, ChartGPT will look for an API key in the `OPENAI_API_KEY` environment variable. If you have set this variable, you can omit the `api_key` parameter. Otherwise you will need to provide your API key using the `api_key` parameter like so:

```python
chart = cg.Chart(df, api_key="YOUR_API_KEY")
```

Generate a chart by calling the `plot` method with a prompt:

```python
chart.plot("Ask any question you want!")
```

This will generate a chart based on the provided prompt.

### Dash App

ChartGPT can also be integrated into Dash apps for interactive visualizations.

## Documentation

For detailed information on how to use ChartGPT, please refer to the [documentation](https://chatgpt.github.io/chart/). The documentation provides comprehensive guides, API reference, and examples to help you get started with ChartGPT.

## License

This project is licensed under the MIT License. For more information, please see the [LICENSE](LICENSE) file.
