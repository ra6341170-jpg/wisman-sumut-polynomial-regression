import auth
import database as db
import dashboard
import streamlit as st

st.set_page_config(
    page_title="Prediksi Wisman Sumut",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Font ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, .stText, .stApp {
    font-family: 'Inter', sans-serif !important;
}

/* ── Hide Streamlit chrome ────────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Lock sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    min-width: 268px !important;
    max-width: 268px !important;
    transform: none !important;
    visibility: visible !important;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[kind="header"] { display: none !important; }

/* ── App background ───────────────────────────────────────────── */
.stApp {
    background: #f8fafc;
}
.main .block-container {
    background: #f8fafc;
    padding-top: 1.75rem;
    padding-bottom: 2.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* ── Sidebar ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid #1e293b !important;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] hr { border-color: #1e293b !important; margin: .9rem 0 !important; }

/* Sidebar slider overrides */
[data-testid="stSidebar"] [data-testid="stSlider"] label {
    color: #94a3b8 !important;
    font-size: .78rem !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stTickBar"] {
    color: #475569 !important;
}
[data-testid="stSidebar"] [role="slider"] {
    background: #3b82f6 !important;
    border: 2px solid #1d4ed8 !important;
}
[data-testid="stSidebar"] .stSlider > div > div > div {
    background: #1e3a5f !important;
}

/* Sidebar logout button */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid #334155 !important;
    color: #94a3b8 !important;
    border-radius: 8px !important;
    width: 100% !important;
    text-align: left !important;
    padding: .45rem .85rem !important;
    font-size: .8rem !important;
    font-weight: 500 !important;
    transition: all .15s !important;
    margin-top: .25rem !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1e293b !important;
    border-color: #475569 !important;
    color: #f1f5f9 !important;
}

/* ── Metric cards ─────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
    transition: box-shadow .2s, transform .2s;
}
[data-testid="metric-container"]:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,.08);
    transform: translateY(-2px);
}
[data-testid="stMetricLabel"] {
    font-size: .7rem !important;
    color: #6b7280 !important;
    font-weight: 600 !important;
    letter-spacing: .05em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    color: #111827 !important;
    line-height: 1.25 !important;
}
[data-testid="stMetricDelta"] { font-size: .75rem !important; }

/* ── Tabs ─────────────────────────────────────────────────────── */
[data-baseweb="tab-list"] {
    gap: 3px;
    background: #f1f5f9;
    padding: 4px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}
[data-baseweb="tab"] {
    border-radius: 9px !important;
    font-weight: 500 !important;
    font-size: .84rem !important;
    color: #64748b !important;
    padding: .45rem 1rem !important;
    transition: color .15s !important;
    border: none !important;
}
[aria-selected="true"] {
    background: #ffffff !important;
    color: #111827 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.08) !important;
    font-weight: 600 !important;
}

/* ── Dataframe ────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e5e7eb;
    background: white;
}

/* ── Divider ──────────────────────────────────────────────────── */
hr { border-color: #e5e7eb !important; margin: 1.5rem 0 !important; }

/* ── Alerts ─────────────────────────────────────────────────────*/
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Primary button ───────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: #2563eb !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: .88rem !important;
    color: #ffffff !important;
    padding: .55rem 1.6rem !important;
    transition: background .15s, box-shadow .15s, transform .1s !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1d4ed8 !important;
    box-shadow: 0 4px 14px rgba(37,99,235,.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Secondary / default button ──────────────────────────────── */
.stButton > button[kind="secondary"] {
    border-radius: 9px !important;
    font-weight: 500 !important;
    font-size: .84rem !important;
}

/* ── Download button ──────────────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 9px !important;
    color: #374151 !important;
    font-size: .84rem !important;
    font-weight: 500 !important;
    padding: .45rem 1rem !important;
    transition: background .15s, border-color .15s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
    color: #111827 !important;
}

/* ── Expander ─────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    background: white !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    font-size: .85rem !important;
    color: #374151 !important;
    padding: .6rem .75rem !important;
}

/* ── Slider ───────────────────────────────────────────────────── */
[data-testid="stSlider"] label {
    font-weight: 500 !important;
    font-size: .84rem !important;
    color: #374151 !important;
}

/* ── Equation / formula box ───────────────────────────────────── */
.eq-box {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    border-radius: 0 10px 10px 0;
    padding: .9rem 1.1rem;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: .9rem;
    color: #1e40af;
    margin: .5rem 0 1rem;
    word-break: break-all;
    line-height: 1.7;
    letter-spacing: .01em;
}

/* ── Badges ───────────────────────────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    padding: .2rem .6rem;
    border-radius: 999px;
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .04em;
    text-transform: uppercase;
}
.badge-green  { background: #dcfce7; color: #15803d; }
.badge-yellow { background: #fef9c3; color: #a16207; }
.badge-red    { background: #fee2e2; color: #b91c1c; }
.badge-blue   { background: #dbeafe; color: #1d4ed8; }

/* ── Section title / subtitle ─────────────────────────────────── */
.sec-title {
    font-size: .95rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 .15rem;
    line-height: 1.4;
}
.sec-sub {
    font-size: .77rem;
    color: #9ca3af;
    margin: 0 0 .9rem;
    line-height: 1.5;
}

/* ── Stat row (key-value pair) ────────────────────────────────── */
.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: .38rem 0;
    border-bottom: 1px solid #f3f4f6;
}
.stat-key   { font-size: .77rem; color: #9ca3af; }
.stat-value { font-size: .82rem; font-weight: 600; color: #111827; }

/* ── Info / warning callout boxes ────────────────────────────── */
.callout-warning {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 4px solid #f59e0b;
    border-radius: 0 10px 10px 0;
    padding: .8rem 1rem;
}
.callout-info {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-left: 4px solid #3b82f6;
    border-radius: 0 10px 10px 0;
    padding: .8rem 1rem;
}
.callout-warning p, .callout-info p {
    font-size: .78rem;
    margin: 0;
    line-height: 1.65;
}
.callout-warning p { color: #92400e; }
.callout-info p    { color: #1e40af; }

/* ── Page header banner ───────────────────────────────────────── */
.page-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 60%, #3b82f6 100%);
    border-radius: 16px;
    padding: 1.4rem 1.75rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.page-header-left h1 {
    font-size: 1.3rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 .25rem;
    line-height: 1.3;
}
.page-header-left p {
    font-size: .78rem;
    color: #bfdbfe;
    margin: 0;
}
.page-header-badge {
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.2);
    border-radius: 10px;
    padding: .6rem 1rem;
    text-align: center;
}
.page-header-badge span {
    display: block;
    font-size: .65rem;
    color: #93c5fd;
    font-weight: 600;
    letter-spacing: .05em;
    text-transform: uppercase;
    margin-bottom: .15rem;
}
.page-header-badge strong {
    font-size: 1.1rem;
    color: #ffffff;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

db.init_db()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    auth.render_auth_page()
else:
    dashboard.render_dashboard()
