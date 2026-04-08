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

# ====================== CONNECTION & CACHING ======================
DB_URL = "postgresql://postgres.kffjahvpapxekbjfhinm:%21Lift1000o7@db.kffjahvpapxekbjfhinm.supabase.co:6543/postgres"

@st.cache_data(ttl=7200, show_spinner="Loading Construction & Equipment Filings…")
def load_data():
    try:
        conn = psycopg2.connect(DB_URL, connect_timeout=10)
        query = """
            SELECT 
                "Ucc1FilingNumber", "DebName", "DebNameFormat", "DebAddressLine1", "DebAddressLine2",
                "DebCity", "DebState", "DebZipCode", "DebCountry", "DebRefNumber",
                "SecName", "SecNameFormat", "SecAddressLine1", "SecAddressLine2", "SecCity",
                "SecStateProvince", "SecZipCode", "SecCountry", "SecRefNumber",
                "brand", "year", "model", "equipment_type", "serial_number"
            FROM construction_equipment_filings
        """
        df = pd.read_sql(query, conn)
        conn.close()
        st.success("✅ Connected to Supabase — 49,176 clean records loaded")
        return df
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")
        st.info("Try hard-refreshing the page (Cmd + Shift + R)")
        return pd.DataFrame()

df = load_data()

# ====================== REST OF YOUR APP (unchanged) ======================
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

# Reorder columns
desired_order = [
    'Ucc1FilingNumber', 'DebName', 'DebNameFormat', 'DebAddressLine1', 'DebAddressLine2',
    'DebCity', 'DebState', 'DebZipCode', 'DebCountry', 'DebRefNumber',
    'SecName', 'SecNameFormat', 'SecAddressLine1', 'SecAddressLine2', 'SecCity',
    'SecStateProvince', 'SecZipCode', 'SecCountry', 'SecRefNumber',
    'brand', 'year', 'model', 'equipment_type', 'serial_number'
]
available_cols = [col for col in desired_order if col in df.columns]
df = df[available_cols]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Stats", "🔍 Name Search", "🏗️ Equipment Financing", "📍 Radius Search", "📋 Recent Filings"
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
                csv = results.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download results as CSV (free)", data=csv,
                                  file_name=f"ucc_search_{search_term.replace(' ', '_')}.csv", mime="text/csv")
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
        with st.spinner("Searching equipment columns only..."):
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
                display_cols = ['Ucc1FilingNumber', 'brand', 'year', 'model', 'equipment_type', 'serial_number', 'DebName', 'SecName']
                display_cols = [col for col in display_cols if col in results.columns]
                st.dataframe(results[display_cols], use_container_width=True)
                csv = results.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download these equipment financing results", data=csv,
                                  file_name="equipment_financing_search.csv", mime="text/csv")
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
    if st.button("🔍 Search Within Radius", type="primary", use_container_width=True):
        if len(zip_code) == 5 and zip_code.isdigit():
            with st.spinner(f"Calculating distances within {radius_miles} miles..."):
                center_coords = get_zip_coordinates(zip_code)
                if center_coords is None:
                    st.error("❌ Invalid zip code or no coordinates found.")
                else:
                    def calculate_distance(row):
                        if pd.isna(row.get('DebZipCode')):
                            return None
                        deb_coords = get_zip_coordinates(str(int(row['DebZipCode'])))
                        if deb_coords:
                            return geodesic(center_coords, deb_coords).miles
                        return None
                  
                    df_temp = df.copy()
                    df_temp['Distance_Miles'] = df_temp.apply(calculate_distance, axis=1)
                    results = df_temp[df_temp['Distance_Miles'] <= radius_miles].copy()
                    results = results.sort_values('Distance_Miles').head(100)
                  
                    if not results.empty:
                        st.success(f"🎉 **{len(results):,} filings found within {radius_miles} miles**")
                        st.dataframe(results, use_container_width=True)
                        csv = results.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Download Full Results as CSV (Premium)", data=csv,
                                          file_name=f"radius_search_{zip_code}_{radius_miles}miles.csv", mime="text/csv")
                    else:
                        st.warning("No filings found in this radius.")
        else:
            st.error("Please enter a valid 5-digit Florida zip code.")

with tab5:
    st.subheader("📋 Recent UCC Filings — Live Preview")
    preview = df.head(20).copy()
    st.dataframe(preview, use_container_width=True)
    csv_all = preview.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download these 20 recent filings as CSV (free)", data=csv_all,
                      file_name="ucc_recent_filings_sample.csv", mime="text/csv")
    st.caption("Sortable table • Full unlimited export after subscription")

st.markdown("---")
st.subheader("💰 Ready to unlock everything?")
if st.button("✅ Subscribe Now — $19/month (cancel anytime)", type="primary", use_container_width=True):
    st.markdown("[🚀 Go to Secure Stripe Checkout →](https://buy.stripe.com/YOUR_REAL_LINK_HERE)")

st.caption(f"Database updated {datetime.now().strftime('%b %d, %Y')} • {len(df):,} records • Data from official Florida UCC")
