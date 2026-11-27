import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import requests
import base64
import io
import calendar
from PIL import Image
from supabase import create_client, Client

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

DEFAULT_50_STAFF_CSV = """office_name,user_code,officer_name,designation,epf_no,role
Hisua Block,BLK-HISUA-EMP01,Shashi Bhushan Kumar,Executive Assistant,101441508089,Block
Nardiganj Block,BLK-NARDIGANJ-EMP01,Pramod Kumar Rao,Executive Assistant,101441508528,Block
Kashichak Block,BLK-KASHICHAK-EMP01,Shankar Kumar,Executive Assistant,101441508544,Block
DM RTPS Cell (Nawada HQ),OFF-DM-RTPS-EMP01,Avinash Kumar Paswan,Executive Assistant,101441508091,Block
Warisaliganj Block,BLK-WARISALIGANJ-EMP01,Amar Kumar,Executive Assistant,101441508268,Block
Kowakole Block,BLK-KOWAKOLE-EMP01,Pavan Kumar,Executive Assistant,101441508193,Block
Rajauli Block,BLK-RAJAULI-EMP01,Pintu Kumar,Executive Assistant,101441508603,Block
Sadar Subdivision Office (Nawada),OFF-SADAR-SDO-EMP01,Amarjit Kumar,Executive Assistant,101441508782,Block
Narhat Block,BLK-NARHAT-EMP01,Krishna Murari Singh,Executive Assistant,101441508559,Block
Narhat Block,BLK-NARHAT-EMP02,Rakesh Kumar Nirala,Executive Assistant,101441506834,Block
Kashichak Block,BLK-KASHICHAK-EMP02,Santosh Kumar,Executive Assistant,101441506765,Block
Meskaur Block,BLK-MESKAUR-EMP01,Niraj Kumar,Executive Assistant,101441508769,Block
Nardiganj Block,BLK-NARDIGANJ-EMP02,Akhalesh Kumar,Executive Assistant,101441508332,Block
Govindpur Block,BLK-GOVINDPUR-EMP01,Pintu Kumar,Executive Assistant,101441508155,Block
Sirdala Block,BLK-SIRDALA-EMP01,Chandra Shekhar Prasad,Executive Assistant,101411019880,Block
Kashichak Block,BLK-KASHICHAK-EMP03,Dharmendra Pandit,Executive Assistant,101441508223,Block
Govindpur Block,BLK-GOVINDPUR-EMP02,Rajeev Ranjan Bharti,Executive Assistant,101441508516,Block
Roh Block,BLK-ROH-EMP01,Alok Ranjan Kishore,Executive Assistant,101441508350,Block
Roh Block,BLK-ROH-EMP02,Archana Kumari,Executive Assistant,101441506823,Block
Warisaliganj Block,BLK-WARISALIGANJ-EMP02,Rabindra Kumar,Executive Assistant,101441506875,Block
Kowakole Block,BLK-KOWAKOLE-EMP02,Dinesh Kumar,Executive Assistant,101441508366,Block
Nawada Sadar Block,BLK-NW-SADAR-EMP01,Gaurav Shekhar,Executive Assistant,101441506806,Block
Sirdala Block,BLK-SIRDALA-EMP02,Pintu Kumar,Executive Assistant,101441506852,Block
Warisaliganj Block,BLK-WARISALIGANJ-EMP03,Ranjeet Kumar,Executive Assistant,101441508537,Block
Pakribarawan Block,BLK-PAKRIBARAWAN-EMP01,Ved Prakash,Executive Assistant,101441508690,Block
Warisaliganj Block,BLK-WARISALIGANJ-EMP04,Purushotam Kumar,Executive Assistant,101441508456,Block
Rajauli Block,BLK-RAJAULI-EMP02,Dharmendra Kumar,Executive Assistant,101441508730,Block
Nawada Sadar Block,BLK-NW-SADAR-EMP02,Rekha kumari,Executive Assistant,101441508494,Block
Kowakole Block,BLK-KOWAKOLE-EMP03,Sadanand Kumar Sinha,Executive Assistant,101441508252,Block
Akbarpur Block,BLK-AKBARPUR-EMP01,Mithlesh Kumar,Executive Assistant,101441508418,Block
Meskaur Block,BLK-MESKAUR-EMP02,R Rigan Kumar,Executive Assistant,101441508309,Block
Narhat Block,BLK-NARHAT-EMP03,Suraj Kumar,Executive Assistant,101441508210,Block
Rajauli Subdivision Office,OFF-RAJAULI-SDO-EMP01,Gireesh Kumar,Executive Assistant,101441508441,Block
Pakribarawan Block,BLK-PAKRIBARAWAN-EMP02,Bablu Kumar,Executive Assistant,101441508707,Block
Kowakole Block,BLK-KOWAKOLE-EMP04,Prince Kumar,Executive Assistant,101441508642,Block
Meskaur Block,BLK-MESKAUR-EMP03,Shambhu Kumar,Executive Assistant,101441506796,Block
Akbarpur Block,BLK-AKBARPUR-EMP02,Sanjeet Kumar Prabhat,Executive Assistant,101441508563,Block
Hisua Block,BLK-HISUA-EMP02,Sangita Kumari,Executive Assistant,101441508657,Block
Akbarpur Block,BLK-AKBARPUR-EMP03,Upendra Kumar,Executive Assistant,101441508661,Block
Nardiganj Block,BLK-NARDIGANJ-EMP03,Sanjay Kumar,Executive Assistant,101441508688,Block
Sirdala Block,BLK-SIRDALA-EMP03,Gyanendra Kumar,Executive Assistant,101441506777,Block
Narhat Block,BLK-NARHAT-EMP04,Kanhai Kumar,Executive Assistant,101441508674,Block
Rajauli Block,BLK-RAJAULI-EMP03,Vikash Kumar,Executive Assistant,101441508619,Block
Narhat Block,BLK-NARHAT-EMP05,Vikash Kumar,Executive Assistant,101441508748,Block
Govindpur Block,BLK-GOVINDPUR-EMP03,Sumit Kumar,Executive Assistant,101441508247,Block
Nawada Sadar Block,BLK-NW-SADAR-EMP03,Urmila Kumari,Executive Assistant,101441508795,Block
Nawada Sadar Block,BLK-NW-SADAR-EMP04,Rajnish Kumar,Executive Assistant,101441508805,Block
Hisua Block,BLK-HISUA-EMP03,Pradeep Chaudhary,Executive Assistant,101441508473,Block
Pakribarawan Block,BLK-PAKRIBARAWAN-EMP03,Dhiraj Kumar,Executive Assistant,101546147809,Block
Govindpur Block,BLK-GOVINDPUR-EMP04,Nilmani Madhav Kumar,Executive Assistant,101792349704,Block"""

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Nawada District Monitoring System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. SUPABASE CLIENT INITIALIZATION
# ============================================================
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

# Inline SVG default avatar (no CDN dependency - works on ALL networks)
DEFAULT_AVATAR = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='50' fill='%23cbd5e1'/%3E%3Ccircle cx='50' cy='38' r='16' fill='%2364748b'/%3E%3Cellipse cx='50' cy='78' rx='30' ry='22' fill='%2364748b'/%3E%3C/svg%3E"

# ============================================================
# 3. COMPREHENSIVE CSS — NETWORK-UNIVERSAL (NO EXTERNAL FONTS)
# ============================================================
st.markdown("""
<style>
    /* ── IMPORT NOTHING: System Font Stack Only ── */
    /* Works on NIC, BSWAN, private LAN, any restricted network */

    /* ── BASE RESET & TYPOGRAPHY ── */
    /* Scope typography carefully so Streamlit icons, Glide Data Grid icons, and ligatures are NEVER corrupted */
    .stApp, p, label, input, textarea, select, button,
    .stMarkdown, .stText, h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', 'Noto Sans', 'Liberation Sans', Arial, sans-serif !important;
    }
    /* Explicitly protect icon fonts from being overridden by standard sans-serif fonts */
    [class*="material-symbols"],
    [class*="material-icons"],
    [data-testid="stIconMaterial"],
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    [data-baseweb="popover"] span:empty,
    [data-baseweb="popover"] [role="menuitem"] > span:first-child,
    [data-baseweb="popover"] li > span:first-child {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
        font-style: normal !important;
        font-weight: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-smoothing: antialiased !important;
    }
    .stApp {
        background-color: #f0f4f8;
        font-size: 15px !important;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0 !important;
    }

    /* ── SIDEBAR PROFILE CARD ── */
    .sidebar-profile-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
        border-radius: 16px !important;
        padding: 24px 18px !important;
        margin: 0 0 20px 0 !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
        text-align: center !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
    }
    .sidebar-profile-card * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .sidebar-profile-card h3 {
        margin: 12px 0 4px 0 !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.4) !important;
        letter-spacing: 0.3px !important;
    }
    .sidebar-profile-card .desig-text {
        color: #bfdbfe !important;
        -webkit-text-fill-color: #bfdbfe !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        margin: 0 0 3px 0 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }
    .sidebar-profile-card .office-text {
        color: #e0e7ff !important;
        -webkit-text-fill-color: #e0e7ff !important;
        font-size: 12.5px !important;
        font-weight: 500 !important;
        margin: 0 0 14px 0 !important;
    }
    .sidebar-profile-card .info-badge {
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 10px 12px !important;
        border-radius: 10px !important;
        font-size: 12px !important;
        display: flex !important;
        justify-content: space-between !important;
        gap: 8px !important;
    }
    .sidebar-profile-card .info-badge span,
    .sidebar-profile-card .info-badge b {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .sidebar-profile-card .info-badge b {
        color: #93c5fd !important;
        -webkit-text-fill-color: #93c5fd !important;
    }

    /* ── PROFILE AVATAR ── */
    .profile-avatar {
        width: 96px !important;
        height: 96px !important;
        border-radius: 50% !important;
        border: 3px solid #93c5fd !important;
        object-fit: cover !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.35) !important;
        display: block !important;
        margin: 0 auto 10px auto !important;
        background-color: #cbd5e1 !important;
    }

    /* ── HEADINGS ── */
    h1 { font-size: 28px !important; font-weight: 800 !important; color: #0f172a !important; }
    h2 { font-size: 24px !important; font-weight: 700 !important; color: #0f172a !important; }
    h3 { font-size: 20px !important; font-weight: 700 !important; color: #1e3a8a !important; }
    h4 { font-size: 17px !important; font-weight: 600 !important; color: #334155 !important; }
    p, span, label, .stMarkdown { font-size: 15px !important; color: #1e293b; }

    /* ── CORPORATE HEADER BANNER ── */
    .corporate-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%) !important;
        padding: 28px 32px !important;
        border-radius: 14px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 12px 24px rgba(15, 23, 42, 0.2) !important;
        text-align: center !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .corporate-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 60%);
        animation: headerPulse 6s ease-in-out infinite;
    }
    @keyframes headerPulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 1; }
    }
    .corporate-header * { position: relative; z-index: 1; }
    .corporate-header h1, .corporate-header h1 * {
        color: #ffffff !important;
        font-size: 26px !important;
        font-weight: 800 !important;
        letter-spacing: 0.8px !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
        margin: 0 0 6px 0 !important;
    }
    .corporate-header p, .corporate-header p * {
        color: #cbd5e1 !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }
    .corporate-header .header-badge {
        display: inline-block;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 12px !important;
        color: #93c5fd !important;
        margin-top: 10px;
        letter-spacing: 0.5px;
    }

    /* ── LOGIN PAGE ── */
    @keyframes loginGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .login-wrapper {
        min-height: 70vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    .login-box {
        max-width: 520px;
        width: 100%;
        margin: 0 auto;
        background: rgba(255, 255, 255, 0.97);
        backdrop-filter: blur(20px);
        padding: 44px 40px;
        border-radius: 20px;
        box-shadow: 0 25px 60px rgba(15, 23, 42, 0.12), 0 0 0 1px rgba(226, 232, 240, 0.8);
        border: 1px solid #e2e8f0;
    }
    .login-seal {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px auto;
        box-shadow: 0 8px 20px rgba(30, 58, 138, 0.3);
    }
    .login-seal span {
        font-size: 36px !important;
        color: #ffffff !important;
    }
    .login-title {
        text-align: center;
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        margin: 0 0 4px 0;
    }
    .login-subtitle {
        text-align: center;
        font-size: 14px !important;
        color: #64748b !important;
        margin: 0 0 28px 0;
    }
    .login-security-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 10px;
        padding: 10px 16px;
        margin-top: 16px;
        font-size: 13px !important;
        color: #166534 !important;
    }

    /* ── TABS STYLING ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: #ffffff !important;
        padding: 8px 10px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
        flex-wrap: wrap !important;
    }
    .stTabs [data-baseweb="tab"],
    .stTabs button[role="tab"] {
        font-size: 14.5px !important;
        font-weight: 600 !important;
        padding: 10px 18px !important;
        border-radius: 8px !important;
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        color: #334155 !important;
        white-space: nowrap !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"] *,
    .stTabs button[role="tab"] * {
        color: #334155 !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab"]:hover,
    .stTabs button[role="tab"]:hover {
        background-color: #e2e8f0 !important;
        border-color: #94a3b8 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"],
    .stTabs button[role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important;
        border: 1px solid #1e3a8a !important;
        box-shadow: 0 4px 10px rgba(30, 58, 138, 0.3) !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] *,
    .stTabs button[role="tab"][aria-selected="true"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
    }
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

    /* ── BUTTONS ── */
    .stButton > button {
        font-size: 15px !important;
        font-weight: 700 !important;
        padding: 10px 22px !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        transition: all 0.2s ease !important;
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        border: 1px solid #cbd5e1 !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 14px rgba(30, 58, 138, 0.2);
        background-color: #1e3a8a !important;
        color: #ffffff !important;
    }
    .stButton > button:hover * { color: #ffffff !important; }

    /* ── SIDEBAR BUTTONS ── */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.08) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] .stButton > button * {
        color: #e2e8f0 !important;
        -webkit-text-fill-color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #3b82f6 !important;
        color: #ffffff !important;
        border-color: #3b82f6 !important;
    }

    /* ════════════════════════════════════════════════════════
       ── CRITICAL FIX: ALL DROPDOWNS / SELECT BOXES ──
       Works on NIC, BSWAN, any network/browser
       ════════════════════════════════════════════════════════ */

    /* Input fields */
    .stTextInput input,
    .stTextArea textarea,
    div[data-baseweb="input"] input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        font-size: 15px !important;
        border-radius: 10px !important;
        border: 1.5px solid #cbd5e1 !important;
        padding: 10px 14px !important;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }

    /* Select box control */
    .stSelectbox div[data-baseweb="select"],
    .stMultiSelect div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 1.5px solid #cbd5e1 !important;
        min-height: 42px !important;
    }
    .stSelectbox div[data-baseweb="select"]:focus-within,
    .stMultiSelect div[data-baseweb="select"]:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }

    /* Selected text inside select box - MUST BE VISIBLE */
    .stSelectbox div[data-baseweb="select"] *,
    .stSelectbox span, .stSelectbox div,
    .stMultiSelect div[data-baseweb="select"] *,
    .stMultiSelect span, .stMultiSelect div {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        background-color: transparent !important;
    }

    /* Dropdown arrow icon */
    .stSelectbox svg, .stMultiSelect svg {
        fill: #475569 !important;
        color: #475569 !important;
    }

    /* ── DROPDOWN POPUP MENU (CRITICAL Z-INDEX + VISIBILITY) ── */
    div[data-baseweb="popover"] {
        z-index: 999999 !important;
    }
    .stSelectbox div[data-baseweb="menu"],
    .stMultiSelect div[data-baseweb="menu"],
    div[data-baseweb="select"] ul[role="listbox"] {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 12px !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18) !important;
        z-index: 999999 !important;
        max-height: 350px !important;
        overflow-y: auto !important;
        padding: 4px !important;
    }

    /* Each option in standard selectbox dropdowns */
    div[data-baseweb="select"] li[role="option"],
    div[data-baseweb="select"] div[role="option"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        padding: 11px 16px !important;
        border-radius: 8px !important;
        margin: 2px 0 !important;
        cursor: pointer !important;
    }
    div[data-baseweb="select"] li[role="option"] *,
    div[data-baseweb="select"] div[role="option"] * {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        font-size: 15px !important;
    }

    /* Hovered option in selectboxes */
    div[data-baseweb="select"] li[role="option"]:hover,
    div[data-baseweb="select"] div[role="option"]:hover {
        background-color: #eff6ff !important;
        color: #1e3a8a !important;
        -webkit-text-fill-color: #1e3a8a !important;
    }
    div[data-baseweb="select"] li[role="option"]:hover *,
    div[data-baseweb="select"] div[role="option"]:hover * {
        color: #1e3a8a !important;
        -webkit-text-fill-color: #1e3a8a !important;
    }

    /* Selected/highlighted option */
    div[data-baseweb="select"] li[role="option"][aria-selected="true"],
    div[data-baseweb="select"] div[role="option"][aria-selected="true"] {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    div[data-baseweb="select"] li[role="option"][aria-selected="true"] *,
    div[data-baseweb="select"] div[role="option"][aria-selected="true"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* Sidebar dropdown overrides */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(255,255,255,0.1) !important;
        border-color: rgba(255,255,255,0.2) !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {
        color: #e2e8f0 !important;
        -webkit-text-fill-color: #e2e8f0 !important;
    }

    /* Number input */
    .stNumberInput input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        font-size: 15px !important;
        border-radius: 10px !important;
        border: 1.5px solid #cbd5e1 !important;
    }

    /* ── LABELS for all inputs ── */
    .stSelectbox label, .stMultiSelect label,
    .stTextInput label, .stTextArea label,
    .stNumberInput label, .stDateInput label,
    .stFileUploader label {
        color: #334155 !important;
        -webkit-text-fill-color: #334155 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }

    /* ── DATA TABLE / DATAFRAME ── */
    /* Keep minimal styling — do NOT override glide-data-grid internals */
    .stDataFrame, [data-testid="stDataFrame"] {
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
    }

    /* ── METRIC DASHBOARD CARDS ── */
    .metric-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 22px 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
        border-left: 5px solid #1e3a8a;
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    .metric-card.pending { border-left-color: #ef4444; }
    .metric-card.progress { border-left-color: #f59e0b; }
    .metric-card.disposed { border-left-color: #10b981; }
    .metric-card.rate { border-left-color: #6366f1; }
    .metric-icon {
        font-size: 28px !important;
        margin-bottom: 6px;
        display: block;
    }
    .metric-title {
        font-size: 12px !important;
        font-weight: 700 !important;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin: 0;
    }
    .metric-value {
        font-size: 30px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        margin: 4px 0 0 0;
        line-height: 1.1;
    }

    /* ── DOSSIER / CASE CARDS ── */
    .dossier-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 24px;
        margin-top: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }
    .dossier-header {
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 14px;
        margin-bottom: 16px;
    }
    .dossier-label {
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #475569 !important;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 6px;
    }
    .dossier-content-desc {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 14px 16px;
        font-size: 14.5px !important;
        line-height: 1.65;
        color: #1e293b !important;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .dossier-content-atr {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 4px solid #16a34a;
        border-radius: 8px;
        padding: 14px 16px;
        font-size: 14.5px !important;
        line-height: 1.65;
        color: #14532d !important;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    /* ── STATUS BADGES ── */
    .badge-pending {
        background-color: #fee2e2; color: #991b1b;
        padding: 5px 14px; border-radius: 20px;
        font-weight: 700; font-size: 13px;
    }
    .badge-progress {
        background-color: #fef3c7; color: #92400e;
        padding: 5px 14px; border-radius: 20px;
        font-weight: 700; font-size: 13px;
    }
    .badge-disposed {
        background-color: #dcfce7; color: #166534;
        padding: 5px 14px; border-radius: 20px;
        font-weight: 700; font-size: 13px;
    }

    /* ── EXPORT TOOLBAR ── */
    .export-toolbar {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px 20px;
        margin: 14px 0;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }

    /* ── SECTION DIVIDER ── */
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #cbd5e1, transparent);
        margin: 28px 0;
    }

    /* ── DOWNLOAD BUTTON STYLING ── */
    .stDownloadButton > button {
        font-size: 14px !important;
        font-weight: 700 !important;
        padding: 9px 20px !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #1e3a8a, #2563eb) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 3px 10px rgba(30, 58, 138, 0.25) !important;
    }
    .stDownloadButton > button:hover {
        box-shadow: 0 6px 16px rgba(30, 58, 138, 0.35) !important;
        transform: translateY(-1px);
    }
    .stDownloadButton > button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* ── ANALYTICS SECTION CARDS ── */
    .analytics-section {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .analytics-section-title {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #1e3a8a !important;
        margin-bottom: 14px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
    }

    /* ── LEADERBOARD TABLE ── */
    .leaderboard-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 16px;
        border-radius: 8px;
        margin-bottom: 4px;
        font-size: 14px !important;
    }
    .leaderboard-row:nth-child(odd) { background: #f8fafc; }
    .leaderboard-row:nth-child(even) { background: #ffffff; }
    .leaderboard-rank {
        font-weight: 800;
        color: #1e3a8a;
        width: 36px;
        text-align: center;
    }
    .leaderboard-name {
        flex: 1;
        font-weight: 600;
        color: #334155;
        padding: 0 12px;
    }
    .leaderboard-value {
        font-weight: 800;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 13px !important;
    }

    /* ── FOOTER ── */
    .corporate-footer {
        text-align: center;
        padding: 24px;
        margin-top: 50px;
        font-size: 13px !important;
        color: #64748b !important;
        border-top: 1px solid #e2e8f0;
    }

    /* ── FIX: PREVENT CONTAINER CLIPPING DROPDOWNS ── */
    .main .block-container { overflow: visible !important; }
    [data-testid="stForm"] { overflow: visible !important; }
    .element-container { overflow: visible !important; }

    /* ════════════════════════════════════════════════════════════
       ── FIX: DATAFRAME COLUMN HEADER THREE-DOT MENU ──
       Explicit styling for the Glide Data Grid column context menu
       ════════════════════════════════════════════════════════════ */

    /* Ensure popover container is top-level and opaque */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div {
        z-index: 9999999 !important;
        background-color: transparent !important;
    }

    /* Style the context menu popup specifically */
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] [role="menu"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2), 0 8px 10px -6px rgba(0, 0, 0, 0.1) !important;
        padding: 6px !important;
        min-width: 220px !important;
        opacity: 1 !important;
    }

    div[data-baseweb="popover"] [role="menuitem"],
    div[data-baseweb="popover"] li {
        background-color: #ffffff !important;
        color: #1e293b !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 8px 14px !important;
        border-radius: 6px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 14px !important;
        white-space: nowrap !important;
        cursor: pointer !important;
    }

    div[data-baseweb="popover"] [role="menuitem"]:hover,
    div[data-baseweb="popover"] li:hover {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }

    /* The icon element inside the menu item */
    div[data-baseweb="popover"] [role="menuitem"] > span:first-child,
    div[data-baseweb="popover"] li > span:first-child {
        width: 24px !important;
        min-width: 24px !important;
        max-width: 24px !important;
        height: 24px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 20px !important;
        line-height: 1 !important;
        color: #475569 !important;
        overflow: hidden !important;
        flex-shrink: 0 !important;
    }

    /* The text label element inside the menu item */
    div[data-baseweb="popover"] [role="menuitem"] > span:last-child,
    div[data-baseweb="popover"] li > span:last-child {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #1e293b !important;
        flex-grow: 1 !important;
    }

    /* ── FIX: EXPANDER TEXT ── */
    .streamlit-expanderHeader p {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #1e3a8a !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 4. USER REGISTRY (STATIC AUTHENTICATION)
# ============================================================
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

# ============================================================
# 5. SESSION STATE PERSISTENCE
# ============================================================
for key, default in [
    ("password_db", {uid: "Nawada@123" for uid in USER_REGISTRY}),
    ("authenticated", False),
    ("current_user", None),
    ("otp_sent", False),
    ("temp_uid", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

if not st.session_state["authenticated"]:
    persisted_user = st.query_params.get("session_auth", None)
    if persisted_user and persisted_user in USER_REGISTRY:
        st.session_state["authenticated"] = True
        st.session_state["current_user"] = persisted_user


# ============================================================
# 6. HELPER FUNCTIONS
# ============================================================

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

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_image_as_base64(url):
    """Downloads image from URL server-side and returns base64 data URI.
    This bypasses NIC/BSWAN browser-level firewall blocks because the
    Streamlit server (on Streamlit Cloud) fetches the image, not the browser.
    """
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and len(resp.content) > 100:
            content_type = resp.headers.get("content-type", "image/jpeg")
            if "image" not in content_type:
                content_type = "image/jpeg"
            b64 = base64.b64encode(resp.content).decode("utf-8")
            return f"data:{content_type};base64,{b64}"
    except Exception:
        pass
    return None

def get_profile_photo_url(raw_url):
    """Returns a base64 data URI for profile photo (works on NIC/BSWAN).
    The Streamlit server fetches the image and embeds it inline,
    so the user's browser never contacts Supabase storage directly.
    """
    if not raw_url or not isinstance(raw_url, str) or not raw_url.strip().startswith("http"):
        return DEFAULT_AVATAR
    url = raw_url.strip()

    # Step 1: Try to get a signed URL from Supabase storage
    fetch_url = url
    if supabase and "supabase" in url.lower():
        try:
            filename = url.split("/")[-1].split("?")[0]
            res = supabase.storage.from_("profile-photos").create_signed_url(filename, 7200)
            if isinstance(res, dict):
                signed = res.get('signedUrl') or res.get('signedURL')
                if signed:
                    fetch_url = signed
        except Exception:
            pass

    # Step 2: Download server-side and convert to base64 data URI
    # This is the KEY FIX — browser never contacts Supabase directly
    data_uri = _fetch_image_as_base64(fetch_url)
    if data_uri:
        return data_uri

    # Step 3: If server-side fetch also fails, try original URL as fallback
    if fetch_url != url:
        data_uri = _fetch_image_as_base64(url)
        if data_uri:
            return data_uri

    # Final fallback: inline SVG avatar
    return DEFAULT_AVATAR

def upload_attendance_record(payload):
    """Upserts monthly attendance record for an employee."""
    if supabase is None:
        return False
    try:
        supabase.table("monthly_attendance").upsert(
            payload, on_conflict="month,year,office_code,employee_name"
        ).execute()
        return True
    except Exception as e:
        st.error(f"Failed to submit attendance: {e}")
        return False

def add_executive_profile(payload):
    """Inserts or updates an employee/executive profile in user_profiles."""
    if supabase is None:
        return False
    try:
        res = supabase.table("user_profiles").upsert(
            payload, on_conflict="user_code"
        ).execute()
        if res.data:
            return True
        return False
    except Exception as e:
        err_msg = str(e)
        if "row-level security" in err_msg.lower() or "403" in err_msg or "unauthorized" in err_msg.lower():
            st.error(
                "❌ **Supabase Table Permission Error (RLS):**\n\n"
                "The `user_profiles` table has Row-Level Security active without an INSERT/UPDATE policy for public/anon.\n\n"
                "👉 In Supabase Dashboard -> **Database** -> **Tables** -> `user_profiles` -> **RLS Policies** -> Add Policy for `INSERT` and `UPDATE`."
            )
        else:
            st.error(f"Failed to add/update executive: {e}")
        return False

def bulk_upsert_employees(records):
    """Upserts multiple employee records into user_profiles table in batches."""
    if supabase is None or not records:
        return 0, "Database connection not available or no records provided."
    total_upserted = 0
    batch_size = 50
    try:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            res = supabase.table("user_profiles").upsert(batch, on_conflict="user_code").execute()
            if res.data:
                total_upserted += len(res.data)
            else:
                total_upserted += len(batch)
        return total_upserted, None
    except Exception as e:
        err_msg = str(e)
        if "row-level security" in err_msg.lower() or "403" in err_msg or "unauthorized" in err_msg.lower():
            return total_upserted, "Supabase Table Permission Error (RLS): The user_profiles table requires an INSERT/UPDATE policy for public/anon in Supabase Dashboard."
        return total_upserted, err_msg

def delete_employee_profile(user_code):
    """Deletes an employee record from user_profiles."""
    if supabase is None or not user_code:
        return False, "Database not available"
    try:
        res = supabase.table("user_profiles").delete().eq("user_code", user_code).execute()
        return True, None
    except Exception as e:
        return False, str(e)

def generate_sample_employee_csv():
    """Generates sample CSV data containing standard columns and example rows for all offices."""
    sample_rows = [
        {"office_name": "Nawada Sadar Block", "user_code": "BLK-NW-SADAR-EMP01", "officer_name": "Rajnish Kumar", "designation": "Executive Assistant", "epf_no": "101441508275", "role": "Block"},
        {"office_name": "Meskaur Block", "user_code": "BLK-MESKAUR-EMP01", "officer_name": "Ramesh Kumar", "designation": "Executive Assistant", "epf_no": "101441508206", "role": "Block"},
        {"office_name": "Hisua Block", "user_code": "BLK-HISUA-EMP01", "officer_name": "Amit Sharma", "designation": "IT Assistant", "epf_no": "101441508207", "role": "Block"},
        {"office_name": "Rajauli Block", "user_code": "BLK-RAJAULI-EMP01", "officer_name": "Sunil Kumar", "designation": "Panchayat Secretary", "epf_no": "101441508208", "role": "Block"},
        {"office_name": "Pakribarawan Block", "user_code": "BLK-PAKRIBARAWAN-EMP01", "officer_name": "Manoj Verma", "designation": "Executive Assistant", "epf_no": "101441508209", "role": "Block"},
        {"office_name": "Akbarpur Block", "user_code": "BLK-AKBARPUR-EMP01", "officer_name": "Prakash Jha", "designation": "Executive Assistant", "epf_no": "101441508210", "role": "Block"},
        {"office_name": "Kashichak Block", "user_code": "BLK-KASHICHAK-EMP01", "officer_name": "Vikas Singh", "designation": "IT Assistant", "epf_no": "101441508211", "role": "Block"},
        {"office_name": "Warisaliganj Block", "user_code": "BLK-WARISALIGANJ-EMP01", "officer_name": "Sanjay Kumar", "designation": "Executive Assistant", "epf_no": "101441508212", "role": "Block"},
        {"office_name": "Kowakole Block", "user_code": "BLK-KOWAKOLE-EMP01", "officer_name": "Deepak Paswan", "designation": "Executive Assistant", "epf_no": "101441508213", "role": "Block"},
        {"office_name": "Roh Block", "user_code": "BLK-ROH-EMP01", "officer_name": "Anil Prasad", "designation": "Executive Assistant", "epf_no": "101441508214", "role": "Block"},
        {"office_name": "Narhat Block", "user_code": "BLK-NARHAT-EMP01", "officer_name": "Mukesh Yadav", "designation": "Executive Assistant", "epf_no": "101441508215", "role": "Block"},
        {"office_name": "Sirdala Block", "user_code": "BLK-SIRDALA-EMP01", "officer_name": "Santosh Kumar", "designation": "IT Assistant", "epf_no": "101441508216", "role": "Block"},
        {"office_name": "Govindpur Block", "user_code": "BLK-GOVINDPUR-EMP01", "officer_name": "Pooja Kumari", "designation": "Executive Assistant", "epf_no": "101441508217", "role": "Block"},
        {"office_name": "Nardiganj Block", "user_code": "BLK-NARDIGANJ-EMP01", "officer_name": "Gautam Kumar", "designation": "Executive Assistant", "epf_no": "101441508218", "role": "Block"},
        {"office_name": "Sadar Subdivision Office (Nawada)", "user_code": "OFF-SADAR-SDO-EMP01", "officer_name": "Arun Mishra", "designation": "Executive Assistant", "epf_no": "101441508219", "role": "Block"},
        {"office_name": "Rajauli Subdivision Office", "user_code": "OFF-RAJAULI-SDO-EMP01", "officer_name": "Kishore Lal", "designation": "Executive Assistant", "epf_no": "101441508220", "role": "Block"},
        {"office_name": "DM RTPS Cell (Nawada HQ)", "user_code": "OFF-DM-RTPS-EMP01", "officer_name": "Neeraj Pandey", "designation": "Executive Assistant", "epf_no": "101441508221", "role": "Block"},
        {"office_name": "SP Office (Nawada HQ)", "user_code": "OFF-SP-HQ-EMP01", "officer_name": "Ravi Shankar", "designation": "IT Assistant", "epf_no": "101441508222", "role": "Block"}
    ]
    df = pd.DataFrame(sample_rows)
    return df.to_csv(index=False).encode('utf-8')

def get_office_employees(office_code, office_display_name):
    """Fetches all employees belonging to an office with strict Block vs Subdivision isolation."""
    if supabase is None:
        return pd.DataFrame()
    try:
        # Fetch all user_profiles
        res = supabase.table("user_profiles").select("*").execute()
        if not res.data:
            return pd.DataFrame()
        df = pd.DataFrame(res.data)

        c_code = str(office_code).strip().upper()
        c_name = str(office_display_name).strip().lower()

        # Office tier classification to strictly prevent Block vs Subdivision cross-contamination
        is_subdiv = ("subdivision" in c_name or "sdo" in c_code.lower())
        is_block = ("block" in c_name or "blk" in c_code.lower())
        is_rtps = ("rtps" in c_code.lower() or "rtps" in c_name)
        is_sp = ("sp" in c_code.lower() or "sp office" in c_name)

        def is_match(row):
            r_code = str(row.get("user_code", "")).strip().upper()
            r_name = str(row.get("office_name", "")).strip().lower()

            # Rule 1: Exact user_code or exact prefix with separator
            if r_code == c_code or r_code.startswith(f"{c_code}-") or r_code.startswith(f"{c_code}_") or r_code.startswith(f"{c_code} "):
                return True

            # Rule 2: Tier guard - Subdivision must NEVER match Block and vice versa
            r_is_subdiv = ("subdivision" in r_name or "sdo" in r_code.lower())
            r_is_block = ("block" in r_name or "blk" in r_code.lower())
            r_is_rtps = ("rtps" in r_code.lower() or "rtps" in r_name)
            r_is_sp = ("sp" in r_code.lower() or "sp office" in r_name)

            if is_subdiv != r_is_subdiv:
                return False
            if is_block != r_is_block:
                return False
            if is_rtps != r_is_rtps:
                return False
            if is_sp != r_is_sp:
                return False

            # Rule 3: Exact office name match
            if r_name == c_name:
                return True

            # Rule 4: Distinctive office name keyword matching
            clean_curr = c_name.replace("block", "").replace("subdivision", "").replace("office", "").replace("(", "").replace(")", "").strip()
            clean_row = r_name.replace("block", "").replace("subdivision", "").replace("office", "").replace("(", "").replace(")", "").strip()
            if clean_curr and (clean_curr == clean_row or clean_curr in clean_row or clean_row in clean_curr):
                return True

            return False

        matched = df[df.apply(is_match, axis=1)]
        matched = matched.drop_duplicates(subset=["user_code"])

        # Deduplicate by non-empty EPF number within office to prevent duplicate roster rows
        if "epf_no" in matched.columns:
            has_epf = matched["epf_no"].astype(str).str.strip().ne("") & matched["epf_no"].astype(str).ne("nan") & matched["epf_no"].astype(str).ne("None")
            epf_dedup = matched[has_epf].drop_duplicates(subset=["epf_no"])
            no_epf = matched[~has_epf]
            matched = pd.concat([epf_dedup, no_epf]).sort_index()

        return matched
    except Exception as e:
        st.error(f"Error fetching office staff: {e}")
        return pd.DataFrame()

def load_monthly_attendance(month, year):
    """Fetches attendance records for all offices for a specific month/year."""
    if supabase is None:
        return pd.DataFrame()
    try:
        res = supabase.table("monthly_attendance").select("*").eq("month", month).eq("year", year).execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching attendance data: {e}")
        return pd.DataFrame()

def process_and_compress_file(uploaded_file):
    """Auto-compress images to crisp A4 print-ready resolution."""
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

def get_secure_file_url(stored_val, bucket_name="complaint-documents"):
    """Generates a secure signed URL for file access."""
    if not stored_val or not isinstance(stored_val, str):
        return ""
    val = stored_val.strip()
    file_path = val
    if "/" in val:
        file_path = val.split("/")[-1].split("?")[0]
    try:
        if supabase and file_path:
            res = supabase.storage.from_(bucket_name).create_signed_url(file_path, 7200)
            if isinstance(res, dict):
                return res.get('signedUrl') or res.get('signedURL') or val
    except Exception:
        pass
    if val.startswith("http://"):
        return val.replace("http://", "https://", 1)
    return val

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_storage_file_bytes(file_url_or_path, bucket_name="complaint-documents"):
    """Downloads file from Supabase storage server-side.
    Returns (file_bytes, filename, mime_type).
    This bypasses NIC/BSWAN browser firewalls and ERR_QUIC_PROTOCOL_ERROR
    because the Streamlit server downloads the file over standard TCP/HTTPS.
    """
    if not file_url_or_path or not str(file_url_or_path).strip():
        return None, "", "application/octet-stream"
    
    val = str(file_url_or_path).strip()
    file_name = val.split("/")[-1].split("?")[0]
    
    ext = file_name.split(".")[-1].lower() if "." in file_name else ""
    mime_map = {
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "csv": "text/csv",
        "txt": "text/plain"
    }
    mime_type = mime_map.get(ext, "application/octet-stream")
    
    # Method 1: Direct download via Supabase storage client
    if supabase and file_name:
        try:
            raw_data = supabase.storage.from_(bucket_name).download(file_name)
            if raw_data and len(raw_data) > 0:
                return raw_data, file_name, mime_type
        except Exception:
            pass

    # Method 2: Fetch via signed URL server-side (TCP HTTPS)
    try:
        signed_url = get_secure_file_url(val, bucket_name=bucket_name)
        if signed_url and signed_url.startswith("http"):
            resp = requests.get(signed_url, timeout=20)
            if resp.status_code == 200 and len(resp.content) > 0:
                return resp.content, file_name, mime_type
    except Exception:
        pass

    # Method 3: Direct HTTP fetch if raw URL
    if val.startswith("http"):
        try:
            resp = requests.get(val, timeout=20)
            if resp.status_code == 200 and len(resp.content) > 0:
                return resp.content, file_name, mime_type
        except Exception:
            pass

    return None, file_name, mime_type

_ACTIVE_RUN_KEYS = set()

def render_file_action_button(file_url, btn_label="📄 View / Download", key_id="1", bucket_name="complaint-documents"):
    """Renders a direct in-app download button that bypasses
    NIC/BSWAN firewalls, Microsoft Edge iframe blocks, and ERR_QUIC_PROTOCOL_ERROR.
    Guarantees unique widget keys across all tabs.
    """
    if not file_url or not str(file_url).strip() or str(file_url).strip() == "None":
        st.caption("📎 No file attached.")
        return

    val = str(file_url).strip()
    clean_k = str(key_id).replace(" ", "_").replace("-", "_").replace("/", "_").replace(":", "_")
    base_k = f"dl_btn_{clean_k}"
    final_k = base_k
    k_counter = 1
    while final_k in _ACTIVE_RUN_KEYS:
        final_k = f"{base_k}_{k_counter}"
        k_counter += 1
    _ACTIVE_RUN_KEYS.add(final_k)

    file_bytes, file_name, mime_type = fetch_storage_file_bytes(val, bucket_name=bucket_name)
    clean_label = btn_label.replace("📄", "").replace("View", "").replace("Download", "").strip() or "Document"

    if file_bytes and len(file_bytes) > 0:
        ext = file_name.split('.')[-1] if '.' in file_name else 'pdf'
        st.download_button(
            label=f"📥 Download {clean_label} ({file_name})",
            data=file_bytes,
            file_name=file_name,
            mime=mime_type or "application/octet-stream",
            key=final_k,
            use_container_width=True
        )
        
        # In-app image preview (images are universally supported across Edge, Chrome, Safari without security blocks)
        if mime_type.startswith("image/"):
            with st.expander(f"👁️ View / Preview {clean_label} (Image)", expanded=True):
                st.image(file_bytes, use_container_width=True)
    else:
        st.caption(f"📎 Attached file reference: `{file_name or 'Document'}` (Not previewable)")

def upload_file_to_supabase(uploaded_file, file_prefix="complaint"):
    """Uploads file to Supabase Storage with clean naming.
    Ensures bucket exists and handles storage errors gracefully.
    """
    if uploaded_file is None or supabase is None:
        return ""
    try:
        file_bytes, file_type, orig_kb, final_kb = process_and_compress_file(uploaded_file)
        ext = uploaded_file.name.split(".")[-1] if "." in uploaded_file.name else "pdf"
        file_name = f"{file_prefix}_{int(datetime.now().timestamp())}.{ext}"
        bucket_name = "complaint-documents"
        
        # Perform upload
        res = supabase.storage.from_(bucket_name).upload(
            file_name, file_bytes,
            file_options={"content-type": file_type, "x-upsert": "true"}
        )
        return supabase.storage.from_(bucket_name).get_public_url(file_name)
    except Exception as e:
        err_msg = str(e)
        if "row-level security" in err_msg.lower() or "403" in err_msg or "unauthorized" in err_msg.lower():
            st.error(
                "❌ **Supabase Storage Permission Error (RLS Violation):**\n\n"
                "The storage bucket `'complaint-documents'` has Row-Level Security (RLS) active without an **INSERT** policy for public/anon users.\n\n"
                "👉 **How to fix in 1 minute in Supabase Dashboard:**\n"
                "1. Go to your Supabase project -> **Storage** -> **Policies** (or click on `'complaint-documents'` bucket configuration).\n"
                "2. Click **New Policy** -> Choose **For full customization** (or select template *'Enable read/write access to all users'*).\n"
                "3. Set Allowed Operations to: **SELECT, INSERT, UPDATE**.\n"
                "4. Set Target Roles to: `anon`, `authenticated` (or `public`).\n"
                "5. Save policy. Uploads will immediately work without error!"
            )
        else:
            st.error(f"Error uploading file to storage: {e}")
        return ""

# ============================================================
# 7. PDF REPORT GENERATION (fpdf2)
# ============================================================

def generate_grievance_pdf(df, title="Grievance Registry Report", subtitle=""):
    """Generate a professional PDF report from grievance dataframe."""
    if not FPDF_AVAILABLE:
        return None

    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 12, 'GOVERNMENT OF BIHAR', 0, 1, 'C')
    pdf.set_font('Helvetica', 'B', 15)
    pdf.cell(0, 10, 'DISTRICT ADMINISTRATION, NAWADA', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 8, title, 0, 1, 'C')
    if subtitle:
        pdf.cell(0, 6, subtitle, 0, 1, 'C')
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, f'Generated: {datetime.now().strftime("%d-%b-%Y %I:%M %p")}', 0, 1, 'C')
    pdf.ln(3)

    # Horizontal rule
    pdf.set_draw_color(30, 58, 138)
    pdf.set_line_width(0.6)
    pdf.line(10, pdf.get_y(), 287, pdf.get_y())
    pdf.ln(5)

    # Summary statistics
    status_col = 'Normalized_Status' if 'Normalized_Status' in df.columns else 'Status'
    if status_col in df.columns:
        total = len(df)
        pending = len(df[df[status_col] == 'Pending'])
        progress = len(df[df[status_col] == 'In Progress'])
        disposed = len(df[df[status_col] == 'Disposed'])
        rate = round((disposed / total) * 100, 1) if total > 0 else 0

        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_fill_color(248, 250, 252)
        pdf.cell(0, 8,
            f'   Total: {total}   |   Pending: {pending}   |   In Progress: {progress}   |   Disposed: {disposed}   |   Disposal Rate: {rate}%',
            1, 1, 'L', True)
        pdf.ln(4)

    # Prepare columns
    export_cols = ['Date', 'Jurisdiction', 'Complaint ID', 'Reference No', 'Category', 'Status', 'Description', 'District Action/Opinion']
    # Map Normalized_Status to Status for display
    df_export = df.copy()
    if 'Normalized_Status' in df_export.columns:
        df_export['Status'] = df_export['Normalized_Status']
    available = [c for c in export_cols if c in df_export.columns]

    widths = {'Date': 22, 'Jurisdiction': 42, 'Complaint ID': 28, 'Reference No': 25,
              'Category': 28, 'Status': 22, 'Description': 58, 'District Action/Opinion': 52}

    def print_table_header():
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_fill_color(30, 58, 138)
        pdf.set_text_color(255, 255, 255)
        for col in available:
            w = widths.get(col, 30)
            pdf.cell(w, 7, col, 1, 0, 'C', True)
        pdf.ln()
        pdf.set_text_color(15, 23, 42)

    print_table_header()

    # Data rows
    pdf.set_font('Helvetica', '', 7)
    fill = False
    for _, row in df_export.iterrows():
        if pdf.get_y() > 180:
            pdf.add_page()
            print_table_header()
            pdf.set_font('Helvetica', '', 7)

        if fill:
            pdf.set_fill_color(248, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)

        for col in available:
            w = widths.get(col, 30)
            val = str(row.get(col, ''))
            max_chars = max(int(w * 0.45), 8)
            if len(val) > max_chars:
                val = val[:max_chars - 2] + '..'
            pdf.cell(w, 6, val.encode('latin-1', 'replace').decode('latin-1'), 1, 0, 'L', True)
        pdf.ln()
        fill = not fill

    # Footer
    pdf.ln(8)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, 'System-generated report | District Grievance Monitoring Portal | Nawada HQ', 0, 1, 'C')

    return bytes(pdf.output())


def generate_attendance_pdf(df, month, year):
    """Generate a professional PDF for attendance/payroll data."""
    if not FPDF_AVAILABLE:
        return None

    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 12, 'GOVERNMENT OF BIHAR', 0, 1, 'C')
    pdf.set_font('Helvetica', 'B', 15)
    pdf.cell(0, 10, 'DISTRICT ADMINISTRATION, NAWADA', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 8, f'Monthly Attendance & Payroll Report - {month_names[month]} {year}', 0, 1, 'C')
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, f'Generated: {datetime.now().strftime("%d-%b-%Y %I:%M %p")}', 0, 1, 'C')
    pdf.ln(3)
    pdf.set_draw_color(30, 58, 138)
    pdf.set_line_width(0.6)
    pdf.line(10, pdf.get_y(), 287, pdf.get_y())
    pdf.ln(5)

    cols = ['office_name', 'employee_name', 'designation', 'attendance_status',
            'total_working_days', 'days_present', 'days_absent', 'remarks']
    headers = ['Office', 'Employee', 'Designation', 'Status', 'Working', 'Present', 'Absent', 'Remarks']
    col_widths = [52, 40, 32, 25, 22, 22, 22, 62]

    def print_att_header():
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_fill_color(30, 58, 138)
        pdf.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 7, h, 1, 0, 'C', True)
        pdf.ln()
        pdf.set_text_color(15, 23, 42)

    print_att_header()

    pdf.set_font('Helvetica', '', 7)
    fill = False
    for _, row in df.iterrows():
        if pdf.get_y() > 180:
            pdf.add_page()
            print_att_header()
            pdf.set_font('Helvetica', '', 7)

        if fill:
            pdf.set_fill_color(248, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)

        for i, col in enumerate(cols):
            val = str(row.get(col, ''))
            max_chars = max(int(col_widths[i] * 0.45), 8)
            if len(val) > max_chars:
                val = val[:max_chars - 2] + '..'
            pdf.cell(col_widths[i], 6, val.encode('latin-1', 'replace').decode('latin-1'), 1, 0, 'L', True)
        pdf.ln()
        fill = not fill

    pdf.ln(8)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, 'System-generated report | District Attendance & Payroll Portal | Nawada HQ', 0, 1, 'C')

    return bytes(pdf.output())

# ============================================================
# 8. DATA LOADING FROM SUPABASE
# ============================================================

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
            'date': 'Date', 'jurisdiction': 'Jurisdiction', 'complaint_id': 'Complaint ID',
            'reference_no': 'Reference No', 'category': 'Category', 'status': 'Status',
            'description': 'Description', 'district_action_opinion': 'District Action/Opinion',
            'resolution_date': 'Resolution Date', 'uploaded_file_url': 'Uploaded File URL',
            'submitted_by_code': 'Submitted By Code', 'atr_response_file_url': 'ATR Response File URL'
        }
        df = df.rename(columns=col_mapping)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        df = df.fillna("")

        for col in ['Date', 'Jurisdiction', 'Complaint ID', 'Reference No', 'Category',
                     'Status', 'Description', 'District Action/Opinion', 'Resolution Date',
                     'Uploaded File URL', 'Submitted By Code', 'ATR Response File URL']:
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


# ============================================================
# 9. HEADER BANNER
# ============================================================
st.markdown("""
<div class="corporate-header">
    <h1>🏛️ GOVERNMENT OF BIHAR — DISTRICT ADMINISTRATION NAWADA</h1>
    <p>Integrated Grievance Redressal &amp; Operational IT Monitoring Infrastructure</p>
    <div class="header-badge">🔒 Secure Government Portal • SSL Encrypted • Session Monitored</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 10. LOGIN PAGE (PROFESSIONAL — NETWORK UNIVERSAL)
# ============================================================
if not st.session_state["authenticated"]:

    # Centered login form
    lcol1, lcol2, lcol3 = st.columns([1, 2, 1])
    with lcol2:
        st.markdown("""
        <div class="login-box">
            <div class="login-seal"><span>🏛️</span></div>
            <div class="login-title">District Command Centre</div>
            <div class="login-subtitle">Authorized Personnel Access Only — All Sessions Monitored</div>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state["otp_sent"]:
            with st.container():
                input_uid = st.text_input(
                    "🏢 Official Office Code (User ID)",
                    placeholder="e.g., BLK-NW-SADAR or ADMIN-NAWADA-DM"
                ).strip()
                input_pwd = st.text_input(
                    "🔑 System Password",
                    type="password",
                    placeholder="Enter your assigned password"
                )

                if st.button("🔐 Verify Credentials & Request OTP", use_container_width=True):
                    if input_uid in USER_REGISTRY and input_pwd == st.session_state["password_db"].get(input_uid):
                        st.session_state["otp_sent"] = True
                        st.session_state["temp_uid"] = input_uid
                        st.success("✅ Credentials verified! OTP dispatched to registered nodal mobile.")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Office Code or Password. Access Denied.")

                st.markdown("""
                <div class="login-security-badge">
                    <span>🛡️</span>
                    <span>Protected by Multi-Factor Authentication • Government Firewall Compliant</span>
                </div>
                """, unsafe_allow_html=True)

        else:
            with st.container():
                st.info(f"🔑 Session Active for Code: `{st.session_state['temp_uid']}`")
                input_otp = st.text_input(
                    "🔢 Enter 4-Digit Verification OTP",
                    type="password",
                    max_chars=4,
                    placeholder="Enter OTP received"
                )

                user_role = USER_REGISTRY[st.session_state["temp_uid"]]["role"]
                required_otp = "9999" if user_role == "District" else "1234"
                st.caption(f"💡 Testing: Use OTP **`{required_otp}`** for {user_role} level access.")

                btn_c1, btn_c2 = st.columns(2)
                with btn_c1:
                    if st.button("✅ Verify OTP & Login", use_container_width=True):
                        if input_otp == required_otp:
                            st.session_state["authenticated"] = True
                            st.session_state["current_user"] = st.session_state["temp_uid"]
                            st.query_params["session_auth"] = st.session_state["temp_uid"]
                            st.success("🚀 Authorization Successful! Connecting to secure server...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid OTP. Security token mismatch.")
                with btn_c2:
                    if st.button("↩️ Back to Login", use_container_width=True):
                        st.session_state["otp_sent"] = False
                        st.session_state["temp_uid"] = None
                        st.rerun()

# ============================================================
# 11. POST-LOGIN: MAIN APPLICATION
# ============================================================
else:
    user_info = USER_REGISTRY[st.session_state["current_user"]]
    current_role = user_info["role"]
    assigned_office = user_info["name"]
    current_code = st.session_state["current_user"]

    # ── SIDEBAR PROFILE ──
    profile_data = get_user_profile(current_code)

    if profile_data:
        officer_name = profile_data.get("officer_name") or "Authorized Officer"
        office_name = profile_data.get("office_name") or assigned_office
        designation = profile_data.get("designation") or "Desk Representative"
        epf_number = profile_data.get("epf_no") or "N/A"
        raw_photo = str(profile_data.get("photo_url") or "").strip()
        photo_url = get_profile_photo_url(raw_photo)
    else:
        officer_name = "Authorized Officer"
        office_name = assigned_office
        designation = "Desk Representative"
        epf_number = "N/A"
        photo_url = DEFAULT_AVATAR

    # Sidebar profile card with inline fallback
    st.sidebar.markdown(f"""
        <div class="sidebar-profile-card">
            <img src="{photo_url}"
                 onerror="this.onerror=null; this.src='{DEFAULT_AVATAR}';"
                 class="profile-avatar" />
            <h3>{officer_name}</h3>
            <p class="desig-text">{designation}</p>
            <p class="office-text">{office_name}</p>
            <div class="info-badge">
                <span><b>EPF:</b> {epf_number}</span>
                <span><b>Code:</b> {current_code}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar action buttons
    st.sidebar.markdown("---")
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

    # Sidebar system info
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
        <div style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 10px; padding: 12px; font-size: 12px !important;">
            <p style="color: #94a3b8 !important; margin: 0 0 4px 0; font-size: 12px !important;">
                <b style="color: #93c5fd !important;">🏢 Role:</b> {current_role} Level</p>
            <p style="color: #94a3b8 !important; margin: 0 0 4px 0; font-size: 12px !important;">
                <b style="color: #93c5fd !important;">📅 Session:</b> {datetime.now().strftime('%d-%b-%Y %I:%M %p')}</p>
            <p style="color: #94a3b8 !important; margin: 0; font-size: 12px !important;">
                <b style="color: #93c5fd !important;">🔗 Status:</b> Connected (Supabase Live)</p>
        </div>
    """, unsafe_allow_html=True)

    # ── SHARED DOSSIER CARD RENDERER ──
    def render_dossier_card(row_data, is_district=False, key_prefix="dossier"):
        status_val = row_data.get('Normalized_Status', row_data.get('Status', 'Pending'))
        badge_class = "badge-pending"
        if status_val == "In Progress":
            badge_class = "badge-progress"
        elif status_val == "Disposed":
            badge_class = "badge-disposed"

        st.markdown(f"""
            <div class="dossier-card">
                <div class="dossier-header">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <span style="font-size: 18px; font-weight: 800; color: #1e3a8a;">Ticket ID: {row_data.get('Complaint ID', 'N/A')}</span>
                            <span style="margin-left: 10px; font-size: 14px; color: #64748b;">(Ref: {row_data.get('Reference No', 'N/A')})</span>
                        </div>
                        <div><span class="{badge_class}">● {status_val.upper()}</span></div>
                    </div>
                    <div style="margin-top: 8px; font-size: 13.5px; color: #475569;">
                        <strong>Office:</strong> {row_data.get('Jurisdiction', 'N/A')} &nbsp;|&nbsp;
                        <strong>Sector:</strong> {row_data.get('Category', 'N/A')} &nbsp;|&nbsp;
                        <strong>Date:</strong> {row_data.get('Date', 'N/A')} &nbsp;|&nbsp;
                        <strong>Resolution:</strong> {row_data.get('Resolution Date', 'Awaiting ATR')}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown('<div class="dossier-label">📝 Problem Description:</div>', unsafe_allow_html=True)
            desc_text = row_data.get('Description', 'No description provided.')
            st.markdown(f'<div class="dossier-content-desc">{desc_text}</div>', unsafe_allow_html=True)
            raw_c_file = str(row_data.get('Uploaded File URL', ''))
            render_file_action_button(raw_c_file, btn_label="📄 View Complaint Attachment", key_id=f"{key_prefix}_cpl_{row_data.get('Complaint ID')}")

        with col_d2:
            st.markdown('<div class="dossier-label">⚖ District ATR Directive:</div>', unsafe_allow_html=True)
            atr_text = row_data.get('District Action/Opinion', '')
            if not str(atr_text).strip():
                atr_text = "Pending evaluation. ATR will be published post audit."
                st.markdown(f'<div class="dossier-content-desc" style="border-left-color: #f59e0b; background: #fffbeb; color: #b45309;">⏳ {atr_text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="dossier-content-atr">✅ {atr_text}</div>', unsafe_allow_html=True)
            raw_atr_file = str(row_data.get('ATR Response File URL', ''))
            render_file_action_button(raw_atr_file, btn_label="📄 View ATR Document", key_id=f"{key_prefix}_atr_{row_data.get('Complaint ID')}")

    # ====================================================
    # ROLE A: BLOCK PORTAL
    # ====================================================
    if current_role == "Block":
        st.markdown(f"### 📝 Welcome — {assigned_office}")

        tab_new, tab_report, tab_att = st.tabs([
            "🆕 File New Grievance",
            "📊 My Office Reports & ATR",
            "📅 Monthly Attendance"
        ])

        # ── TAB 1: FILE NEW GRIEVANCE ──
        with tab_new:
            with st.form(key="block_grievance_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    issue_date = st.date_input("📅 Identification Date", value=date.today())
                    st.text_input("🏢 Submitting Jurisdiction", value=assigned_office, disabled=True)
                    category = st.selectbox("📂 Operational Sector Domain",
                        ["RTPS", "Lok Shikayat", "E-Kalyan", "Social Security", "Administrative Issue", "Hardware/Network"])
                with col2:
                    ref_no = st.text_input("📋 Reference Number (Optional)", placeholder="e.g., RTPS/2026/XXXX")
                    comp_id = f"CPL{int(datetime.now().timestamp())}"
                    st.text_input("🔖 Case Identifier (Auto)", value=comp_id, disabled=True)

                description = st.text_area("📝 Detailed Problem Description", height=140,
                    placeholder="Describe the issue in detail including error logs, affected services, etc.")
                uploaded_file = st.file_uploader(
                    "📎 Attach Document (PDF, JPG, PNG — Auto-compressed)", type=["pdf", "jpg", "png"])

                if st.form_submit_button("🚀 Transmit to District HQ", use_container_width=True):
                    if not description.strip():
                        st.error("❌ Description is required.")
                    else:
                        with st.spinner("Uploading & saving to Supabase..."):
                            public_file_url = upload_file_to_supabase(uploaded_file, file_prefix=comp_id) if uploaded_file else ""
                            db_payload = {
                                "date": str(issue_date), "jurisdiction": assigned_office,
                                "complaint_id": comp_id, "reference_no": ref_no,
                                "category": category, "status": "Pending",
                                "description": description, "district_action_opinion": "",
                                "resolution_date": None, "uploaded_file_url": public_file_url,
                                "submitted_by_code": current_code, "atr_response_file_url": ""
                            }
                            try:
                                supabase.table("district_complaints").insert(db_payload).execute()
                                st.success(f"🚀 Record Synced! Ticket **{comp_id}** saved.")
                                st.balloons()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Database Error: {e}")

        # ── TAB 2: OFFICE REPORTS & ATR ──
        with tab_report:
            st.subheader("📋 Historical Ledger & ATR Inspector")

            if not df_global.empty and 'Submitted By Code' in df_global.columns:
                filtered_df = df_global[df_global['Submitted By Code'] == current_code]
                if filtered_df.empty:
                    st.info("📂 No past grievances found for this office.")
                else:
                    total_b = len(filtered_df)
                    pending_b = len(filtered_df[filtered_df['Normalized_Status'] == "Pending"])
                    prog_b = len(filtered_df[filtered_df['Normalized_Status'] == "In Progress"])
                    disp_b = len(filtered_df[filtered_df['Normalized_Status'] == "Disposed"])

                    kb1, kb2, kb3, kb4 = st.columns(4)
                    with kb1:
                        st.markdown(f'<div class="metric-card"><span class="metric-icon">📋</span><div class="metric-title">Total Lodged</div><div class="metric-value">{total_b}</div></div>', unsafe_allow_html=True)
                    with kb2:
                        st.markdown(f'<div class="metric-card pending"><span class="metric-icon">🔴</span><div class="metric-title">Pending</div><div class="metric-value" style="color:#ef4444;">{pending_b}</div></div>', unsafe_allow_html=True)
                    with kb3:
                        st.markdown(f'<div class="metric-card progress"><span class="metric-icon">🟡</span><div class="metric-title">Under Review</div><div class="metric-value" style="color:#f59e0b;">{prog_b}</div></div>', unsafe_allow_html=True)
                    with kb4:
                        st.markdown(f'<div class="metric-card disposed"><span class="metric-icon">🟢</span><div class="metric-title">Disposed</div><div class="metric-value" style="color:#10b981;">{disp_b}</div></div>', unsafe_allow_html=True)

                    display_df = filtered_df.copy()

                    # ── 📎 DIRECT CASE ATTACHMENT & ATR DOWNLOAD HUB FOR BLOCK ──
                    blk_cases_with_files = display_df[
                        (display_df['Uploaded File URL'].astype(str).str.startswith("http")) |
                        (display_df['ATR Response File URL'].astype(str).str.startswith("http"))
                    ]

                    with st.expander("📎 Download Case Attachments (Complaint & ATR Documents)", expanded=True):
                        if not blk_cases_with_files.empty:
                            def format_blk_case_label(cid):
                                r = display_df[display_df['Complaint ID'] == cid].iloc[0]
                                has_c = "📄 Complaint" if str(r.get('Uploaded File URL', '')).startswith("http") else ""
                                has_a = "⚖ ATR" if str(r.get('ATR Response File URL', '')).startswith("http") else ""
                                att_tag = " + ".join(filter(None, [has_c, has_a]))
                                return f"{cid} — [{r.get('Category', '')}] ({att_tag})"

                            blk_cids_with_files = list(blk_cases_with_files['Complaint ID'].unique())
                            all_blk_cids = list(display_df['Complaint ID'].unique())
                            sorted_blk_cids = blk_cids_with_files + [c for c in all_blk_cids if c not in blk_cids_with_files]

                            sel_blk_hub_cid = st.selectbox(
                                "Select Case to Download Attached Document(s):",
                                sorted_blk_cids,
                                format_func=format_blk_case_label,
                                key="hub_blk_case_select"
                            )

                            sel_blk_data = display_df[display_df['Complaint ID'] == sel_blk_hub_cid].iloc[0]
                            b_hub_c1, b_hub_c2 = st.columns(2)
                            with b_hub_c1:
                                raw_c = str(sel_blk_data.get('Uploaded File URL', ''))
                                if raw_c.startswith("http"):
                                    render_file_action_button(raw_c, btn_label="📥 Download Complaint Attachment", key_id=f"blk_hub_cpl_{sel_blk_hub_cid}")
                                else:
                                    st.caption("📎 No complaint attachment uploaded for this case.")
                            with b_hub_c2:
                                raw_atr = str(sel_blk_data.get('ATR Response File URL', ''))
                                if raw_atr.startswith("http"):
                                    render_file_action_button(raw_atr, btn_label="📥 Download Official ATR Document", key_id=f"blk_hub_atr_{sel_blk_hub_cid}")
                                else:
                                    st.caption("⚖ No ATR attachment uploaded for this case.")

                            # All cases list with direct 1-click download buttons (identical to Attendance statements)
                            st.markdown(f"**Found {len(blk_cases_with_files)} case(s) with uploaded attachment(s):**")
                            for idx, cf_row in blk_cases_with_files.reset_index(drop=True).iterrows():
                                c_id = cf_row['Complaint ID']
                                c_cat = cf_row.get('Category', 'N/A')
                                
                                c_info, c_btn1, c_btn2 = st.columns([3, 2, 2])
                                with c_info:
                                    st.markdown(f"🔖 **{c_id}** ({c_cat})")
                                with c_btn1:
                                    raw_c_item = str(cf_row.get('Uploaded File URL', ''))
                                    if raw_c_item.startswith("http"):
                                        render_file_action_button(raw_c_item, btn_label="📥 Complaint File", key_id=f"blk_all_cpl_{c_id}_{idx}")
                                    else:
                                        st.caption("—")
                                with c_btn2:
                                    raw_atr_item = str(cf_row.get('ATR Response File URL', ''))
                                    if raw_atr_item.startswith("http"):
                                        render_file_action_button(raw_atr_item, btn_label="📥 ATR File", key_id=f"blk_all_atr_{c_id}_{idx}")
                                    else:
                                        st.caption("—")
                        else:
                            st.info("ℹ️ No complaint or ATR files uploaded for your office's current filter.")

                    if 'Uploaded File URL' in display_df.columns:
                        display_df['📎 Complaint'] = display_df['Uploaded File URL'].apply(
                            lambda x: "✅ Available" if str(x).strip().startswith("http") else "—")
                    if 'ATR Response File URL' in display_df.columns:
                        display_df['📎 ATR'] = display_df['ATR Response File URL'].apply(
                            lambda x: "✅ Available" if str(x).strip().startswith("http") else "—")

                    display_cols = ['Date', 'Complaint ID', 'Reference No', 'Category',
                                    'Normalized_Status', 'Description', 'District Action/Opinion',
                                    'Resolution Date', '📎 Complaint', '📎 ATR']
                    valid_cols = [c for c in display_cols if c in display_df.columns]

                    st.dataframe(
                        display_df[valid_cols].rename(columns={"Normalized_Status": "Status"}),
                        column_config={
                            "📎 Complaint": st.column_config.TextColumn("📎 Complaint", width="small", help="Download from the Case Attachments panel above"),
                            "📎 ATR": st.column_config.TextColumn("📎 ATR", width="small", help="Download from the Case Attachments panel above"),
                            "Description": st.column_config.TextColumn("Description", width="large"),
                            "District Action/Opinion": st.column_config.TextColumn("ATR", width="large")
                        },
                        hide_index=True, use_container_width=True
                    )
                    st.caption("💡 **Tip:** Use the **'Download Case Attachments'** panel above to download Complaint or ATR files directly with 1 click.")

                    # Export toolbar for block
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    exp_c1, exp_c2, exp_c3 = st.columns([5, 2.5, 2.5])
                    with exp_c1:
                        st.caption(f"📊 Showing {len(filtered_df)} records")
                    with exp_c2:
                        csv_data = filtered_df[['Date','Complaint ID','Reference No','Category','Normalized_Status','Description','District Action/Opinion','Resolution Date']].rename(columns={"Normalized_Status":"Status"}).to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Export CSV", csv_data, f"grievances_{current_code}.csv", "text/csv", use_container_width=True)
                    with exp_c3:
                        if FPDF_AVAILABLE:
                            pdf_data = generate_grievance_pdf(filtered_df, f"Office Report — {assigned_office}")
                            if pdf_data:
                                st.download_button("📥 Export PDF", pdf_data, f"grievances_{current_code}.pdf", "application/pdf", use_container_width=True)

                    st.markdown("---")
                    st.markdown("### 🔍 Case Dossier Inspector")
                    blk_unique_ids = list(filtered_df['Complaint ID'].unique())
                    default_blk_idx = 0
                    if blk_sel_rows and len(blk_sel_rows) > 0:
                        clicked_blk_id = display_df.iloc[blk_sel_rows[0]]['Complaint ID']
                        if clicked_blk_id in blk_unique_ids:
                            default_blk_idx = blk_unique_ids.index(clicked_blk_id)
                    selected_cpl = st.selectbox("Select Complaint ID:", blk_unique_ids, index=default_blk_idx, key="block_dossier_select")
                    selected_row = filtered_df[filtered_df['Complaint ID'] == selected_cpl].iloc[0]
                    render_dossier_card(selected_row, key_prefix="blk_dossier")
            else:
                st.info("No records to display.")

        # ── TAB 3: MONTHLY ATTENDANCE ──
        with tab_att:
            st.subheader(f"📑 Monthly Attendance — {assigned_office}")

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                selected_month = st.selectbox("Select Month", range(1, 13),
                    format_func=lambda m: calendar.month_name[m],
                    index=datetime.now().month - 1)
            with col_m2:
                selected_year = st.number_input("Select Year", min_value=2024, max_value=2030, value=datetime.now().year)

            # Executive Registration Section
            with st.expander("➕ Register / Update Executive / Employee for this Office", expanded=False):
                st.markdown("##### Add New Employee / Executive to this Office")
                with st.form("add_executive_form", clear_on_submit=True):
                    ea_col1, ea_col2 = st.columns(2)
                    with ea_col1:
                        new_emp_name = st.text_input("Executive Full Name *", placeholder="e.g. Ramesh Kumar")
                        new_emp_desig = st.text_input("Designation *", placeholder="e.g. Executive Assistant / Panchayat Secretary")
                        new_emp_epf = st.text_input("EPF Number / ID", placeholder="Optional EPF or Staff ID")
                    with ea_col2:
                        suggested_code = f"{current_code}-EMP{int(datetime.now().timestamp())%100000}"
                        new_emp_code = st.text_input("Unique Employee Code *", value=suggested_code, help="Must be unique. Format: OFFICE_CODE-EMP...")
                        new_emp_photo = st.file_uploader("Upload Passport Photo (Optional)", type=["jpg", "png", "jpeg"], key="exec_photo_upload")
                    
                    if st.form_submit_button("💾 Save Executive to Office Ledger", use_container_width=True):
                        if not new_emp_name.strip() or not new_emp_desig.strip() or not new_emp_code.strip():
                            st.error("Please enter Employee Name, Designation, and Employee Code.")
                        else:
                            photo_up_url = ""
                            if new_emp_photo:
                                photo_up_url = upload_file_to_supabase(new_emp_photo, file_prefix=f"PROF_{new_emp_code.strip()}")
                            
                            exec_payload = {
                                "user_code": new_emp_code.strip(),
                                "officer_name": new_emp_name.strip(),
                                "designation": new_emp_desig.strip(),
                                "office_name": assigned_office,
                                "epf_no": new_emp_epf.strip() if new_emp_epf else "N/A",
                                "photo_url": photo_up_url,
                                "role": "Block"
                            }
                            if add_executive_profile(exec_payload):
                                st.success(f"✅ Executive **{new_emp_name}** successfully enrolled under {assigned_office}!")
                                st.rerun()

            # Load employees for this office using smart matching (by user_code prefix or office name)
            office_emp_df = get_office_employees(current_code, assigned_office)

            if office_emp_df.empty:
                st.warning("⚠️ No employees registered for this office yet. Use the **'➕ Register / Update Executive'** section above to add employees.")
            else:
                st.info(f"👥 {len(office_emp_df)} employee(s) registered under {assigned_office}.")

                # Bulk Submission & Quick Actions
                st.markdown("##### ⚡ Quick Bulk Actions")
                bulk_c1, bulk_c2, bulk_c3 = st.columns([2, 2, 3])
                with bulk_c1:
                    default_status_bulk = st.selectbox("Set All Status To", ["Present", "Absent", "Leave / CL"], key="bulk_stat_sel")
                with bulk_c2:
                    default_working_days = st.number_input("Default Working Days", min_value=1, max_value=31, value=30, key="bulk_work_days")
                with bulk_c3:
                    st.caption("Tip: You can customize individual rows below or submit for all employees at once.")

                with st.form("attendance_submission_form"):
                    st.markdown("#### 📋 Staff Attendance & Absenty Ledger")
                    for idx, emp_row in office_emp_df.iterrows():
                        e_name = emp_row.get("officer_name", f"Employee {idx+1}")
                        e_desig = emp_row.get("designation", "Staff")
                        e_photo = get_profile_photo_url(str(emp_row.get("photo_url", "")))

                        # Employee card with photo
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 16px;
                                    background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <img src="{e_photo}" onerror="this.onerror=null; this.src='{DEFAULT_AVATAR}';"
                                     style="width: 44px; height: 44px; border-radius: 50%; object-fit: cover; border: 2px solid #cbd5e1;" />
                                <div>
                                    <div style="font-weight: 700; color: #0f172a; font-size: 15px;">{e_name}</div>
                                    <div style="font-size: 12px; color: #64748b;">{e_desig} &nbsp;|&nbsp; <span style="color:#2563eb;">Code: {emp_row.get('user_code', '')}</span></div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.checkbox(
                            f"☑️ **Submit Absenty for {e_name}** *(Uncheck if on leave / transferred / not submitting this month)*",
                            value=True,
                            key=f"att_inc_{idx}",
                            help="Uncheck if this employee is on leave, deputation, or did not submit absenty this month."
                        )

                        c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
                        with c1:
                            stat_opts = ["Present", "Absent", "Leave / CL", "Partial Absent"]
                            def_idx = stat_opts.index(default_status_bulk) if default_status_bulk in stat_opts else 0
                            st.selectbox("Status", stat_opts, index=def_idx, key=f"att_stat_{idx}")
                        with c2:
                            st.number_input("Working Days", min_value=1, max_value=31, value=int(default_working_days), key=f"att_work_{idx}")
                        with c3:
                            initial_absent = 0 if default_status_bulk == "Present" else (int(default_working_days) if default_status_bulk == "Absent" else 1)
                            st.number_input("Absent Days", min_value=0, max_value=31, value=initial_absent, key=f"att_abs_{idx}")
                        with c4:
                            st.text_input("Remarks / Reason", placeholder="Leave / Absenty details", key=f"att_rem_{idx}")
                        st.markdown("---")

                    doc_file = st.file_uploader("📎 Attach Signed Attendance / Absenty Sheet (PDF/JPG) - Mandatory for HQ Verification", type=["pdf", "jpg", "png"])

                    if st.form_submit_button("🚀 Submit Bulk Attendance to District HQ", use_container_width=True):
                        with st.spinner("Processing bulk attendance transmission..."):
                            public_doc_url = ""
                            if doc_file:
                                public_doc_url = upload_file_to_supabase(doc_file, file_prefix=f"ATT_{current_code}_{selected_month}_{selected_year}")

                            success_count = 0
                            skipped_names = []
                            for idx, emp_row in office_emp_df.iterrows():
                                is_included = st.session_state.get(f"att_inc_{idx}", True)
                                emp_name = emp_row.get("officer_name", f"Employee {idx+1}")
                                if not is_included:
                                    skipped_names.append(emp_name)
                                    continue
                                
                                w_days = int(st.session_state.get(f"att_work_{idx}", default_working_days))
                                a_days = int(st.session_state.get(f"att_abs_{idx}", 0))
                                payload = {
                                    "month": selected_month, "year": selected_year,
                                    "office_code": current_code, "office_name": assigned_office,
                                    "employee_name": emp_name,
                                    "designation": emp_row.get("designation", "Staff"),
                                    "attendance_status": st.session_state.get(f"att_stat_{idx}", "Present"),
                                    "total_working_days": w_days,
                                    "days_present": max(0, w_days - a_days),
                                    "days_absent": a_days,
                                    "remarks": st.session_state.get(f"att_rem_{idx}", ""),
                                    "supporting_doc_url": public_doc_url,
                                    "submitted_by": current_code
                                }
                                if upload_attendance_record(payload):
                                    success_count += 1

                            if success_count > 0:
                                skip_info = f" ({len(skipped_names)} excluded: {', '.join(skipped_names)})" if skipped_names else ""
                                st.success(f"✅ Attendance & Absenty for {success_count} employee(s){skip_info} submitted for {calendar.month_name[selected_month]} {selected_year}!")
                                st.balloons()
                            elif skipped_names:
                                st.warning(f"All {len(skipped_names)} employee(s) were excluded from this month's transmission.")


    # ====================================================
    # ROLE B: DISTRICT ADMIN DASHBOARD (DM LEVEL)
    # ====================================================
    else:
        st.markdown("### 📊 Command Control Centre — District Administration")

        adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5 = st.tabs([
            "🔍 Live Grievance Explorer",
            "📈 Operational & ATR Analytics",
            "⚙️ Action Taken Cell (ATR)",
            "🛡️ Security Desk",
            "📑 Attendance & Payroll Portal"
        ])

        # ── TAB 1: LIVE GRIEVANCE EXPLORER ──
        with adm_tab1:
            st.subheader("🌐 Global Grievance Registry")

            if not df_global.empty:
                # Filters row
                f_col1, f_col2, f_col3, f_col4 = st.columns(4)
                with f_col1:
                    filter_status = st.selectbox("🔖 Status Filter", ["All Statuses", "Pending", "In Progress", "Disposed"])
                with f_col2:
                    all_nodes = ["All Jurisdictions"] + sorted(list(df_global['Jurisdiction'].unique()))
                    filter_node = st.selectbox("🏢 Jurisdiction Filter", all_nodes)
                with f_col3:
                    all_cats = ["All Categories"] + sorted(list(df_global['Category'].unique()))
                    filter_cat = st.selectbox("📂 Category Filter", all_cats)
                with f_col4:
                    date_options = ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
                    filter_date = st.selectbox("📅 Date Range", date_options)

                filtered_global = df_global.copy()
                if filter_status != "All Statuses":
                    filtered_global = filtered_global[filtered_global['Normalized_Status'] == filter_status]
                if filter_node != "All Jurisdictions":
                    filtered_global = filtered_global[filtered_global['Jurisdiction'] == filter_node]
                if filter_cat != "All Categories":
                    filtered_global = filtered_global[filtered_global['Category'] == filter_cat]
                if filter_date != "All Time" and 'Date' in filtered_global.columns:
                    try:
                        days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
                        cutoff = date.today() - timedelta(days=days_map.get(filter_date, 9999))
                        filtered_global = filtered_global[filtered_global['Date'] >= cutoff]
                    except Exception:
                        pass

                # Summary counts
                st.markdown(f"""
                <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px;">
                    <div style="background:#eff6ff; padding:8px 18px; border-radius:10px; border:1px solid #bfdbfe;">
                        <span style="font-size:13px; color:#1e40af; font-weight:700;">📋 Total: {len(filtered_global)}</span>
                    </div>
                    <div style="background:#fef2f2; padding:8px 18px; border-radius:10px; border:1px solid #fecaca;">
                        <span style="font-size:13px; color:#991b1b; font-weight:700;">🔴 Pending: {len(filtered_global[filtered_global['Normalized_Status']=='Pending'])}</span>
                    </div>
                    <div style="background:#fffbeb; padding:8px 18px; border-radius:10px; border:1px solid #fde68a;">
                        <span style="font-size:13px; color:#92400e; font-weight:700;">🟡 In Progress: {len(filtered_global[filtered_global['Normalized_Status']=='In Progress'])}</span>
                    </div>
                    <div style="background:#f0fdf4; padding:8px 18px; border-radius:10px; border:1px solid #bbf7d0;">
                        <span style="font-size:13px; color:#166534; font-weight:700;">🟢 Disposed: {len(filtered_global[filtered_global['Normalized_Status']=='Disposed'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── 📎 DIRECT CASE ATTACHMENT & ATR DOWNLOAD HUB (BSWAN / ALL NETWORKS) ──
                cases_with_files = filtered_global[
                    (filtered_global['Uploaded File URL'].astype(str).str.startswith("http")) |
                    (filtered_global['ATR Response File URL'].astype(str).str.startswith("http"))
                ]

                with st.expander("📎 Download Case Attachments (Complaint & ATR Documents)", expanded=True):
                    if not cases_with_files.empty:
                        def format_case_label(cid):
                            r = filtered_global[filtered_global['Complaint ID'] == cid].iloc[0]
                            has_c = "📄 Complaint" if str(r.get('Uploaded File URL', '')).startswith("http") else ""
                            has_a = "⚖ ATR" if str(r.get('ATR Response File URL', '')).startswith("http") else ""
                            att_tag = " + ".join(filter(None, [has_c, has_a]))
                            return f"{cid} — {r.get('Jurisdiction', 'N/A')} [{r.get('Category', '')}] ({att_tag})"

                        cids_with_files = list(cases_with_files['Complaint ID'].unique())
                        all_cids = list(filtered_global['Complaint ID'].unique())
                        sorted_cids = cids_with_files + [c for c in all_cids if c not in cids_with_files]

                        sel_hub_cid = st.selectbox(
                            "Select Case to Download Attached Document(s):",
                            sorted_cids,
                            format_func=format_case_label,
                            key="hub_adm_case_select"
                        )

                        sel_case_data = filtered_global[filtered_global['Complaint ID'] == sel_hub_cid].iloc[0]
                        hub_c1, hub_c2 = st.columns(2)
                        with hub_c1:
                            raw_c = str(sel_case_data.get('Uploaded File URL', ''))
                            if raw_c.startswith("http"):
                                render_file_action_button(raw_c, btn_label="📥 Download Complaint Attachment", key_id=f"hub_cpl_{sel_hub_cid}")
                            else:
                                st.caption("📎 No complaint attachment uploaded for this case.")
                        with hub_c2:
                            raw_atr = str(sel_case_data.get('ATR Response File URL', ''))
                            if raw_atr.startswith("http"):
                                render_file_action_button(raw_atr, btn_label="📥 Download Official ATR Document", key_id=f"hub_atr_{sel_hub_cid}")
                            else:
                                st.caption("⚖ No ATR attachment uploaded for this case.")

                        # All cases list with direct 1-click download buttons (identical to Attendance statements)
                        st.markdown(f"**Found {len(cases_with_files)} case(s) with uploaded attachment(s):**")
                        for idx, cf_row in cases_with_files.reset_index(drop=True).iterrows():
                            c_id = cf_row['Complaint ID']
                            c_jur = cf_row.get('Jurisdiction', 'N/A')
                            c_cat = cf_row.get('Category', 'N/A')
                            
                            c_info, c_btn1, c_btn2 = st.columns([3, 2, 2])
                            with c_info:
                                st.markdown(f"🔖 **{c_id}** ({c_jur} — {c_cat})")
                            with c_btn1:
                                raw_c_item = str(cf_row.get('Uploaded File URL', ''))
                                if raw_c_item.startswith("http"):
                                    render_file_action_button(raw_c_item, btn_label="📥 Complaint File", key_id=f"all_cpl_{c_id}_{idx}")
                                else:
                                    st.caption("—")
                            with c_btn2:
                                raw_atr_item = str(cf_row.get('ATR Response File URL', ''))
                                if raw_atr_item.startswith("http"):
                                    render_file_action_button(raw_atr_item, btn_label="📥 ATR File", key_id=f"all_atr_{c_id}_{idx}")
                                else:
                                    st.caption("—")
                    else:
                        st.info("ℹ️ No complaint or ATR files uploaded for the cases in the current filter.")

                # Prepare display columns - status indicator instead of direct external links
                filtered_global['📎 Complaint'] = filtered_global['Uploaded File URL'].apply(
                    lambda x: "✅ Available" if str(x).strip().startswith("http") else "—")
                filtered_global['📎 ATR'] = filtered_global['ATR Response File URL'].apply(
                    lambda x: "✅ Available" if str(x).strip().startswith("http") else "—")

                table_cols = ['Date', 'Jurisdiction', 'Complaint ID', 'Reference No', 'Category',
                              'Normalized_Status', 'Description', 'District Action/Opinion',
                              'Resolution Date', '📎 Complaint', '📎 ATR']
                valid_table_cols = [c for c in table_cols if c in filtered_global.columns]

                st.dataframe(
                    filtered_global[valid_table_cols].rename(columns={"Normalized_Status": "Status"}),
                    column_config={
                        "📎 Complaint": st.column_config.TextColumn("📎 Complaint", width="small", help="Download from the Case Attachments panel above"),
                        "📎 ATR": st.column_config.TextColumn("📎 ATR", width="small", help="Download from the Case Attachments panel above"),
                        "Description": st.column_config.TextColumn("Description", width="large"),
                        "District Action/Opinion": st.column_config.TextColumn("ATR", width="large")
                    },
                    hide_index=True, use_container_width=True
                )
                st.caption("💡 **Tip:** Use the **'Download Case Attachments'** panel above to download Complaint or ATR files directly with 1 click.")

                # ── EXPORT TOOLBAR (Non-overlapping, dedicated row) ──
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                exp_c1, exp_c2, exp_c3 = st.columns([5, 2.5, 2.5])
                with exp_c1:
                    st.caption(f"📊 {len(filtered_global)} records displayed • Export options →")
                with exp_c2:
                    csv_export = filtered_global[['Date','Jurisdiction','Complaint ID','Reference No','Category','Normalized_Status','Description','District Action/Opinion','Resolution Date']].rename(columns={"Normalized_Status":"Status"}).to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Export as CSV", csv_export, "grievance_registry.csv", "text/csv", use_container_width=True, key="csv_export_admin")
                with exp_c3:
                    if FPDF_AVAILABLE:
                        pdf_bytes = generate_grievance_pdf(filtered_global, "Live Grievance Registry — District Level")
                        if pdf_bytes:
                            st.download_button("📥 Export as PDF", pdf_bytes, "grievance_registry.pdf", "application/pdf", use_container_width=True, key="pdf_export_admin")
                    else:
                        st.caption("Install `fpdf2` for PDF export")

                # ── DOSSIER INSPECTOR ──
                st.markdown("---")
                st.markdown("### 🖨️ Case Dossier & ATR Inspector")
                if not filtered_global.empty:
                    adm_unique_ids = list(filtered_global['Complaint ID'].unique())
                    default_adm_idx = 0
                    if adm_sel_rows and len(adm_sel_rows) > 0:
                        clicked_adm_id = filtered_global.iloc[adm_sel_rows[0]]['Complaint ID']
                        if clicked_adm_id in adm_unique_ids:
                            default_adm_idx = adm_unique_ids.index(clicked_adm_id)
                    chosen_id = st.selectbox("Select Complaint ID:", adm_unique_ids, index=default_adm_idx, key="admin_dossier_select")
                    chosen_row = filtered_global[filtered_global['Complaint ID'] == chosen_id].iloc[0]
                    render_dossier_card(chosen_row, is_district=True, key_prefix="adm_tab1_dossier")
            else:
                st.info("📂 Database empty. No grievances filed yet.")

        # ── TAB 2: ADVANCED OPERATIONAL ANALYTICS ──
        with adm_tab2:
            st.subheader("📈 Operational Analytics & Redressal Performance")

            if not df_global.empty:
                total_complaints = len(df_global)
                pending_count = len(df_global[df_global['Normalized_Status'] == "Pending"])
                progress_count = len(df_global[df_global['Normalized_Status'] == "In Progress"])
                disposed_count = len(df_global[df_global['Normalized_Status'] == "Disposed"])
                disposal_rate = round((disposed_count / total_complaints) * 100, 1) if total_complaints > 0 else 0
                pendency_rate = round((pending_count / total_complaints) * 100, 1) if total_complaints > 0 else 0

                # ── KPI CARDS ──
                kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
                with kpi1:
                    st.markdown(f'<div class="metric-card"><span class="metric-icon">📋</span><div class="metric-title">Total Cases</div><div class="metric-value">{total_complaints}</div></div>', unsafe_allow_html=True)
                with kpi2:
                    st.markdown(f'<div class="metric-card pending"><span class="metric-icon">🔴</span><div class="metric-title">Pending</div><div class="metric-value" style="color:#ef4444;">{pending_count}</div></div>', unsafe_allow_html=True)
                with kpi3:
                    st.markdown(f'<div class="metric-card progress"><span class="metric-icon">🟡</span><div class="metric-title">In Progress</div><div class="metric-value" style="color:#f59e0b;">{progress_count}</div></div>', unsafe_allow_html=True)
                with kpi4:
                    st.markdown(f'<div class="metric-card disposed"><span class="metric-icon">🟢</span><div class="metric-title">Disposed</div><div class="metric-value" style="color:#10b981;">{disposed_count}</div></div>', unsafe_allow_html=True)
                with kpi5:
                    st.markdown(f'<div class="metric-card rate"><span class="metric-icon">📊</span><div class="metric-title">Disposal Rate</div><div class="metric-value" style="color:#6366f1;">{disposal_rate}%</div></div>', unsafe_allow_html=True)

                STATUS_COLOR_MAP = {"Pending": "#ef4444", "In Progress": "#f59e0b", "Disposed": "#10b981"}

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

                # ── ROW 1: Pie Chart + Category Bar ──
                ch_col1, ch_col2 = st.columns(2)

                with ch_col1:
                    status_counts = df_global['Normalized_Status'].value_counts().reset_index()
                    status_counts.columns = ['Status', 'Count']
                    fig_status = px.pie(
                        status_counts, names='Status', values='Count',
                        title='Overall Redressal Breakdown (Pending vs Disposed)',
                        hole=0.48, color='Status', color_discrete_map=STATUS_COLOR_MAP
                    )
                    fig_status.update_traces(textposition='inside', textinfo='percent+label+value',
                                            textfont_size=13)
                    fig_status.update_layout(font=dict(size=13), margin=dict(t=50, b=20, l=20, r=20),
                                            legend=dict(orientation="h", yanchor="bottom", y=-0.15))
                    st.plotly_chart(fig_status, use_container_width=True)

                with ch_col2:
                    cat_counts = df_global['Category'].value_counts().reset_index()
                    cat_counts.columns = ['Category', 'Count']
                    fig_cat = px.bar(
                        cat_counts, x='Category', y='Count', color='Category',
                        title='Grievance Volume by Sector Domain', text_auto=True
                    )
                    fig_cat.update_layout(font=dict(size=13), showlegend=False,
                                         margin=dict(t=50, b=20), xaxis_tickangle=-25)
                    fig_cat.update_traces(textposition='outside')
                    st.plotly_chart(fig_cat, use_container_width=True)

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

                # ── ROW 2: GRIEVANCE TREND + SLA GAUGE (NEW) ──
                trend_col, gauge_col = st.columns([3, 2])

                with trend_col:
                    st.markdown('<div class="analytics-section-title">📈 Grievance Filing Trend Over Time</div>', unsafe_allow_html=True)
                    if 'Date' in df_global.columns:
                        try:
                            trend_df = df_global.copy()
                            trend_df['Date'] = pd.to_datetime(trend_df['Date'], errors='coerce')
                            trend_df = trend_df.dropna(subset=['Date'])
                            if not trend_df.empty:
                                daily_counts = trend_df.groupby(trend_df['Date'].dt.date).size().reset_index(name='Count')
                                daily_counts.columns = ['Date', 'Count']
                                daily_counts = daily_counts.sort_values('Date')
                                fig_trend = px.area(
                                    daily_counts, x='Date', y='Count',
                                    title='Daily Grievance Filing Volume',
                                    color_discrete_sequence=['#3b82f6']
                                )
                                fig_trend.update_layout(
                                    font=dict(size=12), margin=dict(t=50, b=20),
                                    xaxis_title="Date", yaxis_title="Cases Filed",
                                    hovermode="x unified"
                                )
                                fig_trend.update_traces(fill='tozeroy', line_shape='spline')
                                st.plotly_chart(fig_trend, use_container_width=True)
                            else:
                                st.info("No dated records for trend analysis.")
                        except Exception:
                            st.info("Unable to generate trend chart.")

                with gauge_col:
                    st.markdown('<div class="analytics-section-title">🎯 SLA Compliance & Disposal Gauge</div>', unsafe_allow_html=True)
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=disposal_rate,
                        delta={'reference': 75, 'increasing': {'color': '#10b981'}, 'decreasing': {'color': '#ef4444'}},
                        number={'suffix': '%', 'font': {'size': 42, 'color': '#0f172a'}},
                        title={'text': 'Disposal Rate vs 75% Target', 'font': {'size': 14, 'color': '#475569'}},
                        gauge={
                            'axis': {'range': [0, 100], 'tickwidth': 2},
                            'bar': {'color': '#1e3a8a', 'thickness': 0.25},
                            'bgcolor': '#f1f5f9',
                            'steps': [
                                {'range': [0, 40], 'color': '#fee2e2'},
                                {'range': [40, 70], 'color': '#fef3c7'},
                                {'range': [70, 100], 'color': '#dcfce7'}
                            ],
                            'threshold': {'line': {'color': '#ef4444', 'width': 3}, 'thickness': 0.8, 'value': 75}
                        }
                    ))
                    fig_gauge.update_layout(margin=dict(t=60, b=20, l=30, r=30), height=320)
                    st.plotly_chart(fig_gauge, use_container_width=True)

                    # Pendency Alert
                    if pendency_rate > 50:
                        st.error(f"⚠️ HIGH PENDENCY ALERT: {pendency_rate}% cases are still pending!")
                    elif pendency_rate > 30:
                        st.warning(f"⚡ Moderate pendency: {pendency_rate}% cases pending.")
                    else:
                        st.success(f"✅ Low pendency: {pendency_rate}% — System performing well.")

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

                # ── ROW 3: AGING ANALYSIS + RESOLUTION TIME (NEW) ──
                aging_col, restime_col = st.columns(2)

                with aging_col:
                    st.markdown('<div class="analytics-section-title">⏱️ Pending Case Aging Analysis</div>', unsafe_allow_html=True)
                    pending_df = df_global[df_global['Normalized_Status'] == 'Pending'].copy()
                    if not pending_df.empty and 'Date' in pending_df.columns:
                        try:
                            pending_df['Filing_Date'] = pd.to_datetime(pending_df['Date'], errors='coerce')
                            pending_df = pending_df.dropna(subset=['Filing_Date'])
                            if not pending_df.empty:
                                pending_df['Days_Pending'] = (pd.Timestamp.now() - pending_df['Filing_Date']).dt.days
                                bins = [0, 7, 14, 30, 60, 9999]
                                labels = ['0-7 Days', '8-14 Days', '15-30 Days', '31-60 Days', '60+ Days']
                                pending_df['Age_Bucket'] = pd.cut(pending_df['Days_Pending'], bins=bins, labels=labels, right=True)
                                age_counts = pending_df['Age_Bucket'].value_counts().reindex(labels).fillna(0).reset_index()
                                age_counts.columns = ['Age Group', 'Count']
                                colors = ['#10b981', '#22c55e', '#f59e0b', '#f97316', '#ef4444']
                                fig_aging = px.bar(
                                    age_counts, x='Age Group', y='Count', text_auto=True,
                                    title='Pending Cases by Age',
                                    color='Age Group', color_discrete_sequence=colors
                                )
                                fig_aging.update_layout(font=dict(size=12), showlegend=False, margin=dict(t=50, b=20))
                                st.plotly_chart(fig_aging, use_container_width=True)
                            else:
                                st.info("No dated pending cases.")
                        except Exception:
                            st.info("Unable to compute aging.")
                    else:
                        st.info("No pending cases to analyze.")

                with restime_col:
                    st.markdown('<div class="analytics-section-title">⚡ Resolution Time Distribution</div>', unsafe_allow_html=True)
                    disposed_df = df_global[df_global['Normalized_Status'] == 'Disposed'].copy()
                    if not disposed_df.empty and 'Date' in disposed_df.columns and 'Resolution Date' in disposed_df.columns:
                        try:
                            disposed_df['Filing_Date'] = pd.to_datetime(disposed_df['Date'], errors='coerce')
                            disposed_df['Res_Date'] = pd.to_datetime(disposed_df['Resolution Date'], errors='coerce')
                            disposed_df = disposed_df.dropna(subset=['Filing_Date', 'Res_Date'])
                            if not disposed_df.empty:
                                disposed_df['Days_To_Resolve'] = (disposed_df['Res_Date'] - disposed_df['Filing_Date']).dt.days
                                disposed_df = disposed_df[disposed_df['Days_To_Resolve'] >= 0]
                                if not disposed_df.empty:
                                    avg_days = round(disposed_df['Days_To_Resolve'].mean(), 1)
                                    median_days = round(disposed_df['Days_To_Resolve'].median(), 1)
                                    st.markdown(f"""
                                    <div style="display:flex; gap:16px; margin-bottom:12px;">
                                        <div style="background:#eff6ff; padding:8px 16px; border-radius:8px; border:1px solid #bfdbfe;">
                                            <span style="font-size:13px; color:#1e40af; font-weight:700;">Avg: {avg_days} days</span>
                                        </div>
                                        <div style="background:#f0fdf4; padding:8px 16px; border-radius:8px; border:1px solid #bbf7d0;">
                                            <span style="font-size:13px; color:#166534; font-weight:700;">Median: {median_days} days</span>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                    fig_hist = px.histogram(
                                        disposed_df, x='Days_To_Resolve', nbins=15,
                                        title='Days Taken to Resolve Cases',
                                        color_discrete_sequence=['#6366f1'],
                                        labels={'Days_To_Resolve': 'Days to Resolve'}
                                    )
                                    fig_hist.update_layout(font=dict(size=12), margin=dict(t=50, b=20),
                                                          yaxis_title="Number of Cases")
                                    st.plotly_chart(fig_hist, use_container_width=True)
                                else:
                                    st.info("No valid resolution time data.")
                            else:
                                st.info("No valid date pairs for resolution time.")
                        except Exception:
                            st.info("Unable to compute resolution times.")
                    else:
                        st.info("No disposed cases with dates available.")

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

                # ── ROW 4: HEATMAP (Jurisdiction × Category) (NEW) ──
                st.markdown('<div class="analytics-section-title">🗺️ Grievance Intensity Heatmap — Jurisdiction × Sector</div>', unsafe_allow_html=True)
                try:
                    heatmap_data = df_global.groupby(['Jurisdiction', 'Category']).size().reset_index(name='Count')
                    if not heatmap_data.empty:
                        heatmap_pivot = heatmap_data.pivot_table(index='Jurisdiction', columns='Category', values='Count', fill_value=0)
                        fig_heatmap = px.imshow(
                            heatmap_pivot,
                            text_auto=True,
                            color_continuous_scale='Blues',
                            title='Case Volume: Jurisdiction × Sector Domain',
                            aspect='auto'
                        )
                        fig_heatmap.update_layout(
                            font=dict(size=12), margin=dict(t=50, b=20, l=10),
                            xaxis_title="Sector Domain", yaxis_title="Jurisdiction",
                            height=max(350, len(heatmap_pivot) * 32 + 100)
                        )
                        st.plotly_chart(fig_heatmap, use_container_width=True)
                except Exception:
                    st.info("Unable to generate heatmap.")

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

                # ── ROW 5: BLOCK PERFORMANCE MATRIX (IMPROVED) ──
                st.markdown('<div class="analytics-section-title">🏢 Block & Subdivision Performance Matrix</div>', unsafe_allow_html=True)
                block_status_df = df_global.groupby(['Jurisdiction', 'Normalized_Status']).size().reset_index(name='Count')
                fig_block = px.bar(
                    block_status_df, x='Jurisdiction', y='Count', color='Normalized_Status',
                    title='Performance by Jurisdiction (Pending / In Progress / Disposed)',
                    barmode='group', color_discrete_map=STATUS_COLOR_MAP, text_auto=True
                )
                fig_block.update_layout(
                    xaxis_tickangle=-35, font=dict(size=13), legend_title_text='Status',
                    height=500, margin=dict(t=50, b=80),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                fig_block.update_traces(textposition='outside')
                st.plotly_chart(fig_block, use_container_width=True)

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

                # ── ROW 6: TOP PERFORMERS LEADERBOARD (NEW) ──
                perf_col1, perf_col2 = st.columns(2)

                with perf_col1:
                    st.markdown('<div class="analytics-section-title">🏆 Top Performers — Disposal Rate Leaderboard</div>', unsafe_allow_html=True)
                    try:
                        perf_data = df_global.groupby('Jurisdiction').agg(
                            Total=('Normalized_Status', 'count'),
                            Disposed=('Normalized_Status', lambda x: (x == 'Disposed').sum())
                        ).reset_index()
                        perf_data['Rate'] = round((perf_data['Disposed'] / perf_data['Total']) * 100, 1)
                        perf_data = perf_data.sort_values('Rate', ascending=False).head(10)

                        fig_perf = px.bar(
                            perf_data, y='Jurisdiction', x='Rate', orientation='h',
                            text=perf_data['Rate'].apply(lambda x: f'{x}%'),
                            color='Rate', color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'],
                            title='Disposal Rate by Office (%)'
                        )
                        fig_perf.update_layout(
                            font=dict(size=12), showlegend=False,
                            margin=dict(t=50, b=20, l=10),
                            yaxis={'categoryorder': 'total ascending'},
                            xaxis_title='Disposal Rate (%)',
                            coloraxis_showscale=False
                        )
                        fig_perf.update_traces(textposition='outside')
                        st.plotly_chart(fig_perf, use_container_width=True)
                    except Exception:
                        st.info("Unable to compute performance data.")

                with perf_col2:
                    st.markdown('<div class="analytics-section-title">📊 Monthly Intake vs Disposal Comparison</div>', unsafe_allow_html=True)
                    try:
                        monthly_df = df_global.copy()
                        monthly_df['Date'] = pd.to_datetime(monthly_df['Date'], errors='coerce')
                        monthly_df = monthly_df.dropna(subset=['Date'])
                        if not monthly_df.empty:
                            monthly_df['Month'] = monthly_df['Date'].dt.to_period('M').astype(str)
                            intake = monthly_df.groupby('Month').size().reset_index(name='Filed')
                            disposed_m = monthly_df[monthly_df['Normalized_Status'] == 'Disposed'].groupby('Month').size().reset_index(name='Disposed')
                            monthly_comp = intake.merge(disposed_m, on='Month', how='left').fillna(0)
                            monthly_comp = monthly_comp.sort_values('Month').tail(12)

                            fig_monthly = go.Figure()
                            fig_monthly.add_trace(go.Bar(
                                x=monthly_comp['Month'], y=monthly_comp['Filed'],
                                name='Filed', marker_color='#3b82f6', text=monthly_comp['Filed'].astype(int),
                                textposition='outside'
                            ))
                            fig_monthly.add_trace(go.Bar(
                                x=monthly_comp['Month'], y=monthly_comp['Disposed'],
                                name='Disposed', marker_color='#10b981', text=monthly_comp['Disposed'].astype(int),
                                textposition='outside'
                            ))
                            fig_monthly.update_layout(
                                title='Monthly: Cases Filed vs Disposed',
                                barmode='group', font=dict(size=12),
                                margin=dict(t=50, b=20),
                                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                                xaxis_title="Month", yaxis_title="Count"
                            )
                            st.plotly_chart(fig_monthly, use_container_width=True)
                        else:
                            st.info("No monthly data available.")
                    except Exception:
                        st.info("Unable to generate monthly comparison.")

            else:
                st.info("No data available for analytics.")

        # ── TAB 3: ACTION TAKEN CELL (ATR) ──
        with adm_tab3:
            st.subheader("⚖️ ATR Evaluation & Directive Module")

            if not df_global.empty:
                case_to_update = st.selectbox(
                    "🎯 Select Complaint ID for ATR",
                    df_global['Complaint ID'].unique()
                )
                case_row = df_global[df_global['Complaint ID'] == case_to_update].iloc[0]
                render_dossier_card(case_row, is_district=True, key_prefix="adm_tab3_atr_dossier")

                st.markdown("#### ✍ Official ATR Directive Entry")
                with st.form(key="hq_atr_form"):
                    current_stat = case_row.get('Normalized_Status', 'Pending')
                    status_options = ["Pending", "In Progress", "Disposed"]
                    default_idx = status_options.index(current_stat) if current_stat in status_options else 0

                    new_status = st.selectbox("📋 Update Status", status_options, index=default_idx)
                    action_remarks = st.text_area(
                        "📝 Orders / Directives / ATR Remarks",
                        value=case_row.get('District Action/Opinion', ''), height=120
                    )
                    res_date = st.date_input("📅 Resolution Date", value=date.today())

                    st.markdown("---")
                    st.markdown("**📤 Attach ATR Document (Optional)**")
                    atr_file = st.file_uploader(
                        "Upload ATR Response (PDF/Image — Auto-compressed)",
                        type=["pdf", "jpg", "png"], key="atr_file_upload"
                    )

                    if st.form_submit_button("⚖️ Publish ATR Directive", use_container_width=True):
                        with st.spinner("Publishing ATR to Supabase..."):
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
                                st.success(f"✅ ATR published for **{case_to_update}**!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Update failed: {e}")
            else:
                st.info("No cases available.")

        # ── TAB 4: SECURITY DESK ──
        with adm_tab4:
            st.subheader("🔑 Central Credentials & Security Desk")

            sec_c1, sec_c2 = st.columns([3, 2])
            with sec_c1:
                target_user = st.selectbox("🏢 Select Office Node", list(USER_REGISTRY.keys()))
                target_info = USER_REGISTRY[target_user]
                st.markdown(f"""
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px; margin:8px 0;">
                    <p style="margin:0; font-size:14px;"><b>Office:</b> {target_info['name']}</p>
                    <p style="margin:4px 0 0 0; font-size:14px;"><b>Role:</b> {target_info['role']} Level</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("🔄 Reset Password to Default (Nawada@123)", use_container_width=True):
                    st.session_state["password_db"][target_user] = "Nawada@123"
                    st.success(f"🔐 Password for **{target_user}** reset to `Nawada@123`.")

            with sec_c2:
                st.markdown("#### 📋 Registered Office Nodes")
                office_list = pd.DataFrame([
                    {"Code": k, "Name": v["name"], "Role": v["role"]}
                    for k, v in USER_REGISTRY.items()
                ])
                st.dataframe(office_list, hide_index=True, use_container_width=True, height=400)


        # ── TAB 5: ATTENDANCE & PAYROLL PORTAL (DISTRICT LEVEL) ──
        with adm_tab5:
            st.subheader("🏢 District Attendance Audit & Payroll Processing")

            ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([2, 2, 3])
            with ctrl_c1:
                audit_month = st.selectbox("📅 Audit Month", range(1, 13),
                    format_func=lambda m: calendar.month_name[m],
                    index=datetime.now().month - 1, key="adm_audit_m")
            with ctrl_c2:
                audit_year = st.number_input("📅 Audit Year", min_value=2024, max_value=2030,
                    value=datetime.now().year, key="adm_audit_y")
            with ctrl_c3:
                st.markdown(f"""
                <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:12px 16px; margin-top:4px;">
                    <span style="font-size:14px; color:#1e40af; font-weight:600;">
                        📊 Showing data for: {calendar.month_name[audit_month]} {audit_year}
                    </span>
                </div>
                """, unsafe_allow_html=True)

            # Load profiles and attendance
            all_profiles_df = pd.DataFrame()
            try:
                prof_res = supabase.table("user_profiles").select("*").execute()
                if prof_res.data:
                    all_profiles_df = pd.DataFrame(prof_res.data)
            except Exception:
                pass

            att_df = load_monthly_attendance(audit_month, audit_year)

            # ── COMPLIANCE METRICS ──
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("### 📊 Office Submission Compliance Report")

            all_registered_offices = set(USER_REGISTRY.keys())
            submitted_offices = set(att_df["office_code"].unique()) if not att_df.empty else set()
            pending_offices = all_registered_offices - submitted_offices
            compliance_rate = round((len(submitted_offices) / len(all_registered_offices)) * 100, 1) if all_registered_offices else 0
            total_staff = len(all_profiles_df) if not all_profiles_df.empty else 0

            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                st.markdown(f'<div class="metric-card"><span class="metric-icon">🏢</span><div class="metric-title">Total Nodes</div><div class="metric-value">{len(all_registered_offices)}</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card disposed"><span class="metric-icon">✅</span><div class="metric-title">Uploaded</div><div class="metric-value" style="color:#10b981;">{len(submitted_offices)}</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="metric-card pending"><span class="metric-icon">⏳</span><div class="metric-title">Pending Upload</div><div class="metric-value" style="color:#ef4444;">{len(pending_offices)}</div></div>', unsafe_allow_html=True)
            with m4:
                st.markdown(f'<div class="metric-card"><span class="metric-icon">👥</span><div class="metric-title">Total Staff</div><div class="metric-value" style="color:#1e3a8a;">{total_staff}</div></div>', unsafe_allow_html=True)
            with m5:
                st.markdown(f'<div class="metric-card rate"><span class="metric-icon">📈</span><div class="metric-title">Compliance</div><div class="metric-value" style="color:#6366f1;">{compliance_rate}%</div></div>', unsafe_allow_html=True)

            # ── SUBMISSION BREAKDOWN ──
            rep_col1, rep_col2 = st.columns(2)

            with rep_col1:
                st.markdown("#### ✅ Submitted Offices")
                if not att_df.empty:
                    summary_sub = att_df.groupby(["office_name", "office_code"]).agg(
                        Employees=('employee_name', 'count'),
                        Total_Absent=('days_absent', 'sum'),
                        Avg_Present=('days_present', 'mean')
                    ).reset_index()
                    summary_sub['Avg_Present'] = summary_sub['Avg_Present'].round(1)
                    st.dataframe(summary_sub, use_container_width=True, hide_index=True)
                else:
                    st.info("No attendance uploaded for this month yet.")

            with rep_col2:
                st.markdown("#### ⏳ Pending Offices")
                if pending_offices:
                    pending_list = []
                    for p_code in sorted(pending_offices):
                        o_info = USER_REGISTRY.get(p_code, {})
                        e_count = len(all_profiles_df[all_profiles_df["user_code"] == p_code]) if not all_profiles_df.empty else 0
                        pending_list.append({
                            "Code": p_code,
                            "Office": o_info.get("name", "N/A"),
                            "Mapped Staff": e_count,
                            "Status": "⏳ Pending"
                        })
                    st.dataframe(pd.DataFrame(pending_list), use_container_width=True, hide_index=True)
                else:
                    st.success("🎉 All offices have uploaded attendance!")

            # ── ATTENDANCE ANALYTICS CHART (NEW) ──
            if not att_df.empty:
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                att_chart_col1, att_chart_col2 = st.columns(2)

                with att_chart_col1:
                    st.markdown("#### 📊 Absenteeism by Office")
                    try:
                        absent_by_office = att_df.groupby("office_name")["days_absent"].sum().reset_index()
                        absent_by_office.columns = ["Office", "Total Absent Days"]
                        absent_by_office = absent_by_office.sort_values("Total Absent Days", ascending=True)
                        fig_absent = px.bar(
                            absent_by_office, y="Office", x="Total Absent Days",
                            orientation='h', text_auto=True,
                            color_discrete_sequence=['#f97316']
                        )
                        fig_absent.update_layout(font=dict(size=12), margin=dict(t=20, b=20, l=10), showlegend=False)
                        st.plotly_chart(fig_absent, use_container_width=True)
                    except Exception:
                        pass

                with att_chart_col2:
                    st.markdown("#### 📊 Attendance Status Distribution")
                    try:
                        status_dist = att_df["attendance_status"].value_counts().reset_index()
                        status_dist.columns = ["Status", "Count"]
                        fig_att_status = px.pie(
                            status_dist, names="Status", values="Count",
                            hole=0.4, color_discrete_sequence=['#10b981', '#ef4444', '#f59e0b', '#6366f1']
                        )
                        fig_att_status.update_traces(textposition='inside', textinfo='percent+label')
                        fig_att_status.update_layout(font=dict(size=12), margin=dict(t=20, b=20))
                        st.plotly_chart(fig_att_status, use_container_width=True)
                    except Exception:
                        pass

            # ── DOWNLOAD SECTION ──
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("### 📥 Export Payroll & Attendance Data")

            if not att_df.empty:
                exp_c1, exp_c2, exp_c3 = st.columns([5, 2.5, 2.5])
                with exp_c1:
                    st.caption(f"📋 {len(att_df)} employee records for {calendar.month_name[audit_month]} {audit_year}")
                with exp_c2:
                    csv_buffer = att_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Download CSV",
                        data=csv_buffer,
                        file_name=f"Attendance_{audit_month}_{audit_year}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="att_csv_dl"
                    )
                with exp_c3:
                    if FPDF_AVAILABLE:
                        att_pdf = generate_attendance_pdf(att_df, audit_month, audit_year)
                        if att_pdf:
                            st.download_button(
                                "📥 Download PDF",
                                data=att_pdf,
                                file_name=f"Attendance_{audit_month}_{audit_year}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key="att_pdf_dl"
                            )

                # ── DETAILED LEDGER ──
                st.markdown("#### 📋 Detailed Employee Attendance Ledger & Document Downloads")

                # Filter by office option for targeted review
                all_att_offices = ["All Offices"] + sorted(list(att_df["office_name"].unique()))
                selected_att_office = st.selectbox("Filter Ledger by Office", all_att_offices, key="adm_att_off_filter")

                display_att_df = att_df.copy()
                if selected_att_office != "All Offices":
                    display_att_df = display_att_df[display_att_df["office_name"] == selected_att_office]

                show_cols = ["office_name", "employee_name", "designation", "attendance_status",
                             "total_working_days", "days_present", "days_absent", "remarks"]
                valid_show = [c for c in show_cols if c in display_att_df.columns]

                st.dataframe(
                    display_att_df[valid_show],
                    use_container_width=True,
                    hide_index=True
                )

                # ── SIGNED OFFICE ATTENDANCE SHEETS (DIRECT MULTI-OFFICE LIST BELOW LEDGER) ──
                if "supporting_doc_url" in att_df.columns:
                    docs_available = att_df[att_df["supporting_doc_url"].astype(str).str.strip().str.startswith("http")]
                    if not docs_available.empty:
                        with st.expander("📎 Download Signed Office Attendance Sheets / Statements", expanded=True):
                            unique_docs = docs_available[["office_name", "supporting_doc_url"]].drop_duplicates()
                            st.markdown(f"**Found {len(unique_docs)} signed office attendance statement file(s) for {calendar.month_name[audit_month]} {audit_year}:**")
                            
                            for idx, doc_row in unique_docs.reset_index(drop=True).iterrows():
                                o_name = doc_row["office_name"]
                                d_url = doc_row["supporting_doc_url"]
                                f_bytes, f_name, f_mime = fetch_storage_file_bytes(d_url, bucket_name="complaint-documents")
                                
                                doc_col1, doc_col2 = st.columns([3, 2])
                                with doc_col1:
                                    st.markdown(f"🏢 **{o_name}**")
                                with doc_col2:
                                    if f_bytes:
                                        ext = f_name.split('.')[-1] if '.' in f_name else 'pdf'
                                        st.download_button(
                                            label=f"📥 Download Sheet — {o_name}",
                                            data=f_bytes,
                                            file_name=f"Attendance_{o_name.replace(' ', '_')}_{calendar.month_name[audit_month]}_{audit_year}.{ext}",
                                            mime=f_mime or "application/pdf",
                                            key=f"att_stmt_dl_{idx}_{o_name.replace(' ', '_')}",
                                            use_container_width=True
                                        )
                                    else:
                                        st.caption("⚠️ File pending or unavailable")
            else:
                st.warning("No attendance data available for the selected period.")

            # ── 👥 DISTRICT EMPLOYEE MASTER REGISTRY & CENTRAL OFFICE MAPPING ──
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("### 👥 District Employee Master Registry & Central Office Mapping")
            st.caption("Centrally map, bulk import via CSV, and manage all executives and staff across all 18 blocks and subdivision offices. Mapped employees will automatically appear in their office's monthly attendance ledger.")

            emp_mgmt_tab1, emp_mgmt_tab2, emp_mgmt_tab3 = st.tabs([
                "📥 Bulk Import via CSV (All Offices)",
                "➕ Register / Reassign Single Staff",
                "📋 Master Staff Directory & Search"
            ])

            # TAB 1: BULK IMPORT VIA CSV
            with emp_mgmt_tab1:
                st.markdown("#### 📥 Bulk Upload & Map Staff via CSV")
                st.info("💡 **Instructions:** Download the standard CSV template below, enter your staff details across all offices, and upload it back. Existing employee codes will be updated and new staff will be mapped instantly.")

                st.download_button(
                    "📄 Download Sample CSV Template",
                    data=generate_sample_employee_csv(),
                    file_name="Nawada_Employees_Mapping_Template.csv",
                    mime="text/csv",
                    help="Pre-formatted CSV template with standard office names and sample rows."
                )

                # Quick Direct Sync Option for 50 Staff (Embedded Roster)
                with st.expander("⚡ Quick Direct Sync: 50 Validated Nawada Staff (One-Click)", expanded=True):
                    st.write("A pre-validated roster of **50 staff profiles** across all 18 blocks & subdivisions is verified and packaged into the portal.")
                    if st.button("🚀 Direct Sync All 50 Staff to Database Now", key="btn_direct_sync_50_staff", use_container_width=True):
                        with st.spinner("Syncing 50 employee profiles to Supabase database..."):
                            df_ready = pd.read_csv(io.StringIO(DEFAULT_50_STAFF_CSV.strip()), dtype=str)
                            records_ready = df_ready.to_dict(orient="records")
                            n_up, err_up = bulk_upsert_employees(records_ready)
                            if err_up:
                                st.error(f"Sync error: {err_up}")
                            else:
                                st.success(f"🎉 Successfully imported and mapped **{n_up}** staff profiles across all offices!")
                                st.balloons()
                                st.rerun()

                uploaded_emp_csv = st.file_uploader(
                    "Upload Completed Staff CSV Spreadsheet",
                    type=["csv"],
                    key="admin_bulk_emp_csv"
                )

                if uploaded_emp_csv:
                    try:
                        csv_df = pd.read_csv(uploaded_emp_csv, dtype=str)
                        csv_df.columns = [str(c).strip().lower().replace(" ", "_") for c in csv_df.columns]

                        # 1. Default Office column resolution
                        if "office_name" in csv_df.columns:
                            def_off_col = "office_name"
                        elif "office" in csv_df.columns:
                            def_off_col = "office"
                        elif "jurisdiction" in csv_df.columns:
                            def_off_col = "jurisdiction"
                        elif "block" in csv_df.columns:
                            def_off_col = "block"
                        else:
                            def_off_col = next((c for c in csv_df.columns if c.startswith("office_") or c == "office" or "block" in c or "jurisdiction" in c), csv_df.columns[0])

                        # 2. Default Officer Name column resolution
                        if "officer_name" in csv_df.columns:
                            def_name_col = "officer_name"
                        elif "employee_name" in csv_df.columns:
                            def_name_col = "employee_name"
                        elif "staff_name" in csv_df.columns:
                            def_name_col = "staff_name"
                        elif "full_name" in csv_df.columns:
                            def_name_col = "full_name"
                        elif "name" in csv_df.columns and "name" != def_off_col:
                            def_name_col = "name"
                        else:
                            def_name_col = next((c for c in csv_df.columns if c != def_off_col and not c.startswith("office_") and c != "office" and ("officer" in c or "employee" in c or "staff" in c or "name" in c)), csv_df.columns[min(2, len(csv_df.columns)-1)])

                        # 3. Default Employee Code column resolution
                        if "user_code" in csv_df.columns:
                            def_code_col = "user_code"
                        elif "employee_code" in csv_df.columns:
                            def_code_col = "employee_code"
                        elif "code" in csv_df.columns:
                            def_code_col = "code"
                        else:
                            def_code_col = next((c for c in csv_df.columns if "code" in c or "id" in c), None)

                        # 4. Default Designation column resolution
                        if "designation" in csv_df.columns:
                            def_desig_col = "designation"
                        elif "post" in csv_df.columns:
                            def_desig_col = "post"
                        else:
                            def_desig_col = next((c for c in csv_df.columns if "desig" in c or "post" in c), None)

                        # 5. Default EPF column resolution
                        if "epf_no" in csv_df.columns:
                            def_epf_col = "epf_no"
                        elif "epf" in csv_df.columns:
                            def_epf_col = "epf"
                        else:
                            def_epf_col = next((c for c in csv_df.columns if "epf" in c or "pf" in c or "uan" in c), None)

                        # Interactive Mapping Selectors
                        st.markdown("##### 📌 Column Mapping Verification")
                        c_map1, c_map2 = st.columns(2)
                        with c_map1:
                            off_idx = list(csv_df.columns).index(def_off_col) if def_off_col in list(csv_df.columns) else 0
                            office_col = st.selectbox("🏢 Office / Jurisdiction Column", list(csv_df.columns), index=off_idx, key="admin_csv_map_off")
                        with c_map2:
                            name_idx = list(csv_df.columns).index(def_name_col) if def_name_col in list(csv_df.columns) else min(2, len(csv_df.columns)-1)
                            name_col = st.selectbox("👤 Employee / Officer Name Column", list(csv_df.columns), index=name_idx, key="admin_csv_map_name")

                        c_map3, c_map4, c_map5 = st.columns(3)
                        with c_map3:
                            code_opts = ["-- Auto-generate Unique Code --"] + list(csv_df.columns)
                            code_idx = (list(csv_df.columns).index(def_code_col) + 1) if def_code_col in list(csv_df.columns) else 0
                            sel_code = st.selectbox("🔑 Employee Code Column", code_opts, index=code_idx, key="admin_csv_map_code")
                            code_col = None if sel_code.startswith("--") else sel_code
                        with c_map4:
                            desig_opts = ["-- Default 'Staff' --"] + list(csv_df.columns)
                            desig_idx = (list(csv_df.columns).index(def_desig_col) + 1) if def_desig_col in list(csv_df.columns) else 0
                            sel_desig = st.selectbox("💼 Designation Column", desig_opts, index=desig_idx, key="admin_csv_map_desig")
                            desig_col = None if sel_desig.startswith("--") else sel_desig
                        with c_map5:
                            epf_opts = ["-- None --"] + list(csv_df.columns)
                            epf_idx = (list(csv_df.columns).index(def_epf_col) + 1) if def_epf_col in list(csv_df.columns) else 0
                            sel_epf = st.selectbox("💳 EPF / ID Column", epf_opts, index=epf_idx, key="admin_csv_map_epf")
                            epf_col = None if sel_epf.startswith("--") else sel_epf

                        if not name_col or not office_col:
                            st.error(f"❌ Could not resolve required columns. Detected columns: `{list(csv_df.columns)}`. Please ensure there is both an **office_name** and an **officer_name** column.")
                        else:
                            st.write(f"📊 Read **{len(csv_df)}** row(s) from uploaded file.")
                            import_rows = []
                            seen_codes = set()
                            duplicate_auto_fixed = 0

                            for idx, r in csv_df.iterrows():
                                e_name = str(r.get(name_col, "")).strip()
                                o_name = str(r.get(office_col, "")).strip()
                                if not e_name or not o_name or e_name.lower() == "nan":
                                    continue

                                e_code = str(r.get(code_col, "")).strip() if code_col else ""
                                if not e_code or e_code.lower() == "nan":
                                    off_slug = "".join([c for c in o_name.upper() if c.isalnum() or c == " "]).replace(" ", "-")[:12]
                                    e_code = f"{off_slug}-EMP-{idx+1:03d}"

                                # Disambiguate duplicate user_code so employees sharing the same code are not overwritten
                                if e_code in seen_codes:
                                    duplicate_auto_fixed += 1
                                    base_c = e_code
                                    c_idx = 2
                                    while f"{base_c}-{c_idx:02d}" in seen_codes:
                                        c_idx += 1
                                    e_code = f"{base_c}-{c_idx:02d}"
                                seen_codes.add(e_code)

                                e_desig = str(r.get(desig_col, "Staff")).strip() if desig_col else "Staff"
                                if e_desig.lower() == "nan" or not e_desig:
                                    e_desig = "Staff"

                                e_epf = str(r.get(epf_col, "")).strip() if epf_col else ""
                                if e_epf.lower() == "nan":
                                    e_epf = ""
                                elif "e+" in e_epf.lower():
                                    try:
                                        e_epf = f"{int(float(e_epf))}"
                                    except Exception:
                                        pass

                                import_rows.append({
                                    "user_code": e_code,
                                    "officer_name": e_name,
                                    "office_name": o_name,
                                    "designation": e_desig,
                                    "epf_no": e_epf,
                                    "role": "Block",
                                    "photo_url": ""
                                })

                            clean_import_df = pd.DataFrame(import_rows)
                            if not clean_import_df.empty:
                                if duplicate_auto_fixed > 0:
                                    st.info(f"ℹ️ Note: Auto-adjusted **{duplicate_auto_fixed}** duplicate code(s) (e.g. repeated `-EMP01` for different staff) to ensure no employee profile is overwritten.")

                                st.markdown("##### 🔍 Preview of Validated Records:")
                                st.dataframe(
                                    clean_import_df[["user_code", "officer_name", "office_name", "designation", "epf_no"]],
                                    use_container_width=True,
                                    hide_index=True
                                )

                                col_imp_btn, col_imp_info = st.columns([3, 4])
                                with col_imp_btn:
                                    if st.button("🚀 Confirm & Import All Employees to Database", key="btn_confirm_emp_import", use_container_width=True):
                                        with st.spinner("Saving employee master directory to Supabase..."):
                                            records_to_save = clean_import_df.to_dict(orient="records")
                                            n_saved, err = bulk_upsert_employees(records_to_save)
                                            if err:
                                                st.error(f"❌ Error during import: {err}")
                                            else:
                                                st.success(f"🎉 Successfully mapped and saved **{n_saved}** employee profiles across **{clean_import_df['office_name'].nunique()}** offices!")
                                                st.balloons()
                                                st.rerun()
                                with col_imp_info:
                                    st.caption(f"Ready to import {len(clean_import_df)} employees across {clean_import_df['office_name'].nunique()} distinct offices.")
                            else:
                                st.warning("No valid employee records found in the uploaded file.")
                    except Exception as e:
                        st.error(f"Failed to process CSV spreadsheet: {e}")

            # TAB 2: REGISTER / REASSIGN SINGLE STAFF
            with emp_mgmt_tab2:
                st.markdown("#### ➕ Add or Reassign Single Employee / Executive")
                with st.form("admin_single_emp_form"):
                    office_names_list = [v["name"] for k, v in USER_REGISTRY.items() if v.get("role") != "District"]
                    s_col1, s_col2 = st.columns(2)
                    with s_col1:
                        sel_office_name = st.selectbox("Select Office / Block Jurisdiction *", office_names_list, key="adm_s_off")
                        s_off_code = next((k for k, v in USER_REGISTRY.items() if v["name"] == sel_office_name), "OFF")
                        s_emp_name = st.text_input("Employee Full Name *", placeholder="e.g. Ramesh Kumar", key="adm_s_name")
                        s_emp_desig = st.text_input("Designation *", placeholder="e.g. Executive Assistant / Panchayat Secretary", key="adm_s_desig")
                    with s_col2:
                        s_default_code = f"{s_off_code}-EMP{datetime.now().strftime('%M%S')}"
                        s_emp_code = st.text_input("Unique Employee Code *", value=s_default_code, key="adm_s_code", help="Must be unique for each employee.")
                        s_emp_epf = st.text_input("EPF Number / Staff ID (Optional)", placeholder="e.g. 101441508206", key="adm_s_epf")
                        s_emp_role = st.selectbox("Role", ["Block", "Subdivision", "District"], key="adm_s_role")

                    if st.form_submit_button("💾 Save Employee to Database", use_container_width=True):
                        if not s_emp_name.strip() or not s_emp_code.strip():
                            st.error("Please provide both Employee Name and Unique Employee Code.")
                        else:
                            payload = {
                                "user_code": s_emp_code.strip(),
                                "officer_name": s_emp_name.strip(),
                                "office_name": sel_office_name,
                                "designation": s_emp_desig.strip() or "Staff",
                                "epf_no": s_emp_epf.strip(),
                                "role": s_emp_role,
                                "photo_url": ""
                            }
                            if add_executive_profile(payload):
                                st.success(f"✅ Employee **{s_emp_name}** successfully mapped to **{sel_office_name}**!")
                                st.rerun()

            # TAB 3: MASTER STAFF DIRECTORY & SEARCH
            with emp_mgmt_tab3:
                st.markdown("#### 📋 Master Employee Directory")
                # Reload profiles to ensure latest data is displayed
                current_profiles_df = pd.DataFrame()
                try:
                    p_res = supabase.table("user_profiles").select("*").execute()
                    if p_res.data:
                        current_profiles_df = pd.DataFrame(p_res.data)
                except Exception:
                    current_profiles_df = all_profiles_df

                if not current_profiles_df.empty:
                    f_c1, f_c2 = st.columns([3, 4])
                    with f_c1:
                        filter_dir_office = st.selectbox(
                            "Filter by Office",
                            ["All Offices"] + sorted(list(current_profiles_df["office_name"].dropna().unique())),
                            key="adm_dir_off_filter"
                        )
                    with f_c2:
                        search_dir_query = st.text_input("🔍 Search Staff by Name, Designation, or Code", key="adm_dir_search")

                    filtered_profiles = current_profiles_df.copy()
                    if filter_dir_office != "All Offices":
                        filtered_profiles = filtered_profiles[filtered_profiles["office_name"] == filter_dir_office]
                    if search_dir_query.strip():
                        q = search_dir_query.strip().lower()
                        filtered_profiles = filtered_profiles[
                            filtered_profiles["officer_name"].str.lower().str.contains(q, na=False) |
                            filtered_profiles["user_code"].str.lower().str.contains(q, na=False) |
                            filtered_profiles["designation"].str.lower().str.contains(q, na=False)
                        ]

                    st.markdown(f"Showing **{len(filtered_profiles)}** staff profile(s) across selected criteria:")
                    show_dir_cols = ["user_code", "officer_name", "office_name", "designation", "epf_no", "role"]
                    valid_dir_cols = [c for c in show_dir_cols if c in filtered_profiles.columns]
                    st.dataframe(filtered_profiles[valid_dir_cols], use_container_width=True, hide_index=True)

                    d_btn_col1, d_btn_col2 = st.columns([4, 4])
                    with d_btn_col1:
                        dir_csv = filtered_profiles[valid_dir_cols].to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "📥 Download Filtered Staff Directory (CSV)",
                            data=dir_csv,
                            file_name="Nawada_Staff_Master_Directory.csv",
                            mime="text/csv",
                            key="dl_master_dir_csv"
                        )

                    with st.expander("🗑️ Delete / Remove an Employee Profile"):
                        st.caption("Remove an employee profile if transferred, retired, or added by mistake.")
                        del_code = st.selectbox(
                            "Select Employee Code to Remove",
                            options=["-- Select --"] + sorted(list(filtered_profiles["user_code"].unique())),
                            key="adm_del_emp_sel"
                        )
                        if del_code != "-- Select --":
                            if st.button(f"⚠️ Confirm Permanent Deletion of `{del_code}`", key="btn_del_emp_confirm"):
                                ok, d_err = delete_employee_profile(del_code)
                                if ok:
                                    st.success(f"Profile `{del_code}` removed from database.")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to delete: {d_err}")
                else:
                    st.info("No employee profiles found in database.")

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
    <div class="corporate-footer">
        <div style="margin-bottom: 6px;">
            <strong style="color: #1e3a8a;">🏛️ District IT Infrastructure Cell, Nawada HQ</strong>
        </div>
        <div>
            Designed & Formulated for Government Optimization Protocols © 2026 |
            <span style="color: #94a3b8;">Powered by Supabase & Streamlit</span>
        </div>
    </div>
""", unsafe_allow_html=True)
