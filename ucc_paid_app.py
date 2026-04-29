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

# ====================== CONNECTION ======================
DB_URL = "postgresql://postgres.kffjahvpapxekbjfhinm:%21Lift1000o7@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

@st.cache_data(ttl=7200, show_spinner="Loading Construction & Equipment Filings…")
def load_data():
    try:
        conn = psycopg2.connect(DB_URL, connect_timeout=10)
        df = pd.read_sql("SELECT * FROM construction_equipment_filings_v2", conn)
        conn.close()
        st.success(f"✅ Connected to Supabase — {len(df):,} key lender records loaded")
        return df
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")
        st.info("Try hard-refreshing the page (Cmd + Shift + R)")
        return pd.DataFrame()

df = load_data()

# ====================== ZIP CODE HELPER ======================
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

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Stats", "🔍 Name Search", "🏗️ Equipment Financing", "📍 Radius Search", "📋 Recent Filings", "🏆 Top Debtors"
])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Filings", f"{len(df):,}")
    with col2: st.metric("Latest Filing", df['Ucc1FilingNumber'].iloc[0] if not df.empty else "—")
    with col3:
        today = datetime.now().strftime("%b %d, %Y")
        st.metric("Updated", today)
    st.success("✅ Stats always free")

with tab2:
    st.subheader("🔍 General Name Search")
    search_term = st.text_input("Type debtor, business, or UCC number:", placeholder="e.g. ABC Construction LLC")
    if search_term:
        with st.spinner("Searching..."):
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            results = df[mask].head(10).copy()
            if not results.empty:
                st.success(f"**{mask.sum():,} matches found**")
                st.dataframe(results, use_container_width=True)
            else:
                st.warning("No matches found")

with tab3:
    st.subheader("🏗️ Equipment Financing Search")
    st.markdown("**Search by Brand, Equipment Type, or Model**")
    col1, col2 = st.columns(2)
    with col1:
        brand_list = st.multiselect("Brand", ["CATERPILLAR", "JOHN DEERE", "KUBOTA", "KOMATSU", "CASE", "BOBCAT", "CROWN", "HITACHI", "VOLVO"], default=[])
        equipment_list = st.multiselect("Equipment Type", ["COMPACT TRACK LOADER", "EXCAVATOR", "TRACTOR", "WHEEL LOADER", "FORKLIFT", "DOZER", "MOWER", "UTILITY VEHICLE", "SKID STEER"], default=[])
    with col2:
        model_input = st.text_input("Model", placeholder="e.g. 317G or 275-05XE")
    if st.button("🔍 Search Equipment Filings", type="primary", use_container_width=True):
        with st.spinner("Searching..."):
            mask = pd.Series([True] * len(df), index=df.index)
            if brand_list:
                mask &= df['brand'].isin(brand_list)
            if equipment_list:
                mask &= df['equipment_type'].isin(equipment_list)
            if model_input:
                mask &= df['model'].astype(str).str.contains(model_input, case=False, na=False)
            results = df[mask].copy()
            if not results.empty:
                st.success(f"**{len(results):,} equipment financing filings found**")
                display_cols = ['Ucc1FilingNumber', 'brand', 'model', 'equipment_type', 'serial_number', 'DebName', 'SecName']
                display_cols = [col for col in display_cols if col in results.columns]
                st.dataframe(results[display_cols], use_container_width=True)
            else:
                st.warning("No matching equipment filings found.")

with tab4:
    st.subheader("📍 Radius Search (Premium)")
    st.markdown("**Find UCC filings within X miles of any Florida zip code**")
    
    col_a, col_b = st.columns([3, 2])
    with col_a:
        zip_code = st.text_input("Enter Florida Zip Code", placeholder="33101", max_chars=5)
    with col_b:
        radius_miles = st.slider("Search Radius (miles)", min_value=5, max_value=150, value=25, step=5)

    # === Filters (City, County, MSA) ===
    selected_cities = []
    if 'DebCity' in df.columns:
        city_list = sorted(df['DebCity'].dropna().unique())
        selected_cities = st.multiselect("Filter by City", options=city_list, default=[])

    selected_counties = []
    if 'debcounty' in df.columns:
        county_list = sorted(df['debcounty'].dropna().unique())
        selected_counties = st.multiselect("Filter by County", options=county_list, default=[])

    selected_msa = []
    if 'msa' in df.columns:
        msa_list = sorted(df['msa'].dropna().unique())
        selected_msa = st.multiselect("Filter by MSA", options=msa_list, default=[])

    if st.button("🔍 Search Within Radius", type="primary", use_container_width=True):
        if len(zip_code) == 5 and zip_code.isdigit():
            with st.spinner(f"Calculating distances within {radius_miles} miles..."):
                center_coords = get_zip_coordinates(zip_code)
                if center_coords is None:
                    st.error("❌ Invalid zip code or no coordinates found.")
                else:
                    def calculate_distance(row):
                        if pd.isna(row.get('SecZipCode')):
                            return None
                        sec_coords = get_zip_coordinates(str(row['SecZipCode']).strip()[:5])
                        if sec_coords:
                            return geodesic(center_coords, sec_coords).miles
                        return None
                    
                    df_temp = df.copy()
                    df_temp['Distance_Miles'] = df_temp.apply(calculate_distance, axis=1)
                    results = df_temp[df_temp['Distance_Miles'] <= radius_miles].copy()
                    
                    # Apply filters
                    if selected_cities and 'DebCity' in results.columns:
                        results = results[results['DebCity'].isin(selected_cities)]
                    if selected_counties and 'debcounty' in results.columns:
                        results = results[results['debcounty'].isin(selected_counties)]
                    if selected_msa and 'msa' in results.columns:
                        results = results[results['msa'].isin(selected_msa)]
                    
                    results = results.sort_values('Distance_Miles').head(100)
                    
                    if not results.empty:
                        st.success(f"🎉 **{len(results):,} filings found within {radius_miles} miles**")
                        
                        # DEBTOR-FOCUSED COLUMNS FIRST
                        display_cols = [
                            'Ucc1FilingNumber',
                            'DebName',          # Debtor name first
                            'DebCity',
                            'debcounty',
                            'msa',
                            'Distance_Miles',
                            'brand',
                            'model',
                            'equipment_type',
                            'SecName'           # Secured party last
                        ]
                        display_cols = [col for col in display_cols if col in results.columns]
                        st.dataframe(results[display_cols], use_container_width=True)
                    else:
                        st.warning("No filings found in this radius.")
        else:
            st.error("Please enter a valid 5-digit Florida zip code.")

with tab5:
    st.subheader("📋 Recent UCC Filings — Live Preview")
    preview = df.head(20).copy()
    st.dataframe(preview, use_container_width=True)

with tab6:
    st.subheader("🏆 Top Debtors by Number of Filings")
    st.markdown("**Debtors with the most UCC filings in the database**")

    if not df.empty:
        # Group by debtor and calculate stats
        top_debtors = df.groupby(['DebName', 'DebAddressLine1', 'DebCity', 'DebState', 'DebZipCode']).agg(
            total_filings=('Ucc1FilingNumber', 'count'),
            unique_secured=('SecName', 'nunique')
        ).reset_index()

        # Create clean address column
        top_debtors['Address'] = (
            top_debtors['DebAddressLine1'].fillna('') + 
            ", " + top_debtors['DebCity'].fillna('') + 
            ", " + top_debtors['DebState'].fillna('') + 
            " " + top_debtors['DebZipCode'].fillna('')
        ).str.strip(', ')

        # Sort by most filings
        top_debtors = top_debtors.sort_values('total_filings', ascending=False)

        # Display nice table
        display_cols = ['DebName', 'Address', 'total_filings', 'unique_secured']
        st.dataframe(
            top_debtors[display_cols].head(50).rename(columns={
                'DebName': 'Debtor Name',
                'total_filings': 'Total Filings',
                'unique_secured': 'Unique Secured Parties'
            }),
            use_container_width=True,
            hide_index=True
        )

        st.caption("Showing top 50 debtors • Full list available after subscription")
    else:
        st.warning("No data available")
        
st.markdown("---")
st.caption(f"Database updated {datetime.now().strftime('%b %d, %Y')} • {len(df):,} records • Data from official Florida UCC")
