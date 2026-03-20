import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Florida UCC Premium", layout="wide", page_icon="🔒", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .big-font {font-size: 2.8rem !important; font-weight: bold; color: #1E3A8A;}
    .stButton>button {width: 100%; height: 3.2em; font-size: 1.1em;}
    .premium-card {background-color: #f8f9fa; padding: 20px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🔒 Florida UCC Premium</p>', unsafe_allow_html=True)
st.markdown("**Daily Updated • Official Florida UCC Filings**")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Why Subscribe?")
    st.markdown("""
    ✅ Unlimited searches  
    ✅ Full export to CSV/PDF  
    ✅ Radius + advanced filters  
    ✅ Early access to new filings  
    ✅ No ads • Clean interface
    """)
    st.success("**Only $19/month** — Cancel anytime")

# ====================== LOAD DATA ======================
@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect("ucc_secureds.db")
    df = pd.read_sql("SELECT * FROM ucc_filings ORDER BY Ucc1FilingNumber DESC", conn)
    conn.close()
    return df

df = load_data()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Stats", "🔍 Name Search", "📍 Radius Search", "📋 Recent Filings"])

# ====================== TAB 1: STATS ======================
with tab1:
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Filings", f"{len(df):,}")
    with col2: st.metric("Latest Filing", df['Ucc1FilingNumber'].iloc[0] if not df.empty else "—")
    with col3: st.metric("Updated", datetime.now().strftime("%b %d, %Y"))
    st.success("✅ Stats always free")

# ====================== TAB 2: NAME SEARCH (FREE PREVIEW) ======================
with tab2:
    st.subheader("🔍 Search by Debtor / Business Name")
    search_term = st.text_input("Type name or UCC number:", placeholder="e.g. ABC Construction LLC", key="search")
    
    if search_term:
        with st.spinner("Searching..."):
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            results = df[mask].head(10).copy()
            
            if not results.empty:
                st.success(f"**{mask.sum():,} matches found** — Showing top 10")
                st.dataframe(results, use_container_width=True)
                
                csv = results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download these results as CSV (free sample)",
                    data=csv,
                    file_name=f"ucc_search_{search_term.replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No matches found")
    else:
        st.info("Try searching above to see live preview + CSV download")

# ====================== TAB 3: RADIUS (LOCKED) ======================
with tab3:
    st.subheader("📍 Radius Search (Premium)")
    st.info("Search filings near any Florida zip code — **unlocked after subscription**")
    st.button("Subscribe Now – $19/month", type="primary", key="radius_btn")

# ====================== TAB 4: RECENT FILINGS (NOW 20 RECORDS) ======================
with tab4:
    st.subheader("📋 Recent UCC Filings — Live Preview")
    preview = df.head(20).copy()                     # ← changed to 20
    
    st.dataframe(preview, use_container_width=True)
    
    csv_all = preview.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download these 20 recent filings as CSV (free)",
        data=csv_all,
        file_name="ucc_recent_filings_sample.csv",
        mime="text/csv"
    )
    st.caption("Sortable table • Full unlimited export after subscription")

# ====================== MAIN CTA ======================
st.markdown("---")
st.subheader("💰 Ready to unlock everything?")
if st.button("✅ Subscribe Now — $19/month (cancel anytime)", type="primary", use_container_width=True):
    st.markdown("[🚀 Go to Secure Stripe Checkout →](https://buy.stripe.com/YOUR_REAL_LINK_HERE)")

st.caption(f"Database updated {datetime.now().strftime('%b %d, %Y')} • {len(df):,} records • Data from official Florida UCC")