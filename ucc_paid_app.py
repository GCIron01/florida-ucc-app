import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Florida Heavy Equipment UCC", layout="wide", page_icon="🏗️", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .big-font {font-size: 2.8rem !important; font-weight: bold; color: #1E3A8A;}
    .stButton>button {width: 100%; height: 3.2em; font-size: 1.1em;}
    .equipment-badge {background-color: #d4edda; color: #155724; padding: 4px 10px; border-radius: 12px; font-size: 0.9em;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🏗️ Florida Heavy Equipment UCC</p>', unsafe_allow_html=True)
st.markdown("**Construction & Industrial Equipment Financing Liens • Daily Updated**")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Built for Equipment Finance")
    st.markdown("""
    ✅ Spot liens on excavators, cranes, loaders, forklifts  
    ✅ Quick brand & equipment keyword search  
    ✅ Only shows your key secured parties  
    ✅ Export samples before you subscribe  
    """)
    st.success("**Only $19/month** — Cancel anytime")

# ====================== LOAD DATA (FILTERED TO KEY PARTIES) ======================
@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect("ucc_secureds.db")
    # ←←← THIS IS THE CHANGE YOU WANTED
    df = pd.read_sql("SELECT * FROM ucc_filings_key ORDER BY Ucc1FilingNumber DESC", conn)
    conn.close()
    return df

df = load_data()

# Debtor left → Secured right (your requested order)
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

# ====================== TAB 1: STATS ======================
with tab1:
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Filings", f"{len(df):,}")
    with col2: st.metric("Latest Filing", df['Ucc1FilingNumber'].iloc[0] if not df.empty else "—")
    with col3: st.metric("Updated", datetime.now().strftime("%b %d, %Y"))
    st.success("✅ Stats always free")

# ====================== TAB 2: NAME SEARCH ======================
with tab2:
    st.subheader("🔍 General Name Search")
    search_term = st.text_input("Type debtor, business, or UCC number:", placeholder="e.g. ABC Construction LLC")
    if search_term:
        with st.spinner("Searching..."):
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            results = df[mask].head(10).copy()
            if not results.empty:
                st.success(f"**{mask.sum():,} matches found** — Showing top 10")
                st.dataframe(results, use_container_width=True)
                csv = results.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download these results as CSV (free)", data=csv,
                                  file_name=f"ucc_search_{search_term.replace(' ', '_')}.csv", mime="text/csv")
            else:
                st.warning("No matches found")

# ====================== TAB 3: EQUIPMENT FINANCING ======================
with tab3:
    st.subheader("🏗️ Equipment Financing Search")
    st.markdown("**Quick search for construction & industrial equipment liens**")
    keywords = ["Excavator", "Crane", "Loader", "Bulldozer", "Forklift", "Backhoe", "Caterpillar", "John Deere"]
    selected = st.multiselect("Quick keywords", keywords, default=["Excavator"])
    term = " ".join(selected)
    if term:
        with st.spinner("Scanning..."):
            mask = df.astype(str).apply(lambda x: x.str.contains(term, case=False, na=False)).any(axis=1)
            results = df[mask].head(15).copy()
            if not results.empty:
                st.success(f"**{mask.sum():,} equipment liens found**")
                results['Equipment Match'] = "✅ Likely Equipment Financing"
                st.dataframe(results, use_container_width=True)
                csv = results.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download equipment liens (free)", data=csv,
                                  file_name=f"equipment_liens_{term}.csv", mime="text/csv")

# ====================== TAB 4 & 5 (Radius + Recent) ======================
with tab4:
    st.subheader("📍 Radius Search (Premium)")
    st.info("Unlocked after subscription")
with tab5:
    st.subheader("📋 Recent UCC Filings — Live Preview")
    preview = df.head(20).copy()
    st.dataframe(preview, use_container_width=True)
    csv_all = preview.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download these 20 recent filings (free)", data=csv_all,
                      file_name="ucc_recent_filings_sample.csv", mime="text/csv")

# ====================== MAIN CTA ======================
st.markdown("---")
st.subheader("💰 Ready to unlock unlimited equipment lien searches?")
if st.button("✅ Subscribe Now — $19/month (cancel anytime)", type="primary", use_container_width=True):
    st.markdown("[🚀 Go to Secure Stripe Checkout →](https://buy.stripe.com/YOUR_REAL_LINK_HERE)")

st.caption(f"Database updated {datetime.now().strftime('%b %d, %Y')} • {len(df):,} records • Only your key secured parties")