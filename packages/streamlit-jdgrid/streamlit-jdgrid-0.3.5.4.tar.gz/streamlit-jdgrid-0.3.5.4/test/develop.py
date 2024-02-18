import pandas as pd
import streamlit as st

from st_aggrid import AgGrid

st.set_page_config(layout="wide")

df = pd.read_csv(
    "https://raw.githubusercontent.com/fivethirtyeight/data/master/airline-safety/airline-safety.csv"
)

AgGrid(df)
