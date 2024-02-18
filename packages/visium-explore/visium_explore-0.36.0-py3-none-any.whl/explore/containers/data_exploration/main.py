"""The explorer container allows the user to interact with the chosen data by selecting columns to explore and plot."""
import pathlib

import pandas as pd
import streamlit as st

from explore.containers.data_exploration.constants import PlotTypes
from explore.containers.data_exploration.plot import Box, Histogram, Line, Plot, Scatter


def explorer_container(file_path: pathlib.Path, tab_key: str, columns: list[str]) -> None:
    """Display the explorer container.

    It allows the user to interact with the chosen data by selecting columns to explore and plot.
    """
    st.write("---")
    st.header("Data exploration")

    file_path = pathlib.Path(file_path)
    dvc_step = file_path.parts[-1]

    col1, col2 = st.columns([1, 2])
    with col1:
        with st.container(border=True):
            st.subheader("User inputs")
            plot, selected_col = column_of_interest_and_plot_selection_container(
                tab_key=tab_key, dvc_step=dvc_step, columns=columns
            )

    with col2:
        with st.container(border=True):
            st.subheader("Results")
            display_plot_container(file_path=file_path, plot=plot, selected_col=selected_col)

        # exploration_container(file_path, user_inputs=user_inputs)


def column_of_interest_and_plot_selection_container(tab_key: str, dvc_step: str, columns: list):
    key = f"{tab_key}_{dvc_step}"
    selected_col = st.selectbox(
        "Select a column to inspect (x-axis)",
        options=sorted(columns),
        key=f"col_inspect_{key}",
    )
    plot_type = st.selectbox(
        "Select the type of plot you want to use",
        options=[None, PlotTypes.HISTOGRAM, PlotTypes.BOX, PlotTypes.SCATTER, PlotTypes.LINE],
        key=f"plot_type_{key}",
    )

    if plot_type == PlotTypes.HISTOGRAM:
        plot = Histogram(columns=columns, key=key)
    elif plot_type == PlotTypes.BOX:
        plot = Box(columns=columns, key=key)
    elif plot_type == PlotTypes.SCATTER:
        plot = Scatter(columns=columns, key=key)
    elif plot_type == PlotTypes.LINE:
        plot = Line(columns=columns, key=key)
    else:
        plot = None
        st.warning("Please select a plot type above to choose plot options.")

    return plot, selected_col


def display_plot_container(file_path: pathlib.Path, plot: Plot, selected_col: str) -> None:
    """Read the data and display the plot with the settings specified by the Plot object."""
    df = pd.read_parquet(file_path)

    st.write("##### Univariate description")
    # univariate_description_series = df[selected_col].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])

    # univariate_description_df = pd.DataFrame(univariate_description_series).transpose()
    # univariate_description_df = univariate_description_df.drop(columns=["count"])
    # describe_columns = list(univariate_description_df.columns)
    # univariate_description_df["perc_null"] = df[selected_col].isnull().mean()
    # univariate_description_df["size"] = len(df)
    # univariate_description_df = univariate_description_df[["size", "perc_null"] + describe_columns]
    univariate_description_df = construct_univariate_description_df(df, selected_col)
    st.write(univariate_description_df)
    if plot is not None and plot.y_axis and pd.api.types.is_object_dtype(df[selected_col]):
        groupby_description = df.groupby(selected_col)[plot.y_axis].describe()
        groupby_description = pd.DataFrame(groupby_description).transpose()
        groupby_description = groupby_description.sort_values(by="count", ascending=False)
        st.write(groupby_description)

    st.write("##### Plot")
    if plot is not None:
        plot.show(df=df, selected_col=selected_col)
    else:
        st.warning("Please select a plot type on the left.")


def construct_univariate_description_df(df: pd.DataFrame, selected_col: str) -> pd.DataFrame:
    """Compute the univariate description of the selected column."""
    univariate_description_series = df[selected_col].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])

    univariate_description_df = pd.DataFrame(univariate_description_series).transpose()
    univariate_description_df = univariate_description_df.drop(columns=["count"])
    describe_columns = list(univariate_description_df.columns)
    univariate_description_df["ratio_null"] = df[selected_col].isnull().mean()
    univariate_description_df["size"] = len(df)
    univariate_description_df = univariate_description_df[["size", "ratio_null"] + describe_columns]
    return univariate_description_df
