import os
import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# ---------------- Backend API Configuration ----------------
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

# ---------------- Streamlit Page Configuration ----------------
st.set_page_config(
    page_title="JobLens — Job Market Intelligence Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #2b5c8f;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# Helper function to check API connectivity
@st.cache_data(ttl=5)
def check_api_health(base_url):
    try:
        r = requests.get(f"{base_url}/", timeout=3)
        if r.status_code == 200:
            return True, r.json()
    except Exception:
        pass
    return False, {}


@st.cache_data(ttl=10)
def fetch_metadata(base_url):
    roles = []
    cities = []
    stats = {}
    try:
        r_roles = requests.get(f"{base_url}/roles", timeout=4)
        if r_roles.status_code == 200:
            roles = r_roles.json()

        r_cities = requests.get(f"{base_url}/cities", timeout=4)
        if r_cities.status_code == 200:
            cities = r_cities.json()

        r_stats = requests.get(f"{base_url}/stats", timeout=4)
        if r_stats.status_code == 200:
            stats = r_stats.json()
    except Exception:
        pass
    return roles, cities, stats


# ---------------- Sidebar: Filters & Management ----------------
with st.sidebar:
    st.image("https://img.shields.io/badge/JobLens-Intelligence%20Platform-2563EB?style=for-the-badge&logo=compass&logoColor=white")
    st.title("Filters & Controls")

    api_online, health_data = check_api_health(API_BASE_URL)

    if api_online:
        st.success(f"🟢 Backend Online (v{health_data.get('version', '1.0')})")
    else:
        st.error("🔴 Backend Offline")
        st.info("Start the backend with:\n```powershell\nuvicorn backend.main:app --reload\n```")

    roles_list, cities_list, stats_data = fetch_metadata(API_BASE_URL)

    role_options = ["All Roles"] + (roles_list if roles_list else ["Data Analyst", "Data Scientist", "Data Engineer", "Backend Engineer"])
    selected_role = st.selectbox("Role Filter", role_options)

    city_names = ["All Cities"] + [c["city"] for c in cities_list] if cities_list else ["All Cities"]
    selected_city = st.selectbox("City Filter", city_names)

    exp_range = st.slider(
        "Experience Range (Years)",
        min_value=0,
        max_value=20,
        value=(0, 20),
        step=1
    )

    st.divider()
    st.subheader("Map Layer Controls")
    show_heatmap = st.checkbox("Show Heatmap Density", value=True)
    show_clusters = st.checkbox("Show Clustered Points", value=True)
    heatmap_radius = st.slider("Heatmap Blur Radius", 20, 100, 60, step=5)

    st.divider()
    st.subheader("Data Management")
    if st.button("🌱 Seed Sample Data"):
        with st.spinner("Seeding 100 sample jobs..."):
            try:
                res = requests.post(f"{API_BASE_URL}/admin/seed?count=100", timeout=10)
                if res.status_code == 200:
                    st.toast("Seeded successfully!", icon="✅")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Failed to seed.")
            except Exception as e:
                st.error(f"Error: {e}")


# ---------------- Header ----------------
st.title("🔍 JobLens — India Tech Job Market Intelligence")
st.caption("Real-time geographic demand intelligence, role taxonomy, and spatial market analytics")

if not api_online:
    st.warning("⚠️ Cannot communicate with backend API at `" + API_BASE_URL + "`. Please ensure FastAPI is running.")
    st.stop()


# ---------------- KPI Metrics Row ----------------
m1, m2, m3, m4 = st.columns(4)
total_jobs = stats_data.get("total_jobs", 0)
total_cities = stats_data.get("total_cities", 0)
total_companies = stats_data.get("total_companies", 0)
avg_min_sal = stats_data.get("avg_salary_min")
avg_max_sal = stats_data.get("avg_salary_max")

m1.metric("Total Jobs Indexed", f"{total_jobs:,}")
m2.metric("Active Tech Hubs", f"{total_cities}")
m3.metric("Companies Hiring", f"{total_companies}")
sal_display = f"₹{avg_min_sal//100000}L - ₹{avg_max_sal//100000}L" if avg_min_sal and avg_max_sal else "N/A"
m4.metric("Avg Salary Range", sal_display)

st.markdown("---")


# ---------------- Prepare Query Parameters ----------------
query_params = {
    "exp_min": exp_range[0],
    "exp_max": exp_range[1]
}
if selected_role != "All Roles":
    query_params["role"] = selected_role
if selected_city != "All Cities":
    query_params["city"] = selected_city


# ---------------- Fetch Map Heatmap Data ----------------
try:
    map_resp = requests.get(f"{API_BASE_URL}/map/heatmap", params=query_params, timeout=15)
    map_resp.raise_for_status()
    map_data = map_resp.json()
except Exception as e:
    st.error(f"Failed to fetch map data: {e}")
    map_data = []


# ---------------- Tab Navigation ----------------
tab_map, tab_analytics, tab_listings = st.tabs([
    "🗺️ Geospatial Demand Map",
    "📊 Market Analytics",
    "📋 Explore Job Listings"
])


# ==========================================
# TAB 1: GEOSPATIAL MAP
# ==========================================
with tab_map:
    if not map_data:
        st.info("No job postings match the selected filter criteria. Try adjusting the role or experience slider.")
    else:
        df_map = pd.DataFrame(map_data)

        # Center on India
        view_state = pdk.ViewState(
            latitude=21.7679,
            longitude=78.8718,
            zoom=4.2,
            pitch=15,
        )

        layers = []

        if show_heatmap:
            layers.append(
                pdk.Layer(
                    "HeatmapLayer",
                    data=df_map,
                    get_position=["lon", "lat"],
                    get_weight="job_count",
                    radiusPixels=heatmap_radius,
                    intensity=1.2,
                    threshold=0.05
                )
            )

        if show_clusters:
            layers.append(
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df_map,
                    get_position=["lon", "lat"],
                    get_radius="job_count * 1500",
                    get_fill_color=[235, 75, 75, 180],
                    pickable=True,
                    auto_highlight=True,
                )
            )

        deck = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip={"text": "📍 {city}\n💼 Openings: {job_count}"},
            map_style="light"
        )

        st.pydeck_chart(deck, use_container_width=True)

        st.caption(f"Displaying **{len(df_map)}** geographic demand clusters matching current criteria.")


# ==========================================
# TAB 2: MARKET ANALYTICS
# ==========================================
with tab_analytics:
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Top Tech Hubs by Job Openings")
        if cities_list:
            df_cities = pd.DataFrame(cities_list)
            st.bar_chart(df_cities.set_index("city")["job_count"])
        else:
            st.info("No city distribution data available.")

    with col_chart2:
        st.subheader("Demand by Role Category")
        if map_data:
            # Aggregate jobs by city from filtered map data
            df_agg = pd.DataFrame(map_data)
            st.dataframe(
                df_agg[["city", "job_count"]].rename(columns={"city": "City", "job_count": "Available Openings"}),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No aggregated role data available.")


# ==========================================
# TAB 3: EXPLORE JOB LISTINGS
# ==========================================
with tab_listings:
    st.subheader("Filtered Job Listings")
    try:
        jobs_resp = requests.get(f"{API_BASE_URL}/jobs", params={**query_params, "limit": 100}, timeout=15)
        jobs_resp.raise_for_status()
        jobs_payload = jobs_resp.json()
        jobs_items = jobs_payload.get("jobs", [])

        if jobs_items:
            df_jobs = pd.DataFrame(jobs_items)
            display_cols = ["title", "normalized_role", "company", "city", "experience_min", "experience_max", "posted_date", "source"]
            present_cols = [c for c in display_cols if c in df_jobs.columns]

            st.dataframe(
                df_jobs[present_cols].rename(columns={
                    "title": "Job Title",
                    "normalized_role": "Role",
                    "company": "Company",
                    "city": "City",
                    "experience_min": "Min Exp (Yrs)",
                    "experience_max": "Max Exp (Yrs)",
                    "posted_date": "Posted Date",
                    "source": "Source"
                }),
                hide_index=True,
                use_container_width=True
            )
            st.caption(f"Showing {len(df_jobs)} of {jobs_payload.get('total', len(df_jobs))} total jobs.")
        else:
            st.info("No individual job postings found matching current filters.")
    except Exception as e:
        st.error(f"Error loading job list: {e}")
