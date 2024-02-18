"""Streamlit container to study correlations between features."""
import pathlib

import pandas as pd
import plotly.express as px
import streamlit as st


def correlation_container(file_path: pathlib.Path, dvc_step_key: str, columns: list[str]):
    """Display the correlation container.

    A container that allows you to select columns and display a correlation matrix.
    """
    st.write("---")
    st.header("Correlation study")

    col1, col2 = st.columns([1, 2])

    with col1:
        submitted, corr_matrix_rows, corr_matrix_cols = user_inputs(dvc_step_key, columns)

    with col2:
        with st.container(border=True):
            st.subheader("Results")
            if submitted:
                correlation_matrix_output_container(file_path, corr_matrix_rows, corr_matrix_cols)
            else:
                st.info("Please click on Execute to display the correlation matrix.")


def correlation_matrix_output_container(
    file_path: pathlib.Path, corr_matrix_rows: list[str], corr_matrix_cols: list[str]
):
    """Display the correlation matrix."""
    df = pd.read_parquet(file_path)
    correlations = df.corr(numeric_only=True)

    correlations = correlations.abs()

    correlations = correlations.loc[corr_matrix_rows, corr_matrix_cols]

    # Plotly heatmap of the correlations
    fig = px.imshow(correlations)
    st.plotly_chart(fig)


def user_inputs(dvc_step_key: str, columns: list[str]) -> tuple[bool, list[str], list[str]]:
    """Display the user inputs form and return the submitted values."""
    with st.container(border=True):
        st.subheader("User inputs")
        form = st.form(key=f"corr_form_{dvc_step_key}", border=False)
        with form:
            corr_matrix_rows = st.multiselect(
                "Select the correlation matrix's rows:",
                options=columns,
                default=columns,
                key=f"y_corr_cols_{dvc_step_key}",
            )
            corr_matrix_cols = st.multiselect(
                "Select the correlation matrix's columns:",
                options=columns,
                default=columns,
                key=f"x_corr_cols_{dvc_step_key}",
            )

    # submit the form
    submitted = form.form_submit_button(label="Execute")
    return submitted, corr_matrix_rows, corr_matrix_cols
