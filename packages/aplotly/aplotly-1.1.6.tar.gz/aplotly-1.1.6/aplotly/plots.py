from typing import List, Union

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from aplotly.utils.return_breakdown import calculate_return_breakdown

from .style import configure_plotly


def plot_line(
    series: pd.Series,
    label: str,
    xlabel: str,
    ylabel: str,
    legend: bool = True,
    filter_series: Union[pd.Series, None] = None,
    holdings: Union[pd.DataFrame, None] = None,
    color_palette: str = "",
    group_title: str = "",
    plot_title: str = "",
) -> go.Figure:
    """Plot a line chart.

    Args:
        series (pd.Series): data for the line chart, the index is the x-axis and the values are the y-axis.
        label (str): name for the line.
        xlabel (str): x-axis label.
        ylabel (str): y-axis label.
        legend (bool, optional): if the legend should be shown. Defaults to True.
        filter_series (Union[pd.Series, None], optional): filter to show on the plot. Defaults to None (no filter).
        holdings (Union[pd.DataFrame, None], optional): holdings to show on the plot. Defaults to None (no holdings).
        color_palette (str, optional): which color palette to use. Defaults to "" (default color palette).
        group_title (str, optional): name of the group on the legend. Defaults to "" (no group name).
        plot_title (str, optional): title of the plot. Defaults to "" (no title).

    Returns:
        go.Figure: plotly figure containing the line chart.
    """
    if holdings is not None:
        custom_labels = []
        for idx, row in holdings.iterrows():
            if idx not in series.index:
                continue

            custom_string = row[row != 0.0].round(3).to_string()
            custom_string = (
                custom_string.replace("    ", ": ")
                .replace("\n", "<br>")
                .replace("  ", " ")
                .replace("Series([], )", "")
            )
            custom_string = "Holdings: <br>" + custom_string
            custom_labels.append(custom_string)
    else:
        custom_labels = None

    configure_plotly(subplots=1, color_palette=color_palette)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=series.values,
            mode="lines",
            name=label,
            legendgroup=1,
            legendgrouptitle_text=group_title,
            line=dict(width=2),
            text=custom_labels,
        )
    )

    fig.update_xaxes(title_text=xlabel)
    fig.update_yaxes(title_text=ylabel)
    fig.update_layout(showlegend=legend, title_text=plot_title)

    if filter_series is not None:
        filter_change = filter_series.diff()

        for x, y in zip(series[filter_change > 0].index, series[filter_change > 0].values):
            fig.add_annotation(
                xref="x",
                yref="y",
                x=x,
                y=y,
                xanchor="center",
                yanchor="bottom",
                text="\u2191",
                showarrow=False,
                font=dict(color="cyan" if color_palette in ["dark_mode", "night"] else "green", size=20),
            )

        for x, y in zip(series[filter_change < 0].index, series[filter_change < 0].values):
            fig.add_annotation(
                xref="x",
                yref="y",
                x=x,
                y=y,
                xanchor="center",
                yanchor="bottom",
                text="\u2193",
                showarrow=False,
                font=dict(color="red", size=20),
            )

    return fig


def plot_multiple_lines(
    series: List[pd.Series],
    ylabel: str,
    xlabel: str,
    labels: list = None,
    visible: list = None,
    styles: list = None,
    legend: bool = True,
    color_palette: str = "",
    group_title: str = "",
    plot_title: str = "",
) -> go.Figure:
    """Plot multiple line charts.

    Args:
        series (List[pd.Series]): list of data for the line charts, the index is the x-axis and the values are the y-axis.
        ylabel (str): y-axis label.
        xlabel (str): x-axis label.
        labels (list, optional): name of each line. Defaults to None (doesn't label of the lines).
        visible (list, optional): if the lines should be visible by default. Defaults to None (all lines are visible).
        legend (bool, optional): if the legend should be shown. Defaults to True.
        color_palette (str, optional): name of the color palette to use. Defaults to "" (default color palette).
        group_title (str, optional): name of the legend group. Defaults to "" (no group name).
        plot_title (str, optional): title for the plot. Defaults to "" (no title).

    Returns:
        go.Figure: plotly figure containing the line charts.
    """
    if labels is None:
        labels = [None] * len(series)

    if visible is None:
        visible = [True] * len(series)

    if styles is None:
        styles = [{"width": 2}] * len(series)

    if any(visible) is False:
        legend = True

    configure_plotly(subplots=1, color_palette=color_palette)
    fig = go.Figure()
    for data, label, visibility, style in zip(series, labels, visible, styles):
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data.values,
                mode="lines",
                name=label,
                legendgroup=1,
                legendgrouptitle_text=group_title,
                visible=visibility,
                line=style,
            )
        )
    fig.update_xaxes(title_text=xlabel)
    fig.update_yaxes(title_text=ylabel)
    fig.update_layout(showlegend=legend, title_text=plot_title)

    return fig


def plot_performance(
    performance: pd.Series,
    drawdown: pd.Series,
    performance_label: str,
    drawdown_label: str,
    performance_ylabel: str = "PnL (%)",
    drawdown_ylabel: str = "Drawdown (%)",
    xlabel: str = "Date",
    legend: bool = True,
    color_palette: str = "",
    performance_group_title: str = "Performance",
    drawdown_group_title: str = "Drawdown",
    row_heights: list = [0.7, 0.3],
    vertical_spacing: float = 0.02,
    plot_title: str = "",
) -> go.Figure:
    """Plot the performance and drawdown of a strategy.

    Returns a double panel plot with the performance on the top and the drawdown on the bottom.

    Args:
        performance (pd.Series): data for the performance, the index is the x-axis and the values are the y-axis.
        drawdown (pd.Series): data for the drawdown, the index is the x-axis and the values are the y-axis.
        performance_label (str): name for the performance line.
        drawdown_label (str): name for the drawdown line.
        performance_ylabel (str, optional): performance y-axis label. Defaults to "PnL (%)".
        drawdown_ylabel (str, optional): drawdown y-axis label. Defaults to "Drawdown (%)".
        xlabel (str, optional): x-axis label. Defaults to "Date".
        legend (bool, optional): if the legend should be shown. Defaults to True.
        color_palette (str, optional): name of the color palette to use. Defaults to "" (default color palette).
        performance_group_title (str, optional): name for the performance legend group. Defaults to "Performance".
        drawdown_group_title (str, optional): name for the drawdown legend group. Defaults to "Drawdown".
        row_heights (list, optional): height of each row. Defaults to [0.7, 0.3].
        vertical_spacing (float, optional): vertical spacing between rows. Defaults to 0.02.
        plot_title (str, optional): title for the plot. Defaults to "" (no title).

    Returns:
        go.Figure: plotly figure containing the performance and drawdown.
    """
    configure_plotly(subplots=2, color_palette=color_palette)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=vertical_spacing, row_heights=row_heights)
    fig.add_trace(
        go.Scatter(
            x=performance.index,
            y=performance,
            mode="lines",
            name=performance_label,
            legendgroup=1,
            legendgrouptitle_text=performance_group_title,
            line=dict(width=2),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=drawdown.index,
            y=drawdown,
            mode="lines",
            name=drawdown_label,
            legendgroup=2,
            legendgrouptitle_text=drawdown_group_title,
            line=dict(width=2),
        ),
        row=2,
        col=1,
    )

    fig.update_yaxes(title_text=performance_ylabel, row=1, col=1)
    fig.update_yaxes(title_text=drawdown_ylabel, row=2, col=1)
    fig.update_xaxes(title_text=xlabel, row=2, col=1)
    fig.update_layout(showlegend=legend, title_text=plot_title)

    return fig


def plot_multiple_performance(
    performance: List[pd.Series],
    drawdown: List[pd.Series],
    labels: list = None,
    performance_ylabel: str = "PnL (%)",
    drawdown_ylabel: str = "Drawdown (%)",
    xlabel: str = "Date",
    legend: bool = True,
    color_palette: str = "",
    performance_group_title: str = "Performance",
    drawdown_group_title: str = "Drawdown",
    row_heights: list = [0.7, 0.3],
    vertical_spacing: float = 0.02,
    plot_title: str = "",
) -> go.Figure:
    """Plot the performance and drawdown of multiple strategies.

    Returns a double panel plot with the performance on the top and the drawdown on the bottom.

    Args:
        performance (List[pd.Series]): list of data for the performance, the index is the x-axis and the values are the y-axis.
        drawdown (List[pd.Series]): list of data for the drawdown, the index is the x-axis and the values are the y-axis.
        labels (list, optional): name for each strategy. Defaults to None (no labels).
        performance_ylabel (str, optional): performance y-axis label. Defaults to "PnL (%)".
        drawdown_ylabel (str, optional): drawdown y-axis label. Defaults to "Drawdown (%)".
        xlabel (str, optional): x-axis label. Defaults to "Date".
        legend (bool, optional): if the legend should be shown. Defaults to True.
        color_palette (str, optional): name of the color palette to use. Defaults to "" (default color palette).
        performance_group_title (str, optional): name for the performance legend group. Defaults to "Performance".
        drawdown_group_title (str, optional): name for the drawdown legend group. Defaults to "Drawdown".
        row_heights (list, optional): height of each row. Defaults to [0.7, 0.3].
        vertical_spacing (float, optional): vertical spacing between rows. Defaults to 0.02.
        plot_title (str, optional): title for the plot. Defaults to "" (no title).

    Returns:
        go.Figure: plotly figure containing the performance and drawdown.

    """
    if len(performance) != len(drawdown):
        raise ValueError("performance and drawdown must have the same length")

    if labels is None:
        labels = [None] * len(performance)

    configure_plotly(subplots=2, color_palette=color_palette)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=vertical_spacing, row_heights=row_heights)
    for _performance, _drawdown, label in zip(performance, drawdown, labels):
        fig.add_trace(
            go.Scatter(
                x=_performance.index,
                y=_performance,
                mode="lines",
                name=label,
                legendgroup=1,
                legendgrouptitle_text=performance_group_title,
                line=dict(width=2),
            ),
            row=1,
            col=1,
        )

        fig.for_each_trace(lambda trace: trace.update(line=dict(color=trace.marker.color)))

        fig.add_trace(
            go.Scatter(
                x=_drawdown.index,
                y=_drawdown,
                mode="lines",
                name=label,
                legendgroup=2,
                legendgrouptitle_text=drawdown_group_title,
                line=dict(width=2),
            ),
            row=2,
            col=1,
        )

    fig.update_yaxes(title_text=performance_ylabel, row=1, col=1)
    fig.update_yaxes(title_text=drawdown_ylabel, row=2, col=1)
    fig.update_xaxes(title_text=xlabel, row=2, col=1)
    fig.update_layout(showlegend=legend, title_text=plot_title)

    return fig


def plot_bars(
    df: pd.DataFrame,
    height_column: str,
    label_column: str = None,
    ylabel: str = "",
    xlabel: str = "",
    legend: bool = True,
    color_palette: str = "",
    group_title: str = "",
    plot_title: str = "",
) -> go.Figure:
    """Plot a bar chart.

    Args:
        df (pd.DataFrame): data for the bar chart, the index is the x-axis and the columns should contain the bar heights and (optionally) the labels.
        height_column (str): name of the column containing the height of the bars.
        label_column (str, optional): name of the column containing the labels for the bars. Defaults to None (no labels).
        ylabel (str, optional): y-axis label. Defaults to "" (no label).
        xlabel (str, optional): x-axis label. Defaults to "" (no label).
        legend (bool, optional): if the legend should be shown. Defaults to True.
        color_palette (str, optional): name of the color palette to use. Defaults to "" (default color palette).
        group_title (str, optional): name of the legend group. Defaults to "" (no group name).
        plot_title (str, optional): title for the plot. Defaults to "" (no title).

    Returns:
        go.Figure: plotly figure containing the bar chart.
    """
    configure_plotly(subplots=1, color_palette=color_palette)

    if label_column is not None:
        labels = df[label_column].unique()
        heights = {label: df[df[label_column] == label][height_column] for label in labels}

        data = [
            go.Bar(name=label, x=df.index, y=heights[label], legendgroup=1, legendgrouptitle_text=group_title)
            for label in labels
        ]

    else:
        data = [go.Bar(x=df.index, y=df[height_column], legendgroup=1, legendgrouptitle_text=group_title)]

    fig = go.Figure(data=data)

    fig.update_yaxes(title_text=ylabel)
    fig.update_xaxes(title_text=xlabel)
    fig.update_layout(showlegend=legend, title_text=plot_title)

    return fig


def plot_returns_tree(
    returns: pd.DataFrame,
    exposure: pd.DataFrame,
    metric: str = "total_return",
    root_color: str = "black",
    color_path: list = ["red", "grey", "green"],
    color_bar: bool = False,
    plot_title: str = "",
):
    """Plot a tree map of the returns.

    Args:
        returns (pd.DataFrame): return data, the index is the date and the columns are the instruments.
        exposure (pd.DataFrame): exposure data, the index is the date and the columns are the instruments.
        metric (str, optional): metric to use for the tree map. Defaults to "total_return",
            choices are "max_return", "avg_return", "std_return" or "total_return".
        root_color (str, optional): color of the root node. Defaults to "black".
        color_path (list, optional): color path for the tree map. Defaults to ["red", "grey", "green"].
            This is used to create a color gradient from the worst performing instrument to the best performing (first color) to the best performing (last color).
        color_bar (bool, optional): if the color bar should be shown. Defaults to False.
        plot_title (str, optional): title for the plot. Defaults to "" (no title).

    Returns:
        go.Figure: plotly figure containing the tree map.

    Raises:
        ValueError: if metric is not one of "max_return", "avg_return", "std_return" or "total_return".

    """
    if metric not in ["max_return", "avg_return", "std_return", "total_return"]:
        raise ValueError("metric must be either 'max_return', 'avg_return', 'std_return' or 'total_return'")

    if metric == "total_return":
        return plot_return_breakdown(returns, exposure, root_color, color_path, color_bar, plot_title)

    metrics = []
    for column in exposure.columns:
        _exposure = exposure[column]
        _exposure = _exposure[_exposure != 0]
        try:
            _metrics = {
                "name": column,
                "max_return": returns.loc[_exposure.index, column].max(),
                "avg_return": returns.loc[_exposure.index, column].mean(),
                "std_return": returns.loc[_exposure.index, column].std(),
            }
            metrics.append(_metrics)
        except:
            continue

    sizes = metrics[metric].abs()
    colors = metrics[metric]
    labels = metrics["name"]

    configure_plotly(1, "")
    fig = go.Figure(
        go.Treemap(
            labels=labels,
            parents=[""] * len(labels),
            values=sizes,
            customdata=colors,
            hovertemplate="<b>%{label}</b><br>%{customdata:.2%}<extra></extra>",
            texttemplate="%{label}<br>%{customdata:.2%}",
            textposition="middle center",
            textfont=dict(size=18),
            marker=dict(
                colors=colors,
                colorscale=color_path,
                cmid=0,
                showscale=color_bar,
                line=dict(width=0),
            ),
            tiling=dict(
                packing="squarify",
                pad=1,
            ),
            root_color=root_color,
        )
    )

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), title_text=plot_title)

    fig.data[0].customdata = colors.values
    fig.data[0].texttemplate = "%{label}<br>%{customdata:.2%}"

    return fig


def plot_return_breakdown(
    returns: pd.DataFrame,
    exposure: pd.DataFrame,
    root_color: str = "black",
    color_path: list = ["red", "grey", "green"],
    color_bar: bool = False,
    plot_title: str = "",
):
    returns = calculate_return_breakdown(exposure, returns)
    relative_returns = returns / returns.sum()

    labels = returns.index
    sizes = returns.abs()
    colors = returns

    configure_plotly(1, "")
    fig = go.Figure(
        go.Treemap(
            labels=labels,
            parents=[""] * len(labels),
            values=sizes,
            customdata=colors,
            hovertemplate="<b>%{label}</b><br>%{customdata:.2%}<extra></extra>",
            texttemplate="%{label}<br>%{customdata:.2%}",
            textposition="middle center",
            textfont=dict(size=18),
            marker=dict(
                colors=colors,
                colorscale=color_path,
                cmid=0,
                showscale=color_bar,
                line=dict(width=0),
            ),
            tiling=dict(
                packing="squarify",
                pad=1,
            ),
            root_color=root_color,
        )
    )

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), title_text=plot_title)

    fig.data[0].customdata = [(r, _r) for r, _r in zip(returns, relative_returns)]
    fig.data[0].texttemplate = "%{label}<br>%{customdata[0]:.2%}<br><i>%{customdata[1]:.2%}</i>"

    return fig


def plot_exposure_tree(
    exposure: pd.Series,
    root_color: str = "black",
    color_path: list = ["red", "grey", "green"],
    color_bar: bool = False,
    plot_title: str = "",
):
    """Plot a tree map of the exposure.

    Args:
        exposure (pd.Series): exposure data, the index is the instruments.
        root_color (str, optional): color of the root node. Defaults to "black".
        color_path (list, optional): color path for the tree map. Defaults to ["red", "grey", "green"].
            This is used to create a color gradient from the worst performing instrument to the best performing (first color) to the best performing (last color).
        color_bar (bool, optional): if the color bar should be shown. Defaults to False.
        plot_title (str, optional): title for the plot. Defaults to "" (no title).
    """
    labels = exposure.index
    sizes = exposure.abs()
    colors = exposure

    configure_plotly(1, "")
    fig = go.Figure(
        go.Treemap(
            labels=labels,
            parents=[""] * len(labels),
            values=sizes,
            customdata=colors,
            hovertemplate="<b>%{label}</b><br>%{customdata:.2%}<extra></extra>",
            texttemplate="%{label}<br>%{customdata:.2%}",
            textposition="middle center",
            textfont=dict(size=18),
            marker=dict(
                colors=colors,
                colorscale=color_path,
                cmid=0,
                showscale=color_bar,
                line=dict(width=0),
            ),
            tiling=dict(
                packing="squarify",
                pad=1,
            ),
            root_color=root_color,
        )
    )

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), title_text=plot_title)

    fig.data[0].customdata = colors.values
    fig.data[0].texttemplate = "%{label}<br>%{customdata:.2%}"

    return fig
