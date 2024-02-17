import pandas as pd
import streamlit as st

from st_aggrid import AgGrid

st.set_page_config(layout="wide")

df = pd.read_csv(
    "https://raw.githubusercontent.com/lxndrblz/Airports/main/citycodes.csv"
)

AgGrid(df)
