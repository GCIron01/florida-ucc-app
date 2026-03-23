import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
import pgeocode
from geopy.distance import geodesic

st.set_page_config(page_title="Florida Heavy Equipment UCC Premium", layout="wide", page_icon="🏗️", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .big-font {font-size: 2.8rem !important; font-weight: bold; color: #1E3A8A;}
    .stButton>button {width: 100%; height: 3.2em; font-size: 1.1em;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🏗️ Florida Heavy Equipment UCC</p>', unsafe_allow_html=True)
st.markdown("**Construction & Industrial Equipment Financing UCC Filings**")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Why Subscribe?")
    st.markdown("✅ **UCC on excavators, cranes, loaders, forklifts**")
    st.markdown("✅ **Quick brand & equipment keyword search**")
    st.markdown("✅ **Debtor + Secured Party details side-by-side**")
    st.markdown("✅ **Export samples before you subscribe**")
    st.markdown("✅ **Radius + advanced filters**")
    st.markdown("✅ **Early access to new filings**")
    st.markdown("✅ **No ads • Clean interface**")
    st.success("**Only $19/month** — Cancel anytime")

# ====================== LOAD DATA FROM SUPABASE (NOW SPECIALIZED) ======================
@st.cache_data(ttl=3600, show_spinner="Loading Construction & Equipment Filings...")
def load_data():
    try:
        conn = psycopg2.connect(st.secrets["DB_URL"])
        df = pd.read_sql("SELECT * FROM construction_equipment_filings", conn)
        conn.close()
        
        st.success("✅ Connected to Supabase — Showing ONLY Construction & Equipment Lenders!")
        return df
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")
        return pd.DataFrame()

df = load_data()

# ====================== ZIP CODE DISTANCE HELPER ======================
@st.cache_resource
def get_nomi():
    return pgeocode.Nominatim('us')

@st.cache_data
def get_zip_coordinates(zip_code):
    nomi = get_nomi()
    location = nomi.query_postal_code(str(zip_code))
    if pd.isna(location.latitude) or pd.isna(location.longitude):
        return None
    return (location.latitude, location.longitude)

# ====================== REORDER COLUMNS ======================
desired_order = [
    'Ucc1FilingNumber',
   