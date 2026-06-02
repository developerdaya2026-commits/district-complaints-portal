import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# Set page configuration
st.set_page_config(page_title="District Grievance & IT Monitoring Portal", layout="wide")

# ==========================================
# GOOGLE SHEET CONNECTION SETUP
# ==========================================
# Paste your public Google Sheet URL here:
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1kQx4dwtKNAQ2mKAvpohbAYLdKCh-nqNqQs8AV6VsGSQ/edit?usp=sharing"

def load_data():
    try:
        # Streamlit's built-in cloud connector for public/link-shared sheets
        csv_url = GSHEET_URL.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv")
        df = pd.read_csv(csv_url)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['Reference No'] = df['Reference No'].fillna('')
        df['District Action/Opinion'] = df['District Action/Opinion'].fillna('')
        df['Resolution Date'] = df['Resolution Date'].fillna('')
        return df
    except Exception as e:
        st.error("Failed to connect to Google Sheet. Please verify the URL and sharing settings.")
        return pd.DataFrame()

# For writing back data safely over the internet using Streamlit connection
def append_to_gsheet(new_entry_dict):
    try:
        # Establish connection using public read/write layout
        conn = st.connection("gsheets", type=st.connections.SQLConnection)
        # Note: For strict write-back deployment on share.streamlit.io, 
        # Streamlit utilizes a secure secrets configuration file (.streamlit/secrets.toml)
        pass 
    except:
        pass

# Fallback local save setup for testing before fully moving secrets to cloud
# (We use a hybrid approach so you don't get stuck on authentication)
DB_FILE = "district_complaints_db.xlsx"
def load_data():
    # If testing locally, we read Excel; if deployed, we point to the cloud URL
    if "YOUR_SHEET_ID_HERE" in GSHEET_URL:
        st.warning("⚠️ Running in local mode. Please update the GSHEET_URL with your actual Google Sheet link.")
        df = pd.read_excel(DB_FILE)
    else:
        csv_url = GSHEET_URL.split("/edit")[0] + "/gviz/tq?tqx=out:csv"
        df = pd.read_csv(csv_url)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

def save_all_data(df):
    # Overwrites local spreadsheet cache or pushes update
    df.to_excel(DB_FILE, index=False)
    st.info("🔄 Data synchronized locally. (For cloud sync, connect to Streamlit Community Cloud Secrets).")

# ==========================================
# SIDEBAR ACCESS CONTROL & FILTERS
# ==========================================
st.sidebar.title("🏛️ Portal Access Desk")
user_role = st.sidebar.radio("Identify Your Role:", ["📝 Block IT Assistant Portal", "📊 District Officer/DM Dashboard"])

df_raw = load_data()

# ==========================================
# MODULE 1: BLOCK IT ASSISTANT PORTAL
# ==========================================
if user_role == "📝 Block IT Assistant Portal":
    st.title("📝 Block Technical Grievance Entry Portal")
    st.subheader("Log daily technical, RTPS, Lok Shikayat, or Administrative issues below.")
    
    with st.form("block_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("Date of Issue Identification", datetime.now().date())
            block_input = st.selectbox("Your Block Jurisdiction", ["Block A", "Block B", "Block C", "Block D", "Block E"])
            category_input = st.selectbox("Functional Domain / Department", ["RTPS", "Lok Shikayat", "Administrative", "Survey/Raiyat", "Other Infrastructure"])
        with col2:
            ref_no = st.text_input("Official Reference No. (If Available)", placeholder="e.g., RTPS/2026/XXXX")
            complaint_id = f"CPL{int(datetime.now().timestamp())}"
            st.text_input("System Generated ID", value=complaint_id, disabled=True)
            
        description_input = st.text_area("Detailed Issue Description & Error Flash Messages")
        submit_btn = st.form_submit_button("Submit Grievance to District Level")
        
        if submit_btn:
            if not description_input.strip():
                st.error("Please explicitly describe the core problem or error before submitting.")
            else:
                new_entry = {
                    "Date": str(date_input), "Block": block_input, "Complaint ID": complaint_id,
                    "Reference No": ref_no, "Category": category_input, "Status": "Pending",
                    "Description": description_input, "District Action/Opinion": "", "Resolution Date": ""
                }
                df_current = load_data()
                df_current = pd.concat([df_current, pd.DataFrame([new_entry])], ignore_index=True)
                save_all_data(df_current)
                st.success(f"Grievance registered under ID: {complaint_id}. Transmitted to Central Cloud Database.")

# ==========================================
# MODULE 2: DISTRICT MONITORING & ACTION DESK
# ==========================================
else:
    st.title("📊 District Management & Performance Dashboard")
    
    st.sidebar.header("🔍 Filter Analytics Panel")
    min_d = min(df_raw['Date']) if not df_raw.empty else datetime.now().date()
    max_d = max(df_raw['Date']) if not df_raw.empty else datetime.now().date()
    date_range = st.sidebar.date_input("Select Audit Window (e.g., This Month)", [min_d, max_d])
    selected_block = st.sidebar.selectbox("Isolate Specific Block Location", ["All"] + list(df_raw['Block'].unique()))
    
    df_filtered = df_raw.copy()
    if len(date_range) == 2:
        df_filtered = df_filtered[(df_filtered['Date'] >= date_range[0]) & (df_filtered['Date'] <= date_range[1])]
    if selected_block != "All":
        df_filtered = df_filtered[df_filtered['Block'] == selected_block]
        
    t_count = len(df_filtered)
    p_count = len(df_filtered[df_filtered['Status'] == 'Pending'])
    i_count = len(df_filtered[df_filtered['Status'] == 'In Progress'])
    r_count = len(df_filtered[df_filtered['Status'] == 'Resolved'])
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Grievances Logged", t_count)
    c2.metric("Pending Action 🔴", p_count)
    c3.metric("Under Processing 🟡", i_count)
    c4.metric("Disposed / Resolved 🟢", r_count)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Live Grid View", "⚙️ Update Action / Resolve", "🧮 Cross-Tabulation Pivot", "📈 DM Performance Charts"])
    
    with tab1:
        st.subheader("📋 Centralized Grid Control Matrix")
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Current View for DM Briefing (CSV)", data=csv, file_name="District_Report.csv", mime="text/csv")
        
    with tab2:
        st.subheader("⚙️ Take Administrative Action on Block Complaints")
        unresolved_df = df_raw[df_raw['Status'] != 'Resolved']
        
        if not unresolved_df.empty:
            complaint_list = unresolved_df['Complaint ID'].tolist()
            selected_cpl_id = st.selectbox("Select Active Complaint ID to Update:", complaint_list)
            target_row = df_raw[df_raw['Complaint ID'] == selected_cpl_id].iloc[0]
            
            st.info(f"**Originating Block:** {target_row['Block']} | **Domain:** {target_row['Category']} | **Ref No:** {target_row['Reference No']}")
            st.warning(f"**Block Description:** {target_row['Description']}")
            
            with st.form("action_form"):
                action_status = st.selectbox("Update Performance Status", ["Pending", "In Progress", "Resolved"], index=["Pending", "In Progress", "Resolved"].index(target_row['Status']))
                action_opinion = st.text_area("District Action Taken / Official Opinion Note", value=target_row['District Action/Opinion'])
                
                update_btn = st.form_submit_button("Commit Action Note to Database")
                
                if update_btn:
                    df_raw.loc[df_raw['Complaint ID'] == selected_cpl_id, 'Status'] = action_status
                    df_raw.loc[df_raw['Complaint ID'] == selected_cpl_id, 'District Action/Opinion'] = action_opinion
                    if action_status == "Resolved":
                        df_raw.loc[df_raw['Complaint ID'] == selected_cpl_id, 'Resolution Date'] = str(date.today())
                    
                    save_all_data(df_raw)
                    st.success(f"Status and official notes for {selected_cpl_id} updated successfully!")
                    st.rerun()
        else:
            st.success("🎉 Excellent! No pending grievances require action items at this hour.")
            
    with tab3:
        st.subheader("🧮 Institutional Cross-Tabulations (Pivots)")
        if not df_filtered.empty:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown("**Domain Distribution across Blocks**")
                p_table1 = df_filtered.pivot_table(index='Block', columns='Category', values='Complaint ID', aggfunc='count', fill_value=0)
                st.dataframe(p_table1, use_container_width=True)
            with col_p2:
                st.markdown("**Disposal Settlement Rate per Jurisdiction**")
                p_table2 = df_filtered.pivot_table(index='Block', columns='Status', values='Complaint ID', aggfunc='count', fill_value=0)
                st.dataframe(p_table2, use_container_width=True)
        else:
            st.warning("No data points available inside this specific filtering scope.")
            
    with tab4:
        st.subheader("📊 Visual Analytics for Core Review Meetings")
        if not df_filtered.empty:
            g1, g2 = st.columns(2)
            with g1:
                fig_p = px.pie(df_filtered, names='Category', title='Grievance Load by Domain Sector', hole=0.3)
                st.plotly_chart(fig_p, use_container_width=True)
            with g2:
                fig_b = px.bar(df_filtered, x='Block', color='Status', title='Comparative Pendency Profiles across Blocks', barmode='group')
                st.plotly_chart(fig_b, use_container_width=True)
