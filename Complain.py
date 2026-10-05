import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import requests
import base64
import io
from PIL import Image
from supabase import create_client, Client

# 1. Page & Corporate Theme Configuration
st.set_page_config(
    page_title="Nawada District Monitoring System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Supabase Client
@st.cache_resource
def init_supabase() -> Client:
    try:
        url = st.secrets["supabase"]["SUPABASE_URL"]
        key = st.secrets["supabase"]["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Supabase Configuration Error: {e}")
        return None

supabase = init_supabase()

# Enhanced Corporate UI Styling
st.markdown("""
    <style>
        /* Base typography & App background */
        .stApp {
            background-color: #f8fafc;
            font-size: 16px !important;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        }

        /* Sidebar Base Styling */
        [data-testid="stSidebar"] {
            background-color: #f1f5f9 !important;
        }

        /* FIX 2: GLOBAL CSS INJECTION FOR SIDEBAR PROFILE TEXT */
        [data-testid="stSidebar"] .sidebar-profile-card h1,
        [data-testid="stSidebar"] .sidebar-profile-card h2,
        [data-testid="stSidebar"] .sidebar-profile-card h3,
        [data-testid="stSidebar"] .sidebar-profile-card p,
        [data-testid="stSidebar"] .sidebar-profile-card span,
        [data-testid="stSidebar"] .sidebar-profile-card b,
        [data-testid="stSidebar"] .sidebar-profile-card div {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }

        /* Profile Card Specific High Contrast Styling */
        .sidebar-profile-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%) !important;
            border-radius: 14px !important;
            padding: 20px 16px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 8px 16px rgba(15, 23, 42, 0.25) !important;
            text-align: center !important;
            border: 1px solid #3b82f6 !important;
        }
        .sidebar-profile-card h3 {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            margin: 10px 0 4px 0 !important;
            font-size: 19px !important;
            font-weight: 800 !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.6) !important;
        }
        .sidebar-profile-card .desig-text {
            color: #93c5fd !important;
            -webkit-text-fill-color: #93c5fd !important;
            margin: 0 0 4px 0 !important;
            font-size: 14px !important;
            font-weight: 700 !important;
        }
        .sidebar-profile-card .office-text {
            color: #e2e8f0 !important;
            -webkit-text-fill-color: #e2e8f0 !important;
            margin: 0 0 12px 0 !important;
            font-size: 13px !important;
            font-weight: 500 !important;
        }
        .sidebar-profile-card .info-badge {
            background: rgba(255, 255, 255, 0.12) !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            padding: 10px 12px !important;
            border-radius: 8px !important;
            font-size: 12.5px !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            color: #ffffff !important;
        }
        .sidebar-profile-card .info-badge span,
        .sidebar-profile-card .info-badge b {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }

        /* Enlarge body text & markdown */
        p, span, label, .stMarkdown {
            font-size: 15.5px !important;
            color: #1e293b;
        }

        /* Header Banner Styling */
        .corporate-header {
            background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%) !important;
            padding: 26px 30px !important;
            border-radius: 12px !important;
            color: #ffffff !important;
            margin-bottom: 25px !important;
            box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.15) !important;
            text-align: center !important;
        }
        .corporate-header,
        .corporate-header *,
        .corporate-header h1,
        .corporate-header h1 * {
            color: #ffffff !important;
        }
        .corporate-header h1 {
            color: #ffffff !important;
            margin: 0 0 8px 0 !important;
            font-size: 28px !important;
            font-weight: 800 !important;
            letter-spacing: 0.8px !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4) !important;
        }
        .corporate-header p,
        .corporate-header p * {
            color: #cbd5e1 !important;
            margin: 0 !important;
            font-size: 16px !important;
            font-weight: 500 !important;
        }

        /* Headings */
        h2 { font-size: 25px !important; font-weight: 700 !important; color: #0f172a !important; }
        h3 { font-size: 21px !important; font-weight: 700 !important; color: #1e3a8a !important; }
        h4 { font-size: 18px !important; font-weight: 600 !important; color: #334155 !important; }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px !important;
            background-color: #ffffff !important;
            padding: 8px 10px !important;
            border-radius: 10px !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04) !important;
        }

        /* Inactive Tab Styling */
        .stTabs [data-baseweb="tab"],
        .stTabs button[role="tab"] {
            font-size: 16px !important;
            font-weight: 600 !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
            background-color: #f8fafc !important;
            border: 1px solid #cbd5e1 !important;
            color: #334155 !important;
            transition: all 0.2s ease-in-out !important;
        }
        .stTabs [data-baseweb="tab"] *,
        .stTabs [data-baseweb="tab"] p,
        .stTabs [data-baseweb="tab"] span,
        .stTabs [data-baseweb="tab"] div,
        .stTabs button[role="tab"] *,
        .stTabs button[role="tab"] p,
        .stTabs button[role="tab"] span,
        .stTabs button[role="tab"] div {
            color: #334155 !important;
            font-size: 16px !important;
            font-weight: 600 !important;
        }
        .stTabs [data-baseweb="tab"]:hover,
        .stTabs button[role="tab"]:hover {
            background-color: #e2e8f0 !important;
            border-color: #94a3b8 !important;
        }
        .stTabs [data-baseweb="tab"]:hover *,
        .stTabs [data-baseweb="tab"]:hover p,
        .stTabs [data-baseweb="tab"]:hover span,
        .stTabs button[role="tab"]:hover *,
        .stTabs button[role="tab"]:hover p,
        .stTabs button[role="tab"]:hover span {
            color: #0f172a !important;
        }

        /* Active Tab Styling */
        .stTabs [data-baseweb="tab"][aria-selected="true"],
        .stTabs button[role="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%) !important;
            border: 1px solid #1e3a8a !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 8px -1px rgba(30, 58, 138, 0.35) !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] *,
        .stTabs [data-baseweb="tab"][aria-selected="true"] p,
        .stTabs [data-baseweb="tab"][aria-selected="true"] span,
        .stTabs [data-baseweb="tab"][aria-selected="true"] div,
        .stTabs button[role="tab"][aria-selected="true"] *,
        .stTabs button[role="tab"][aria-selected="true"] p,
        .stTabs button[role="tab"][aria-selected="true"] span,
        .stTabs button[role="tab"][aria-selected="true"] div {
            background-color: transparent !important;
            color: #ffffff !important;
            fill: #ffffff !important;
            font-weight: 800 !important;
            font-size: 16px !important;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4) !important;
        }

        /* Clean Tab Indicators */
        .stTabs [data-baseweb="tab-highlight"],
        .stTabs [data-baseweb="tab-border"] {
            display: none !important;
        }

        /* Buttons Styling */
        .stButton > button {
            font-size: 16px !important;
            font-weight: 700 !important;
            padding: 10px 24px !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease-in-out !important;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 10px -1px rgba(0, 0, 0, 0.15);
        }

        /* Input Controls and Select boxes */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            font-size: 15.5px !important;
            border-radius: 8px !important;
        }

        /* Login Box Wrapper */
        .login-box {
            max-width: 480px;
            margin: 40px auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
        }

        /* Metric Dashboard Cards */
        .metric-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            border-left: 6px solid #1e3a8a;
            margin-bottom: 15px;
        }
        .metric-card.pending { border-left-color: #ef4444; }
        .metric-card.progress { border-left-color: #f59e0b; }
        .metric-card.disposed { border-left-color: #10b981; }

        .metric-title {
            font-size: 14px !important;
            font-weight: 700 !important;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0;
        }
        .metric-value {
            font-size: 34px !important;
            font-weight: 800 !important;
            color: #0f172a;
            margin: 6px 0 0 0;
        }

        /* Dossier Cards */
        .dossier-card {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 24px;
            margin-top: 15px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        .dossier-header {
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 12px;
            margin-bottom: 16px;
        }
        .dossier-label {
            font-size: 14px !important;
            font-weight: 700 !important;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        .dossier-content-desc {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #3b82f6;
            border-radius: 6px;
            padding: 14px 16px;
            font-size: 15.5px !important;
            line-height: 1.65;
            color: #1e293b;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .dossier-content-atr {
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-left: 4px solid #16a34a;
            border-radius: 6px;
            padding: 14px 16px;
            font-size: 15.5px !important;
            line-height: 1.65;
            color: #14532d;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        /* Status Badge */
        .badge-pending {
            background-color: #fee2e2;
            color: #991b1b;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 13.5px;
        }
        .badge-progress {
            background-color: #fef3c7;
            color: #92400e;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 13.5px;
        }
        .badge-disposed {
            background-color: #dcfce7;
            color: #166534;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 13.5px;
        }

        /* Footer Styling */
        .corporate-footer {
            text-align: center;
            padding: 20px;
            margin-top: 50px;
            font-size: 13.5px !important;
            color: #64748b;
            border-top: 1px solid #e2e8f0;
        }
    </style>
""", unsafe_allow_html=True)

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

# SESSION PERSISTENCE
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

if not st.session_state["authenticated"]:
    persisted_user = st.query_params.get("session_auth", None)
    if persisted_user and persisted_user in USER_REGISTRY:
        st.session_state["authenticated"] = True
        st.session_state["current_user"] = persisted_user

# FETCH USER PROFILE DIRECTLY FROM SUPABASE DATABASE
def get_user_profile(user_code):
    """Fetches official officer profile from Supabase user_profiles table."""
    if supabase is None or not user_code:
        return None
    try:
        res = supabase.table("user_profiles").select("*").eq("user_code", user_code).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception:
        pass
    return None

# AUTO-COMPRESSION FOR CRISP A4 PRINT-READY RESOLUTION
def process_and_compress_file(uploaded_file):
    file_bytes = uploaded_file.read()
    orig_kb = len(file_bytes) // 1024
    file_type = uploaded_file.type or "application/octet-stream"

    if file_type in ["image/jpeg", "image/jpg", "image/png"]:
        try:
            img = Image.open(io.BytesIO(file_bytes))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            max_dim = 1800
            if max(img.size) > max_dim:
                ratio = max_dim / float(max(img.size))
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            out_buf = io.BytesIO()
            img.save(out_buf, format="JPEG", quality=82, optimize=True)
            compressed_bytes = out_buf.getvalue()
            
            if len(compressed_bytes) < len(file_bytes):
                file_bytes = compressed_bytes
                file_type = "image/jpeg"
        except Exception:
            pass

    final_kb = len(file_bytes) // 1024
    return file_bytes, file_type, orig_kb, final_kb

# FILE UPLOAD LOGIC (SUPABASE STORAGE)
def upload_file_to_supabase(uploaded_file, file_prefix="complaint"):
    if uploaded_file is None or supabase is None:
        return ""
    try:
        file_bytes, file_type, orig_kb, final_kb = process_and_compress_file(uploaded_file)
        ext = uploaded_file.name.split(".")[-1] if "." in uploaded_file.name else "bin"
        file_name = f"{file_prefix}_{int(datetime.now().timestamp())}.{ext}"
        bucket_name = "complaint-documents"
        
        supabase.storage.from_(bucket_name).upload(
            file_name,
            file_bytes,
            file_options={"content-type": file_type, "x-upsert": "true"}
        )
        
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        return public_url
    except Exception as e:
        st.error(f"Error uploading file to Supabase Storage: {e}")
        return ""

# DATA LOADING & FETCHING FROM SUPABASE POSTGRESQL
def standardize_status(status_str, remarks, res_date):
    s = str(status_str).strip()
    if s in ["Disposed", "Resolved", "Closed", "Disposed / Resolved", "Disposed (ATR Issued)"]:
        return "Disposed"
    elif s in ["In Progress", "Under Enquiry", "In Process", "Under Process"]:
        return "In Progress"
    elif s == "Pending" or s == "" or s == "nan" or s is None:
        if str(remarks).strip() != "" and str(res_date).strip() != "":
            return "Disposed"
        elif str(remarks).strip() != "":
            return "In Progress"
        return "Pending"
    return s

def load_data():
    if supabase is None:
        return pd.DataFrame()
    try:
        response = supabase.table("district_complaints").select("*").order("created_at", desc=True).execute()
        data = response.data
        if not data:
            return pd.DataFrame(columns=[
                'date', 'jurisdiction', 'complaint_id', 'reference_no', 'category', 
                'status', 'description', 'district_action_opinion', 'resolution_date', 
                'uploaded_file_url', 'submitted_by_code', 'atr_response_file_url', 'Normalized_Status'
            ])
        
        df = pd.DataFrame(data)
        
        col_mapping = {
            'date': 'Date',
            'jurisdiction': 'Jurisdiction',
            'complaint_id': 'Complaint ID',
            'reference_no': 'Reference No',
            'category': 'Category',
            'status': 'Status',
            'description': 'Description',
            'district_action_opinion': 'District Action/Opinion',
            'resolution_date': 'Resolution Date',
            'uploaded_file_url': 'Uploaded File URL',
            'submitted_by_code': 'Submitted By Code',
            'atr_response_file_url': 'ATR Response File URL'
        }
        df = df.rename(columns=col_mapping)
        
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        df = df.fillna("")

        expected_cols = [
            'Date', 'Jurisdiction', 'Complaint ID', 'Reference No', 'Category', 
            'Status', 'Description', 'District Action/Opinion', 'Resolution Date', 
            'Uploaded File URL', 'Submitted By Code', 'ATR Response File URL'
        ]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""

        df['Normalized_Status'] = df.apply(
            lambda r: standardize_status(r['Status'], r['District Action/Opinion'], r['Resolution Date']),
            axis=1
        )
        return df
    except Exception as e:
        st.error(f"Failed to fetch records from Supabase: {e}")
        return pd.DataFrame()

df_global = load_data()

# Header Component
st.markdown("""
<div class="corporate-header" style="background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); padding: 26px 30px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.15); text-align: center;">
    <h1 style="color: #ffffff !important; margin: 0 0 8px 0; font-size: 28px !important; font-weight: 800 !important; letter-spacing: 0.8px; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">GOVERNMENT OF BIHAR | DISTRICT ADMINISTRATION NAWADA</h1>
    <p style="color: #cbd5e1 !important; margin: 0; font-size: 16px !important; font-weight: 500; letter-spacing: 0.3px;">Integrated Grievance Redressal &amp; Operational IT Monitoring Infrastructure</p>
</div>
""", unsafe_allow_html=True)

# SECURE LOGIN SCREEN
if not st.session_state["authenticated"]:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.subheader("🔐 Secure System Authentication")
    
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
                    st.query_params["session_auth"] = st.session_state["temp_uid"]
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

# SECURE ROUTING SYSTEM (POST LOGIN)
else:
    user_info = USER_REGISTRY[st.session_state["current_user"]]
    current_role = user_info["role"]
    assigned_office = user_info["name"]
    current_code = st.session_state["current_user"]
    
    # Live Profile Integration from Supabase
    profile_data = get_user_profile(current_code)
    
    if profile_data:
        officer_name = profile_data.get("officer_name") or "Authorized Officer"
        office_name = profile_data.get("office_name") or assigned_office
        designation = profile_data.get("designation") or "Desk Representative"
        epf_number = profile_data.get("epf_no") or "N/A"
        photo_url = profile_data.get("photo_url") or ""
    else:
        officer_name = "Authorized Officer"
        office_name = assigned_office
        designation = "Desk Representative"
        epf_number = "N/A"
        photo_url = ""

    if not str(photo_url).strip():
        photo_url = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

    # FIX 1: INLINE HTML FIX WITH EXPLICIT WHITE COLOR INJECTION
    st.sidebar.markdown(f"""
        <div class="sidebar-profile-card" style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%) !important;">
            <img src="{photo_url}" style="
                width: 100px !important;
                height: 100px !important;
                border-radius: 50% !important;
                border: 3px solid #60a5fa !important;
                margin: 0 auto 12px auto !important;
                object-fit: cover !important;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
                display: block !important;
            " />
            <h3 style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-weight: 800 !important; margin-bottom: 4px !important;">{officer_name}</h3>
            <p class="desig-text" style="color: #93c5fd !important; -webkit-text-fill-color: #93c5fd !important; font-weight: 700 !important;">{designation}</p>
            <p class="office-text" style="color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important;">{office_name}</p>
            <div class="info-badge" style="color: #ffffff !important;">
                <span style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;"><b style="color: #93c5fd !important; -webkit-text-fill-color: #93c5fd !important;">EPF No:</b> {epf_number}</span>
                <span style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;"><b style="color: #93c5fd !important; -webkit-text-fill-color: #93c5fd !important;">Code:</b> {current_code}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🔄 Refresh Data From Cloud", use_container_width=True):
        st.cache_data.clear() if hasattr(st, "cache_data") else None
        st.rerun()

    if st.sidebar.button("🚪 Log Out Securely", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
        st.session_state["otp_sent"] = False
        if "session_auth" in st.query_params:
            del st.query_params["session_auth"]
        st.rerun()

    def render_dossier_card(row_data, is_district=False):
        status_val = row_data.get('Normalized_Status', row_data.get('Status', 'Pending'))
        badge_class = "badge-pending"
        if status_val == "In Progress":
            badge_class = "badge-progress"
        elif status_val == "Disposed":
            badge_class = "badge-disposed"

        st.markdown(f"""
            <div class="dossier-card">
                <div class="dossier-header">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <span style="font-size: 20px; font-weight: 800; color: #1e3a8a;">Ticket ID: {row_data.get('Complaint ID', 'N/A')}</span>
                            <span style="margin-left: 12px; font-size: 15px; color: #64748b;">(Ref: {row_data.get('Reference No', 'N/A')})</span>
                        </div>
                        <div>
                            <span class="{badge_class}">● {status_val.upper()}</span>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 14.5px; color: #475569;">
                        <strong>Submitting Office:</strong> {row_data.get('Jurisdiction', 'N/A')} &nbsp;|&nbsp; 
                        <strong>Sector:</strong> {row_data.get('Category', 'N/A')} &nbsp;|&nbsp; 
                        <strong>Date:</strong> {row_data.get('Date', 'N/A')} &nbsp;|&nbsp;
                        <strong>Resolution Date:</strong> {row_data.get('Resolution Date', 'Awaiting ATR')}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown('<div class="dossier-label">📝 Problem Description (From Submitting Block):</div>', unsafe_allow_html=True)
            desc_text = row_data.get('Description', 'No description provided.')
            st.markdown(f'<div class="dossier-content-desc">{desc_text}</div>', unsafe_allow_html=True)
            
            c_file = str(row_data.get('Uploaded File URL', ''))
            if c_file.startswith("http"):
                st.markdown(f'<div style="margin-top: 10px;"><a href="{c_file}" target="_blank" style="text-decoration: none; font-weight: 700; color: #1e3a8a;">📄 🖨️ View / Print Original Complaint Attachment</a></div>', unsafe_allow_html=True)
            else:
                st.caption("📎 No supporting file attached by submitting office.")

        with col_d2:
            st.markdown('<div class="dossier-label">⚖ District Action Taken Report (ATR Directives):</div>', unsafe_allow_html=True)
            atr_text = row_data.get('District Action/Opinion', '')
            if not str(atr_text).strip():
                atr_text = "Pending evaluation at District Administration Level. Action Taken Report (ATR) will be published post audit."
                st.markdown(f'<div class="dossier-content-desc" style="border-left-color: #f59e0b; background: #fffbeb; color: #b45309;">⏳ {atr_text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="dossier-content-atr">✅ {atr_text}</div>', unsafe_allow_html=True)

            atr_file = str(row_data.get('ATR Response File URL', ''))
            if atr_file.startswith("http"):
                st.markdown(f'<div style="margin-top: 10px;"><a href="{atr_file}" target="_blank" style="text-decoration: none; font-weight: 700; color: #16a34a;">📄 🖨️ View / Print Official ATR Response Document</a></div>', unsafe_allow_html=True)
            else:
                st.caption("📎 No ATR response document uploaded by District.")

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
                
                description = st.text_area("Detailed Problem Classification / Error Logs (Text will auto-wrap)", height=140)
                
                uploaded_file = st.file_uploader(
                    "Attach Supporting Document (PDF, JPG, PNG - Auto-compressed to high-clarity A4 print resolution)", 
                    type=["pdf", "jpg", "png"]
                )
                
                if st.form_submit_button("🚀 Transmit Records to District HQ", use_container_width=True):
                    if not description.strip():
                        st.error("❌ Description matrix cannot be left blank.")
                    else:
                        with st.spinner("Uploading document & saving record to Supabase..."):
                            public_file_url = upload_file_to_supabase(uploaded_file, file_prefix=comp_id) if uploaded_file else ""

                            db_payload = {
                                "date": str(issue_date),
                                "jurisdiction": assigned_office,
                                "complaint_id": comp_id,
                                "reference_no": ref_no,
                                "category": category,
                                "status": "Pending",
                                "description": description,
                                "district_action_opinion": "",
                                "resolution_date": None,
                                "uploaded_file_url": public_file_url,
                                "submitted_by_code": st.session_state["current_user"],
                                "atr_response_file_url": ""
                            }
                            
                            try:
                                supabase.table("district_complaints").insert(db_payload).execute()
                                st.success(f"🚀 Record Synced! Ticket ID **{comp_id}** saved directly to Supabase Database.")
                                st.balloons()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Database Insertion Error: {e}")
        
        with tab_report:
            st.subheader("📋 Historical Ledger & Action Taken Report (ATR)")
            
            if not df_global.empty and 'Submitted By Code' in df_global.columns:
                filtered_df = df_global[df_global['Submitted By Code'] == st.session_state["current_user"]]
                if filtered_df.empty:
                    st.info("📂 No past grievances found for this office jurisdiction.")
                else:
                    total_block = len(filtered_df)
                    pending_block = len(filtered_df[filtered_df['Normalized_Status'] == "Pending"])
                    prog_block = len(filtered_df[filtered_df['Normalized_Status'] == "In Progress"])
                    disp_block = len(filtered_df[filtered_df['Normalized_Status'] == "Disposed"])

                    kb1, kb2, kb3, kb4 = st.columns(4)
                    with kb1:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Lodged</div><div class="metric-value">{total_block}</div></div>', unsafe_allow_html=True)
                    with kb2:
                        st.markdown(f'<div class="metric-card pending"><div class="metric-title">Pending</div><div class="metric-value" style="color: #ef4444;">{pending_block}</div></div>', unsafe_allow_html=True)
                    with kb3:
                        st.markdown(f'<div class="metric-card progress"><div class="metric-title">Under Review</div><div class="metric-value" style="color: #f59e0b;">{prog_block}</div></div>', unsafe_allow_html=True)
                    with kb4:
                        st.markdown(f'<div class="metric-card disposed"><div class="metric-title">Disposed / ATR Completed</div><div class="metric-value" style="color: #10b981;">{disp_block}</div></div>', unsafe_allow_html=True)

                    display_df = filtered_df.copy()
                    
                    if 'Uploaded File URL' in display_df.columns:
                        display_df['📎 Complaint File'] = display_df['Uploaded File URL'].apply(
                            lambda x: x if str(x).startswith("http") else ""
                        )
                    if 'ATR Response File URL' in display_df.columns:
                        display_df['📎 ATR Response'] = display_df['ATR Response File URL'].apply(
                            lambda x: x if str(x).startswith("http") else ""
                        )

                    display_cols = [
                        'Date', 'Complaint ID', 'Reference No', 'Category', 
                        'Normalized_Status', 'Description', 'District Action/Opinion', 
                        'Resolution Date', '📎 Complaint File', '📎 ATR Response'
                    ]
                    valid_cols = [c for c in display_cols if c in display_df.columns]

                    st.markdown("#### 📑 Summary Table (Click any row or select below for full wrapped details)")
                    st.dataframe(
                        display_df[valid_cols].rename(columns={"Normalized_Status": "Status"}),
                        column_config={
                            "📎 Complaint File": st.column_config.LinkColumn("📎 Complaint File", display_text="📄 View"),
                            "📎 ATR Response": st.column_config.LinkColumn("📎 ATR Response", display_text="📄 View"),
                            "Description": st.column_config.TextColumn("Description", width="large"),
                            "District Action/Opinion": st.column_config.TextColumn("District Action/Opinion", width="large")
                        },
                        hide_index=True,
                        use_container_width=True
                    )

                    st.markdown("---")
                    st.markdown("### 🔍 Case Dossier & Official ATR Inspector")
                    selected_cpl = st.selectbox(
                        "Select Complaint ID to read full text and print ATR:",
                        filtered_df['Complaint ID'].unique(),
                        key="block_dossier_select"
                    )
                    selected_row = filtered_df[filtered_df['Complaint ID'] == selected_cpl].iloc[0]
                    render_dossier_card(selected_row)
            else:
                st.info("No records to display.")

    # ------------------------------------------
    # ROLE B: DISTRICT MONITORING DASHBOARD (DM LEVEL)
    # ------------------------------------------
    else:
        st.markdown("### 📊 Command Control Centre & Analytical Panel")
        
        adm_tab1, adm_tab2, adm_tab3, adm_tab4 = st.tabs([
            "🔍 Live Grievance Explorer", 
            "📈 Operational Matrix & ATR Charts", 
            "⚙️ Action Taken Cell (ATR)", 
            "🛡️ Security Desk (Credential Control)"
        ])
        
        with adm_tab1:
            st.subheader("Global Grievance Registry Dashboard")
            
            if not df_global.empty:
                f_col1, f_col2, f_col3 = st.columns(3)
                with f_col1:
                    filter_status = st.selectbox("Filter by Execution Status", ["All Statuses", "Pending", "In Progress", "Disposed"])
                with f_col2:
                    all_nodes = ["All Jurisdictions"] + sorted(list(df_global['Jurisdiction'].unique()))
                    filter_node = st.selectbox("Filter by Operational Node", all_nodes)
                with f_col3:
                    all_cats = ["All Categories"] + sorted(list(df_global['Category'].unique()))
                    filter_cat = st.selectbox("Filter by Sector Domain", all_cats)

                filtered_global = df_global.copy()
                if filter_status != "All Statuses":
                    filtered_global = filtered_global[filtered_global['Normalized_Status'] == filter_status]
                if filter_node != "All Jurisdictions":
                    filtered_global = filtered_global[filtered_global['Jurisdiction'] == filter_node]
                if filter_cat != "All Categories":
                    filtered_global = filtered_global[filtered_global['Category'] == filter_cat]

                filtered_global['📎 Complaint File'] = filtered_global['Uploaded File URL'].apply(
                    lambda x: x if str(x).startswith("http") else ""
                )
                filtered_global['📎 ATR Response'] = filtered_global['ATR Response File URL'].apply(
                    lambda x: x if str(x).startswith("http") else ""
                )

                table_cols = [
                    'Date', 'Jurisdiction', 'Complaint ID', 'Reference No', 'Category', 
                    'Normalized_Status', 'Description', 'District Action/Opinion', 
                    'Resolution Date', '📎 Complaint File', '📎 ATR Response'
                ]
                valid_table_cols = [c for c in table_cols if c in filtered_global.columns]

                st.dataframe(
                    filtered_global[valid_table_cols].rename(columns={"Normalized_Status": "Status"}),
                    column_config={
                        "📎 Complaint File": st.column_config.LinkColumn("📎 Complaint File", display_text="📄 View"),
                        "📎 ATR Response": st.column_config.LinkColumn("📎 ATR Response", display_text="📄 View"),
                        "Description": st.column_config.TextColumn("Description", width="large"),
                        "District Action/Opinion": st.column_config.TextColumn("District Action/Opinion", width="large")
                    },
                    hide_index=True,
                    use_container_width=True
                )

                st.markdown("---")
                st.markdown("### 🖨️ Detailed Case File & Official ATR Dossier")
                if not filtered_global.empty:
                    chosen_case_id = st.selectbox(
                        "Select Complaint ID for full text inspection and print preparation:", 
                        filtered_global['Complaint ID'].unique(),
                        key="admin_dossier_select"
                    )
                    chosen_case_row = filtered_global[filtered_global['Complaint ID'] == chosen_case_id].iloc[0]
                    render_dossier_card(chosen_case_row, is_district=True)
            else:
                st.info("Database empty.")

        with adm_tab2:
            st.subheader("Operational Analytics & Redressal Performance")
            
            if not df_global.empty:
                total_complaints = len(df_global)
                pending_count = len(df_global[df_global['Normalized_Status'] == "Pending"])
                progress_count = len(df_global[df_global['Normalized_Status'] == "In Progress"])
                disposed_count = len(df_global[df_global['Normalized_Status'] == "Disposed"])
                disposal_rate = round((disposed_count / total_complaints) * 100, 1) if total_complaints > 0 else 0

                kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
                with kpi1:
                    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Cases</div><div class="metric-value">{total_complaints}</div></div>', unsafe_allow_html=True)
                with kpi2:
                    st.markdown(f'<div class="metric-card pending"><div class="metric-title">Pending</div><div class="metric-value" style="color: #ef4444;">{pending_count}</div></div>', unsafe_allow_html=True)
                with kpi3:
                    st.markdown(f'<div class="metric-card progress"><div class="metric-title">In Progress</div><div class="metric-value" style="color: #f59e0b;">{progress_count}</div></div>', unsafe_allow_html=True)
                with kpi4:
                    st.markdown(f'<div class="metric-card disposed"><div class="metric-title">Disposed / ATR</div><div class="metric-value" style="color: #10b981;">{disposed_count}</div></div>', unsafe_allow_html=True)
                with kpi5:
                    st.markdown(f'<div class="metric-card"><div class="metric-title">Disposal Rate</div><div class="metric-value" style="color: #1e3a8a;">{disposal_rate}%</div></div>', unsafe_allow_html=True)

                st.markdown("---")

                STATUS_COLOR_MAP = {
                    "Pending": "#ef4444",
                    "In Progress": "#f59e0b",
                    "Disposed": "#10b981"
                }

                ch_col1, ch_col2 = st.columns(2)
                
                with ch_col1:
                    status_counts = df_global['Normalized_Status'].value_counts().reset_index()
                    status_counts.columns = ['Status', 'Count']
                    fig_status = px.pie(
                        status_counts, 
                        names='Status', 
                        values='Count',
                        title='Overall Redressal Execution Breakdown (Pending vs Disposed)',
                        hole=0.45,
                        color='Status',
                        color_discrete_map=STATUS_COLOR_MAP
                    )
                    fig_status.update_traces(textposition='inside', textinfo='percent+label+value')
                    fig_status.update_layout(font=dict(size=14))
                    st.plotly_chart(fig_status, use_container_width=True)

                with ch_col2:
                    cat_counts = df_global['Category'].value_counts().reset_index()
                    cat_counts.columns = ['Category', 'Count']
                    fig_cat = px.bar(
                        cat_counts,
                        x='Category',
                        y='Count',
                        color='Category',
                        title='Grievance Volume by Sector Domain (RTPS, Lok Shikayat, etc.)',
                        text_auto=True
                    )
                    fig_cat.update_layout(font=dict(size=14), showlegend=False)
                    st.plotly_chart(fig_cat, use_container_width=True)

                st.markdown("#### 🏢 Node-wise Performance: Pending vs Disposed Breakdown")
                block_status_df = df_global.groupby(['Jurisdiction', 'Normalized_Status']).size().reset_index(name='Count')
                fig_block = px.bar(
                    block_status_df, 
                    x='Jurisdiction', 
                    y='Count', 
                    color='Normalized_Status',
                    title='Block / Subdivision Performance Matrix (Pending, In Progress & Disposed Cases)',
                    barmode='group',
                    color_discrete_map=STATUS_COLOR_MAP,
                    text_auto=True
                )
                fig_block.update_layout(
                    xaxis_tickangle=-35, 
                    font=dict(size=13.5),
                    legend_title_text='Resolution Status',
                    height=500
                )
                st.plotly_chart(fig_block, use_container_width=True)

            else:
                st.info("No data available for analytical computation.")

        # ACTION TAKEN CELL (ATR) MODULE (UPDATE SUPABASE DB)
        with adm_tab3:
            st.subheader("Issue Evaluation & ATR Insertion Module")
            
            if not df_global.empty:
                case_to_update = st.selectbox(
                    "Select Target Complaint ID for Operational Audit / ATR Directive", 
                    df_global['Complaint ID'].unique()
                )
                case_row = df_global[df_global['Complaint ID'] == case_to_update].iloc[0]
                
                render_dossier_card(case_row, is_district=True)
                
                st.markdown("#### ✍️️ Enter Official District ATR Directive")
                with st.form(key="hq_atr_form"):
                    current_stat = case_row.get('Normalized_Status', 'Pending')
                    status_options = ["Pending", "In Progress", "Disposed"]
                    default_idx = status_options.index(current_stat) if current_stat in status_options else 0
                    
                    new_status = st.selectbox("Update Execution Status", status_options, index=default_idx)
                    action_remarks = st.text_area(
                        "Official Orders / Technical Directives / Action Taken Remarks", 
                        value=case_row.get('District Action/Opinion', ''),
                        height=120
                    )
                    res_date = st.date_input("ATR Resolution Date", value=date.today())
                    
                    st.markdown("---")
                    st.markdown("**📤 Attach Supporting ATR Directive Document (Optional, PDF / Image)**")
                    atr_file = st.file_uploader(
                        "Upload ATR Response File (Auto-compressed to high-clarity A4 print resolution)", 
                        type=["pdf", "jpg", "png"],
                        key="atr_file_upload"
                    )
                    
                    if st.form_submit_button("⚖️ Publish ATR Directive to Supabase Database", use_container_width=True):
                        with st.spinner("Publishing ATR updates to Supabase..."):
                            atr_public_url = case_row.get('ATR Response File URL', '')
                            if atr_file is not None:
                                atr_public_url = upload_file_to_supabase(atr_file, file_prefix=f"ATR_{case_to_update}")
                            
                            update_payload = {
                                "status": new_status,
                                "district_action_opinion": action_remarks,
                                "resolution_date": str(res_date),
                                "atr_response_file_url": atr_public_url
                            }
                            
                            try:
                                supabase.table("district_complaints").update(update_payload).eq("complaint_id", case_to_update).execute()
                                st.success(f"📝 Directives published! Complaint ID **{case_to_update}** updated in Supabase Database.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to update ATR in Supabase: {e}")
            else:
                st.info("No pending tasks available.")

        with adm_tab4:
            st.subheader("🔑 Central Administrative Credentials Desk")
            target_user = st.selectbox("Select Office Jurisdiction Node to Reset", list(USER_REGISTRY.keys()))
            if st.button("Reset Selected Office Password to Default (Nawada@123)", use_container_width=True):
                st.session_state["password_db"][target_user] = "Nawada@123"
                st.success(f"🔐 Password for office code **{target_user}** successfully reset to `Nawada@123`.")

# Corporate Footer
st.markdown("""
    <div class="corporate-footer">
        Designed & Formulated for Optimization Protocols | District IT Infrastructure Cell, Nawada HQ © 2026
    </div>
""", unsafe_allow_html=True)