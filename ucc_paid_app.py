import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import pgeocode
from geopy.distance import geodesic

st.set_page_config(page_title="Florida UCC Premium", layout="wide", page_icon="🔒", initial_sidebar_state="collapsed")

st.title("🔒 Florida UCC Daily Filings")
st.markdown("**Name Search + Radius Search** — Separate tabs")

conn = sqlite3.connect("ucc_secureds.db")
df = pd.read_sql("SELECT * FROM ucc_filings ORDER BY Ucc1FilingNumber DESC", conn)

tab1, tab2, tab3, tab4 = st.tabs(["📋 Recent Filings", "🔍 Name Search", "📍 Radius Search", "📊 Stats"])

with tab1:
    st.dataframe(df[["Ucc1FilingNumber", "SecName", "DebName", "DebCity", "DebZipCode"]].head(100), width="stretch", hide_index=True)

with tab2:
    st.subheader("Search by Name or Company")
    text_search = st.text_input("Business Name, Debtor Name, or UCC Number", "")
    if text_search:
        filtered = df[
            df["SecName"].str.contains(text_search, case=False, na=False) |
            df["DebName"].str.contains(text_search, case=False, na=False) |
            df["Ucc1FilingNumber"].astype(str).str.contains(text_search)
        ]
        st.success(f"✅ Found {len(filtered)} matches")
        st.dataframe(filtered[["Ucc1FilingNumber", "SecName", "DebName", "DebCity", "DebZipCode"]], width="stretch", hide_index=True)
    else:
        st.info("Type a name or UCC number above")

with tab3:
    st.subheader("Radius Search (Debtor Zip Code)")
    center_zip = st.text_input("Center Zip Code", max_chars=5)
    radius_miles = st.slider("Radius (miles)", 5, 100, 25)

    if center_zip and len(center_zip) == 5:
        nomi = pgeocode.Nominatim("us")
        center = nomi.query_postal_code(center_zip)
        if pd.isna(center.latitude):
            st.error("Invalid zip code")
        else:
            filtered = []
            for _, row in df.iterrows():
                z = str(row.get("DebZipCode", ""))[:5]
                if z.isdigit():
                    dest = nomi.query_postal_code(z)
                    if not pd.isna(dest.latitude):
                        dist = geodesic((center.latitude, center.longitude), (dest.latitude, dest.longitude)).miles
                        if dist <= radius_miles:
                            filtered.append(row)
            if filtered:
                count = len(filtered)
                st.success(f"✅ Found {count} debtors within {radius_miles} miles of {center_zip}")
                st.dataframe(pd.DataFrame(filtered)[["Ucc1FilingNumber", "SecName", "DebName", "DebCity", "DebZipCode"]], width="stretch", hide_index=True)
            else:
                st.info("No results in this radius")
    else:
        st.info("Enter a 5-digit zip code")

with tab4:
    st.metric("Total Filings", len(df))

st.markdown("---")
st.subheader("💰 Subscribe to unlock full access")
if st.button("Subscribe Now – $19/month (cancel anytime)", type="primary", use_container_width=True):
    st.markdown("[🚀 Go to Stripe Checkout →](https://buy.stripe.com/YOUR_REAL_LINK_HERE)")

st.caption(f"Database updated {datetime.now().strftime('%b %d, %Y')} • {len(df):,} records")