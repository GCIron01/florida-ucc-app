import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

st.set_page_config(page_title="Florida Heavy Equipment UCC - TEST", layout="wide", page_icon="🏗️")

st.title("🔧 Florida UCC Connection Test (Hardcoded)")

# TEMPORARY HARDCODED URL FOR TESTING
TEST_DB_URL = "postgresql://postgres.kffjahvpapxekbjfhinm:FloridaUCCSimplePass2026@aws-1-us-east-2.pooler.supabase.com:6543/postgres"

@st.cache_data(ttl=3600, show_spinner="Testing connection...")
def test_connection():
    st.subheader("🔍 Test Results")
    st.success("✅ Using hardcoded URL (secrets bypassed)")

    try:
        conn = psycopg2.connect(TEST_DB_URL)
        secured = pd.read_sql("SELECT COUNT(*) as count FROM secured_filings", conn)
        debtor = pd.read_sql("SELECT COUNT(*) as count FROM debtor_filings", conn)
        conn.close()
        
        st.success("🎉 **CONNECTION SUCCESSFUL!** Your URL works perfectly!")
        st.balloons()
        st.metric("Secured Filings", f"{secured.iloc[0,0]:,}")
        st.metric("Debtor Filings", f"{debtor.iloc[0,0]:,}")
        return True
    except Exception as e:
        st.error("❌ Connection failed")
        st.write(str(e))
        return False

test_connection()

st.info("If you see the green 'CONNECTION SUCCESSFUL' above → reply 'It worked!' and I'll give you the fixed full app back with secrets.")
st.info("If you still see a red error → paste the full red message here.")