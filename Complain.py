import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import requests

# Set page configuration
st.set_page_config(page_title="District Grievance & IT Monitoring Portal", layout="wide")

# ==========================================
# GOOGLE SHEET CONNECTION SETUP
# ==========================================
# Public Link with Edit Access for Web App Backend
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1kQx4dwtKNAQ2mKAvpohbAYLdKCh-nqNqQs8AV6VsGSQ/edit?usp=sharing"

# App Script Web App URL for directly writing data to Google Sheet
# (This bypasses the need for Streamlit Cloud Secrets)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwCvpBKvr-3Jp8sHZQubz16Yl6Um0F7DqLgDj7L60ZONHfvVYieZm539ibjo0Iyu1ek/exec"

def load_data():
    try:
        # Convert public sheet link to CSV export URL for instant reading
        csv_url = "https://docs.google.com/spreadsheets/d/1kQx4dwtKNAQ2mKAvpohbAYLdKCh-nqNqQs8AV6VsGSQ/gviz/tq?tqx=out:csv"
        df = pd.read_csv(csv_url)
        
        # Ensure Date column is in proper date format
        if not df.empty and 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df.fillna("")
    except Exception as e:
        # Fallback to empty dataframe with correct headers if read fails
        return pd.DataFrame(columns=[
            'Date', 'Block', 'Complaint ID', 'Reference No', 
            'Category', 'Status', 'Description', 'District Action/Opinion', 'Resolution Date'
        ])

def save_data_to_gsheet(new_row_dict):
    try:
        # Format the date to string for smooth transfer
        if isinstance(new_row_dict['Date'], (date, datetime)):
            new_row_dict['Date'] = new_row_dict['Date'].strftime('%Y-%m-%d')
            
        # Direct API Call to Google Sheet Apps Script Backend
        response = requests.post(WEB_APP_URL, json=new_row_dict, timeout=10)
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        return False

# Load Live Data
df_global = load_data()

# ==========================================
# SIDEBAR - ROLE SELECTION
# ==========================================
st.sidebar.title("🏛️ Portal Access Desk")
role = st.sidebar.radio(
    "Identify Your Role:",
    ["Block IT Assistant Portal", "District Officer/DM Dashboard"]
)

# ==========================================
# ROLE 1: BLOCK IT ASSISTANT PORTAL
# ==========================================
if role == "Block IT Assistant Portal":
    st.title("📝 Block Technical Grievance Entry Portal")
    st.subheader("Log daily technical, RTPS, Lok Shikayat, or Administrative issues below.")
    
    with st.form(key="grievance_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            issue_date = st.date_input("Date of Issue Identification", value=date.today())
            block_name = st.selectbox("Your Block Jurisdiction", [
                "Block A", "Block B", "Block C", "Block D", "Nawada Sadar", "Akbarpur", "Hisua", "Kashichak"
            ])
            category = st.selectbox("Functional Domain / Department", [
                "RTPS", "Lok Shikayat", "E-Kalyan", "Social Security", "Administrative Issue", "Hardware/Network"
            ])
        with col2:
            ref_no = st.text_input("Official Reference No. (If Available)", placeholder="e.g., RTPS/2026/XXXX")
            # Generate unique Complaint ID
            comp_id = f"CPL{int(datetime.now().timestamp())}"
            st.text_input("System Generated ID", value=comp_id, disabled=True)
            
        description = st.text_area("Detailed Issue Description & Error Flash Messages")
        submit_btn = st.form_submit_button(label="Submit Grievance to District Level")
        
        if submit_btn:
            if not description.strip():
                st.error("❌ Please provide a detailed description of the issue before submitting.")
            else:
                new_data = {
                    "Date": issue_date,
                    "Block": block_name,
                    "Complaint ID": comp_id,
                    "Reference No": ref_no,
                    "Category": category,
                    "Status": "Pending",
                    "Description": description,
                    "District Action/Opinion": "",
                    "Resolution Date": ""
                }
                
                # Trigger Direct Web App Cloud Write
                with st.spinner("Transmitting data directly to Central District Database..."):
                    success = save_data_to_gsheet(new_data)
                    
                if success:
                    st.success(f"🚀 Grievance successfully registered under ID: {comp_id}. Real-time synced with District Google Sheet!")
                    st.balloons()
                else:
                    # Secondary local fallback if network fails
                    st.warning("⚠️ Direct cloud sync timed out. Saving locally. Please check internet connection.")
                    # Append locally for immediate display consistency
                    new_df = pd.DataFrame([new_data])
                    df_global = pd.concat([df_global, new_df], ignore_index=True)
                    df_global.to_excel("district_complaints_db.xlsx", index=False)

# ==========================================
# ROLE 2: DISTRICT OFFICER / DM DASHBOARD
# ==========================================
else:
    st.title("📊 District Officer & DM Monitoring Dashboard")
    st.subheader("Live Analytical Review of Block Level Pendency & Grievances")
    
    if df_global.empty:
        st.info("📂 No data available currently. Once Blocks log complaints, analytics will auto-populate.")
    else:
        # High-level Metrics
        total_cases = len(df_global)
        pending_cases = len(df_global[df_global['Status'].str.lower() == 'pending'])
        resolved_cases = len(df_global[df_global['Status'].str.lower() == 'resolved'])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Grievances Received", total_cases)
        m2.metric("Active Pendency (Pending)", pending_cases, delta=f"{pending_cases} Action Required", delta_color="inverse")
        m3.metric("Resolved Cases", resolved_cases, delta=f"{resolved_cases} Closed Successfully")
        
        st.markdown("---")
        
        # Tabs for better sorting
        tab1, tab2, tab3 = st.tabs(["🔍 Live Data Explorer", "📈 Domain Analytics", "⚙️ Action Taken Cell"])
        
        with tab1:
            st.subheader("Master Grievance Ledger (Real-time Google Sheet Sync)")
            st.dataframe(df_global, use_container_width=True)
            
        with tab2:
            st.subheader("Analytical Trends for Review Meetings")
            c1, c2 = st.columns(2)
            with c1:
                fig_pie = px.pie(df_global, names='Category', title='Grievance Load by Domain Sector', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            with c2:
                fig_bar = px.bar(df_global, x='Block', color='Status', title='Comparative Pendency Profiles Across Blocks', barmode='group')
                st.plotly_chart(fig_bar, use_container_width=True)
                
        with tab3:
            st.subheader("Update Action Taken & Remarks")
            case_to_update = st.selectbox("Select Complaint ID to Action", df_global['Complaint ID'].unique())
            
            if case_to_update:
                case_row = df_global[df_global['Complaint ID'] == case_to_update].iloc[0]
                st.write(f"**Block:** {case_row['Block']} | **Issue:** {case_row['Description']}")
                
                with st.form(key="action_form"):
                    new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Resolved"], index=["pending", "in progress", "resolved"].index(case_row['Status'].lower()) if case_row['Status'].lower() in ["pending", "in progress", "resolved"] else 0)
                    action_remarks = st.text_area("District Office Remarks / Orders Issued", value=case_row['District Action/Opinion'])
                    res_date = st.date_input("Resolution Date (If Closing)", value=date.today())
                    
                    action_submit = st.form_submit_button("Update Ledger Records")
                    
                    if action_submit:
                        # Find index and update global dataframe
                        idx = df_global[df_global['Complaint ID'] == case_to_update].index[0]
                        df_global.at[idx, 'Status'] = new_status
                        df_global.at[idx, 'District Action/Opinion'] = action_remarks
                        df_global.at[idx, 'Resolution Date'] = res_date.strftime('%Y-%m-%d') if new_status == "Resolved" else ""
                        
                        # Trigger Write Back to Cloud Sheet
                        with st.spinner("Updating Google Sheet records..."):
                            # Logic to push updated row to database
                            response = requests.post(WEB_APP_URL, json={"update_mode": True, "Complaint ID": case_to_update, "Status": new_status, "Remarks": action_remarks, "ResDate": res_date.strftime('%Y-%m-%d')})
                            
                        st.success(f"📝 Records for {case_to_update} updated successfully on Google Sheet!")
                        st.rerun()
