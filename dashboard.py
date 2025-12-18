import streamlit as st
import pandas as pd
import time  # <--- NEW IMPORT
from database import engine
from sqlalchemy import text

# 1. Page Config
st.set_page_config(page_title="Smart Router Analytics", page_icon="💰", layout="wide")
st.title("💰 AI Cost-Control Dashboard")

# 2. Sidebar Controls
st.sidebar.header("Settings")
# The "Live Mode" toggle
auto_refresh = st.sidebar.checkbox("Enable Live Updates", value=False)
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 2)

# 3. Fetch Data
def load_data():
    try:
        conn = engine.connect()
        # Fetch only the last 50 rows to keep it fast
        query = "SELECT * FROM request_logs ORDER BY timestamp DESC LIMIT 50"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()

df = load_data()

# 4. Display Metrics
if not df.empty:
    # Calculate totals
    total_saved = df["money_saved"].sum()
    
    # Custom CSS to make the "Savings" number big and green
    st.markdown(
        f"""
        <div style="background-color:#d4edda;padding:20px;border-radius:10px;border:1px solid #c3e6cb;text-align:center">
            <h3 style="color:#155724;margin:0">Total Money Saved</h3>
            <h1 style="color:#155724;margin:0">${total_saved:.6f}</h1>
        </div>
        <br>
        """, 
        unsafe_allow_html=True
    )

    # Metrics Columns
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Requests Logged", len(df))
    col2.metric("Models Used", df['model_used'].nunique())
    col3.metric("Last Request", df.iloc[0]['timestamp'].strftime('%H:%M:%S'))

    st.divider()

    # Charts & Tables
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("Model Distribution")
        st.bar_chart(df['model_used'].value_counts())

    with col_right:
        st.subheader("Recent Live Logs")
        # Show specific columns
        display_df = df[['timestamp', 'prompt_text', 'difficulty_level', 'model_used', 'money_saved']]
        st.dataframe(display_df, hide_index=True)

else:
    st.info("Waiting for data... Send a request via FastAPI!")

# 5. Auto-Refresh Logic
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()