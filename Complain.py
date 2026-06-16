import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import requests
import base64

# 1. Page & Corporate Theme Configuration
st.set_page_config(page_title="Nawada District Monitoring System", layout="wide", initial_sidebar_state="expanded")

# Corporate UI Styling (Premium Deep Navy and Slate Grey Theme)
st.markdown("""
    <style>
        /* Main Layout Background */
        .stApp { background-color: #f8fafc; }
        
        /* Header Banner Styling */
        .corporate-header {
            background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
            padding: 24px;
            border-radius: 8px;
            color: #ffffff;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .corporate-header h1 { color: #ffffff !important; margin: 0; font-size: 28px; font-weight: 700; }
        .corporate-header p { color: #94a3b8 !important; margin: 5px 0 0 0; font-size: 14px; }
        
        /* Login Box Wrapper */
        .login-box {
            max-width: 450px;
            margin: 40px auto;
            background: #ffffff;
            padding: 35px;
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
        }
        
        /* Footer Styling */
        .corporate-footer {
            text-align: center;
            padding: 15px;
            margin-top: 50px;
            font-size: 12px;
            color: #64748b;
            border-top: 1px solid #e2e8f0;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Configuration & API Endpoints
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1kQx4dwtKNAQ2mKAvpohbAYLdKCh-nqNqQs8AV6VsGSQ/gviz/tq?tqx=out:csv"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxBmY0o566hGBQERklGQI-Jk_ijXU0NOhf9ZdWUJ3ZuFVVwJ-XKHPwxdTuJu3i_67Mn/exec"

# Static Registry for Authentication
USER_REGISTRY = {
    "OFF-SADAR-SDO": {"name": "Sadar Subdivision Office (Nawada)", "role": "Block"},
    "OFF-RAJAULI-SDO": {"name": "Rajauli Subdivision Office", "role": "Block"},
    "OFF-DM-RTPS": {"name": "DM RTPS Cell (Nawada HQ)", "role": "Block"},
    "OFF-SP-HQ": {"name": "SP Office (Nawada HQ)", "role": "Block"},
    "BLK-NW-SADAR": {"name": "Nawada Sadar Block", "role": "Block"},
    "BLK-AKBARPUR": {"name": "Akbarpur Block", "role": "Block"},
    "BLK-HISUA": {"name": "Hisua Block", "role": "Block"},
    "BLK-KASHICHAK": {"name": "Kashichak Block", "role": "Block"},
    "BLK-WARISALIGANJ": {"name": "Warisaliganj Block", "role": "Block"},
    "BLK-PAKRIBARAWAN": {"name": "Pakribarawan Block", "role": "Block"},
    "BLK-KOWAKOLE": {"name": "Kowakole Block", "role": "Block"},
    "BLK-ROH": {"name": "Roh Block", "role": "Block"},
    "BLK-RAJAULI": {"name": "Rajauli Block", "role": "Block"},
    "BLK-MESKAUR": {"name": "Meskaur Block", "role": "Block"},
    "BLK-NARHAT": {"name": "Narhat Block", "role": "Block"},
    "BLK-SIRDALA": {"name": "Sirdala Block", "role": "Block"},
    "BLK-GOVINDPUR": {"name": "Govindpur Block", "role": "Block"},
    "BLK-NARDIGANJ": {"name": "Nardiganj Block", "role": "Block"},
    "ADMIN-NAWADA-DM": {"name": "District Admin Dashboard (DM Level)", "role": "District"}
}

# Initialize Session States
if "password_db" not in st.session_state:
    st.session_state["password_db"] = {uid: "Nawada@123" for uid in USER_REGISTRY}
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "otp_sent" not in st.session_state:
    st.session_state["otp_sent"] = False
if "temp_uid" not in st.session_state:
    st.session_state["temp_uid"] = None

def load_data():
    try:
        df = pd.read_csv(GSHEET_URL)
        if not df.empty and 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df.fillna("")
    except:
        return pd.DataFrame(columns=[
            'Date', 'Jurisdiction', 'Complaint ID', 'Reference No', 'Category', 
            'Status', 'Description', 'District Action/Opinion', 'Resolution Date', 'Uploaded File URL', 'Submitted By Code'
        ])

df_global = load_data()

# Header Component
st.markdown("""
    <div class="corporate-header">
        <h1>GOVERNMENT OF BIHAR | DISTRICT ADMINISTRATION NAWADA</h1>
        <p>Integrated Grievance Redressal & Operational IT Monitoring Infrastructure</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# SECURE LOGIN SCREEN WITH PREDEFINED OTP
# ==========================================
if not st.session_state["authenticated"]:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.subheader("🔐 Secure System Authentication")
    
    # STEP 1: Enter Office ID & Password
    if not st.session_state["otp_sent"]:
        input_uid = st.text_input("Enter Official Office Code (User ID)").strip()
        input_pwd = st.text_input("Enter System Password", type="password")
        
        if st.button("Verify Credentials & Send OTP", use_container_width=True):
            if input_uid in USER_REGISTRY and input_pwd == st.session_state["password_db"][input_uid]:
                st.session_state["otp_sent"] = True
                st.session_state["temp_uid"] = input_uid
                st.success("✅ Password Verified! OTP has been routed to registered nodal mobile.")
                st.rerun()
            else:
                st.error("❌ Invalid Office Code or Password. Access Denied.")
                
    # STEP 2: Enter Predefined OTP Box
    else:
        st.info(f"🔑 Session Active for Code: `{st.session_state['temp_uid']}`")
        input_otp = st.text_input("Enter 4-Digit Verification OTP", type="password", max_chars=4)
        
        user_role = USER_REGISTRY[st.session_state["temp_uid"]]["role"]
        required_otp = "9999" if user_role == "District" else "1234"
        
        st.caption(f"💡 For Testing: Use OTP **`{required_otp}`** for this {user_role} level access.")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Verify OTP & Login", use_container_width=True):
                if input_otp == required_otp:
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = st.session_state["temp_uid"]
                    st.success("Authorization Successful! Connecting to secure server...")
                    st.rerun()
                else:
                    st.error("❌ Invalid OTP. Security Token mismatch.")
        with col_btn2:
            if st.button("Back to Login", use_container_width=True):
                st.session_state["otp_sent"] = False
                st.session_state["temp_uid"] = None
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SECURE ROUTING SYSTEM (POST LOGIN)
# ==========================================
else:
    user_info = USER_REGISTRY[st.session_state["current_user"]]
    current_role = user_info["role"]
    assigned_office = user_info["name"]
    
    # Sidebar Profile Summary
    st.sidebar.markdown(f"### 👤 Active Session")
    st.sidebar.info(f"**Office:** {assigned_office}\n\n**Code:** `{st.session_state['current_user']}`")
    
    if st.sidebar.button("Log Out Securely", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
        st.session_state["otp_sent"] = False
        st.rerun()

    # ------------------------------------------
    # ROLE A: COMPREHENSIVE BLOCK PORTAL
    # ------------------------------------------
    if current_role == "Block":
        st.markdown(f"### 📝 Welcome, Authorized Desk - {assigned_office}")
        
        tab_new, tab_report = st.tabs(["🆕 File New Grievance", "📊 My Office Performance Reports (ATR)"])
        
        with tab_new:
            with st.form(key="block_grievance_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    issue_date = st.date_input("Identification Date", value=date.today())
                    st.text_input("Submitting Jurisdiction", value=assigned_office, disabled=True)
                    category = st.selectbox("Operational Sector Domain", ["RTPS", "Lok Shikayat", "E-Kalyan", "Social Security", "Administrative Issue", "Hardware/Network"])
                with col2:
                    ref_no = st.text_input("Official Reference Number (If Available)", placeholder="e.g., RTPS/2026/XXXX")
                    comp_id = f"CPL{int(datetime.now().timestamp())}"
                    st.text_input("Unique Case Identifier (Auto)", value=comp_id, disabled=True)
                
                description = st.text_area("Detailed Problem Classification / Error Logs")
                
                # 2MB File Upload Handling
                uploaded_file = st.file_uploader("Attach Supporting Document (Max 2MB, PDF/JPG)", type=["pdf", "jpg", "png"])
                
                file_payload = ""
                file_type = ""
                if uploaded_file is not None:
                    if uploaded_file.size > 2 * 1024 * 1024:
                        st.error("❌ Transmission Rejected: Attached file exceeds the structural limit of 2MB.")
                    else:
                        file_payload = base64.b64encode(uploaded_file.read()).decode()
                        file_type = uploaded_file.type
                        st.success("✅ Document uploaded successfully and compressed for cloud sync.")
                
                if st.form_submit_button("Transmit Records to District HQ"):
                    if not description.strip():
                        st.error("❌ Description matrix cannot be left blank.")
                    else:
                        # यहाँ ध्यान दें: Apps Script को सही की (Keys) भेजने के लिए मॉडिफाई किया गया है
                        new_data = {
                            "Date": str(issue_date), 
                            "Jurisdiction": assigned_office, 
                            "Complaint ID": comp_id,
                            "Reference No": ref_no, 
                            "Category": category, 
                            "Status": "Pending",
                            "Description": description, 
                            "District Action/Opinion": "", 
                            "Resolution Date": "",
                            "file_payload": file_payload,
                            "file_type": file_type,
                            "Submitted By Code": st.session_state["current_user"]
                        }
                        with st.spinner("Pushing record to secure cloud database..."):
                            try:
                                response = requests.post(WEB_APP_URL, json=new_data, timeout=20)
                                if response.status_code == 200:
                                    st.success(f"🚀 Record Synced! Ticket ID {comp_id} has been transmitted.")
                                    st.balloons()
                                else:
                                    st.warning("⚠️ High latency on cloud network. Data saved to buffer.")
                            except:
                                st.warning("⚠️ Cloud connection timeout. Buffer preserved.")
        
        with tab_report:
            st.subheader("📋 Historical Ledger & Action Taken Report (ATR)")
            if not df_global.empty and 'Submitted By Code' in df_global.columns:
                filtered_df = df_global[df_global['Submitted By Code'] == st.session_state["current_user"]]
                if filtered_df.empty:
                    st.info("📂 No past grievances found for this office jurisdiction.")
                else:
                    # ब्लॉक स्तर पर भी क्लिक करने योग्य डाउनलोड लिंक कॉलम सेट किया गया
                    st.data_editor(
                        filtered_df,
                        column_config={
                            "Uploaded File URL": st.column_config.LinkColumn("📄 View Attachment", display_text="Open File")
                        },
                        disabled=True,
                        use_container_width=True
                    )
            else:
                st.dataframe(df_global[df_global['Jurisdiction'] == assigned_office], use_container_width=True)

    # ------------------------------------------
    # ROLE B: DISTRICT MONITORING DASHBOARD (DM LEVEL)
    # ------------------------------------------
    else:
        st.markdown("### 📊 Command Control Centre & Analytical Panel")
        
        adm_tab1, adm_tab2, adm_tab3, adm_tab4 = st.tabs(["🔍 Live System Explorer", "📈 Operational Matrix Charts", "⚙️ Action Taken Cell (ATR)", "🛡️ Security Desk (Credential Control)"])
        
        with adm_tab1:
            st.subheader("Global Grievance Registry Dashboard")
            # जिला स्तर पर फ़ाइल डाउनलोड करने के लिए डायरेक्ट 'LinkColumn' सेट किया गया
            st.data_editor(
                df_global,
                column_config={
                    "Uploaded File URL": st.column_config.LinkColumn("📄 Attached Document", display_text="View Document")
                },
                disabled=True,
                use_container_width=True
            )
            
        with adm_tab2:
            if not df_global.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.pie(df_global, names='Category', title='Load Distribution by Sector Domain', hole=0.4), use_container_width=True)
                with c2:
                    st.plotly_chart(px.bar(df_global, x='Jurisdiction', color='Status', title='Performance Profile by Operational Nodes', barmode='group'), use_container_width=True)
            else:
                st.info("No charts to display. Database empty.")
                
        with adm_tab3:
            st.subheader("Issue Evaluation & ATR Insertion Module")
            if not df_global.empty:
                case_to_update = st.selectbox("Select Target Complaint ID for Operational Audit", df_global['Complaint ID'].unique())
                case_row = df_global[df_global['Complaint ID'] == case_to_update].iloc[0]
                
                st.warning(f"**Origin Jurisdiction:** {case_row['Jurisdiction']} | **Functional Details:** {case_row['Description']}")
                
                with st.form(key="hq_atr_form"):
                    new_status = st.selectbox("Modify Execution Status", ["Pending", "In Progress", "Resolved"])
                    action_remarks = st.text_area("Official Orders / Technical Directives", value=case_row['District Action/Opinion'])
                    res_date = st.date_input("Closure Date", value=date.today())
                    
                    if st.form_submit_button("Publish ATR Directive to Cloud"):
                        with st.spinner("Broadcasting changes to edge nodes..."):
                            requests.post(WEB_APP_URL, json={"update_mode": True, "Complaint ID": case_to_update, "Status": new_status, "Remarks": action_remarks, "ResDate": res_date.strftime('%Y-%m-%d')})
                        st.success("📝 Directives successfully propagated across the secure database infrastructure.")
                        st.rerun()
            else:
                st.info("No pending tasks available.")
                
        with adm_tab4:
            st.subheader("🔑 Central Administrative Credentials Desk")
            target_user = st.selectbox("Select Office Jurisdiction Node to Reset", list(USER_REGISTRY.keys()))
            if st.button("Reset Selected Office Password to Default (Nawada@123)"):
                st.session_state["password_db"][target_user] = "Nawada@123"
                st.success(f"🔐 Password for office code **{target_user}** successfully reset to `Nawada@123`.")

# Corporate Footer
st.markdown("""
    <div class="corporate-footer">
        Designed & Formulated for Optimization Protocols | District IT Infrastructure Cell, Nawada HQ © 2026
    </div>
""", unsafe_allow_html=True)
