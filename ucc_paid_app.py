import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Florida UCC Premium",
    layout="wide",
    page_icon="🔒",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM STYLING ======================
st.markdown("""
<style>
    .big-font {font-size: 2.8rem !important; font-weight: bold; color: #1E3A8A;}
    .stButton>button {width: 100%; height: 3.2em; font-size: 1.1em;}
    .premium-card {background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0;}
</style>
""", unsafe_allow_html=True)

# ====================== HEADER ======================
st.markdown('<p class="big-font">🔒 Florida UCC Premium</p>', unsafe_allow_html=True)
st.markdown("**Daily Updated • Official Florida UCC Filings • Secure & Reliable**")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Why Florida UCC Premium?")
    st.markdown("""
    ✅ Unlimited name & UCC searches  
    ✅ Radius search by zip code  
    ✅ Export results to CSV  
    ✅ Full debtor & secured party details  
    ✅ Early access to new filings  
    ✅ No ads • Clean & fast interface
    """)
    st.markdown("---")
    st.success("**Only $19 per month**  \nCancel anytime")
    st.caption("Perfect for lien search professionals, title companies, and attorneys.")

# ====================== LOAD DATA (CACHED) ======================
@st.cache_data(ttl=7200)  # Cache for 2 hours — much faster!
def load_data():
    try:
        conn = sqlite3.connect("ucc_secureds.db")
        df = pd.read_sql("SELECT * FROM ucc_filings ORDER BY Ucc1FilingNumber DESC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("No data found in database. Please update ucc_secureds.db")
    st.stop()

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Stats", "🔍 Name Search", "📍 Radius Search", "📋 Recent Filings"])

# --------------------- TAB 1: STATS (Always Free) ---------------------
with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Filings", f"{len(df):,}")
    with col2:
        st.metric("Latest Filing", df['Ucc1FilingNumber'].iloc[0] if not df.empty else "—")
    with col3:
        st.metric("Database Updated", datetime.now().strftime("%b %d, %Y"))
    
    st.success("✅ These stats are always free. Full search access requires subscription.")

# --------------------- TAB 2: NAME SEARCH (Free Demo) ---------------------
with tab2:
    st.subheader("🔍 Search by Debtor / Business Name")
    search_term = st.text_input("Enter name or UCC number to preview:", placeholder="e.g. ABC Construction LLC")
    
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        count = mask.sum()
        st.info(f"**{count:,}** records match your search.")
        st.warning("🔒 Subscribe to view the full results and download them.")
    else:
        st.info("Try searching a company name above to see how many matches exist.")

# --------------------- TAB 3: RADIUS SEARCH (Locked) ---------------------
with tab3:
    st.subheader("📍 Radius Search by Zip Code")
    st.info("Find filings within a certain distance of any Florida zip code.")
    st.warning("🔒 This advanced feature is locked. Subscribe to unlock location-based searches.")

# --------------------- TAB 4: RECENT FILINGS (Preview) ---------------------
with tab4:
    st.subheader("📋 Recent UCC Filings — Live Preview")
    preview = df.head(12).copy()
    
    # Show only useful columns (safely)
    display_cols = [col for col in ['Ucc1FilingNumber', 'FilingDate', 'DebtorName', 'SecuredPartyName', 'Type'] 
                   if col in preview.columns]
    st.dataframe(preview[display_cols] if display_cols else preview, use_container_width=True)
    
    st.caption("Showing the 12 most recent filings • Full table + export requires subscription")

# ====================== MAIN CTA ======================
st.markdown("---")
st.subheader("💰 Ready to unlock full access?")

col_a, col_b = st.columns([1, 3])
with col_a:
    if st.button("✅ Subscribe Now — $19/month", type="primary", use_container_width=True):
        st.markdown("[🚀 Proceed to Secure Stripe Checkout](https://buy.stripe.com/YOUR_REAL_LINK_HERE)")

with col_b:
    st.markdown("Cancel anytime • Instant access after payment")

# ====================== FOOTER ======================
st.markdown("---")
st.caption(f"""
Data sourced from official Florida UCC records • This is not legal advice • 
For informational purposes only • Database last refreshed: {datetime.now().strftime('%B %d, %Y')}
""")