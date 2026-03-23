import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

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

# ====================== LOAD DATA FROM SUPABASE ======================
@st.cache_data(ttl=3600, show_spinner="Connecting to Supabase...")
def load_data():
    try:
        conn = psycopg2.connect(st.secrets["DB_URL"])
        secured = pd.read_sql("SELECT * FROM secured_filings", conn)
        debtor = pd.read_sql("SELECT * FROM debtor_filings", conn)
        conn.close()
        
        df = pd.merge(secured, debtor, on="Ucc1FilingNumber", how="left")
        
        st.success("✅ Connected to Supabase successfully! 🎉")
        return df
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")
        return pd.DataFrame()

df = load_data()

# ====================== REORDER COLUMNS ======================
desired_order = [
    'Ucc1FilingNumber',
    'DebName', 'DebNameFormat', 'DebAddressLine1', 'DebAddressLine2', 'DebCity', 'DebState',
    'DebZipCode', 'DebCountry', 'DebRefNumber', 'DebRelToFiling', 'DebOrigParty', 'DebFilingStatus',
    'SecName', 'SecNameFormat', 'SecAddressLine1', 'SecAddressLine2', 'SecCity', 'SecStateProvince',
    'SecZipCode', 'SecCountry', 'SecRefNumber', 'SecRelToFiling', 'SecOrigParty', 'SecFilingStatus'
]
available_cols = [col for col in desired_order if col in df.columns]
df = df[available_cols]

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Stats", "🔍 Name Search", "🏗️ Equipment Financing", "📍 Radius Search", "📋 Recent Filings"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Filings", f"{len(df):,}")
    with col2: st.metric("Latest Filing", df['Ucc1FilingNumber'].iloc[0] if not df.empty else "—")
    with col3: st.metric("Updated", datetime.now().strftime("%b %d, %Y"))
    st.success("✅ Stats always free")

with tab2:
    st.subheader("🔍 General Name Search")
    search_term = st.text_input("Type debtor, business, or UCC number:", placeholder="e.g. ABC Construction LLC")
    if search_term: