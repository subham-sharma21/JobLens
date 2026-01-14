import os
import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# ---------------- Backend API config ----------------
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_URL = f"{API_BASE_URL}/map/heatmap"

# ---------------- Streamlit config ----------------
st.set_page_config(page_title="JobLens", layout="wide")
st.title("JobLens — India Job Market Map")

# ---------------- Filters ----------------
params = {}

role = st.selectbox(
    "Select Role",
    ["All", "data analyst", "data scientist", "data engineer", "backend engineer"]
)

if role != "All":
    params["role"] = role

exp_range = st.slider(
    "Experience Range (years)",
    min_value=0,
    max_value=20,
    value=(0, 20)
)

params["exp_min"] = exp_range[0]
params["exp_max"] = exp_range[1]

# ---------------- Fetch data ----------------
with st.spinner("Fetching job market data..."):
    try:
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        st.error("Backend API not reachable")
        st.stop()

if not data:
    st.warning("No data found for selected filters")
    st.stop()

df = pd.DataFrame(data)

# ---------------- Map view ----------------
view_state = pdk.ViewState(
    latitude=22.5937,
    longitude=78.9629,
    zoom=4,
    pitch=0,
)

# ---------------- Heatmap Layer ----------------
heatmap_layer = pdk.Layer(
    "HeatmapLayer",
    data=df,
    get_position=["lon", "lat"],
    get_weight="job_count",
    radiusPixels=60,
)

# ---------------- Cluster Layer ----------------
cluster_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position=["lon", "lat"],
    get_radius="job_count * 80",
    get_fill_color=[255, 0, 0, 140],
    pickable=True,
)

deck = pdk.Deck(
    layers=[heatmap_layer, cluster_layer],
    initial_view_state=view_state,
    tooltip={"text": "{city}\nJobs: {job_count}"}
)

st.pydeck_chart(deck)
