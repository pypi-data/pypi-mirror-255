"""Sidebar for the explore module."""

import os

import streamlit as st


def set_side_bar() -> str:
    """Set the sidebar with the logo and title."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = "resources/horizontal-color.svg"
    absolute_path = os.path.join(current_dir, relative_path)

    st.sidebar.image(absolute_path, width=175)
    st.sidebar.title("Explore")

    option_to_label = {
        SideBarOptions.SAMPLE: "Sample data",
        SideBarOptions.EDA: "Univariate and bivariate EDA",
        SideBarOptions.CORRELATION: "Correlation study",
        SideBarOptions.EXPERIMENTS: "Experiments tracking :building_construction:",
        SideBarOptions.MODEL: "Model deployment :building_construction:",
    }
    view_name = st.sidebar.radio(
        "Select the type of data you want to explore",
        options=option_to_label.keys(),
        format_func=lambda x: option_to_label[x],
        key="radio_select_data",
        label_visibility="collapsed",
    )
    return view_name


class SideBarOptions:
    """Class containing the options for the sidebar."""

    SAMPLE = "sample"
    EDA = "eda"
    CORRELATION = "correlation"
    EXPERIMENTS = "experiments"
    MODEL = "model"
