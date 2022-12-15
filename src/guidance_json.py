import json
import pandas as pd
import streamlit as st
from pathlib import Path

with open(Path("guidance/gunderson-2018-revised/main-codebook.json"), "r") as f:
    df_json = pd.json_normalize(json.load(f), record_path=["variables"])
    st.write(df_json)