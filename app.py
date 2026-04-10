import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
import pickle
from pathlib import Path

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinTrack AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: #0e0e16 !important;
    border-right: 1px solid #1e1e2e !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid #1e1e2e !important;
    color: #9b97a0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.04em !important;
    text-align: left !important;
    width: 100% !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.2s ease !important;
    margin-bottom: 0.2rem !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1a1a28 !important;
    border-color: #c9a84c !important;
    color: #c9a84c !important;
}

/* ── METRIC CARDS ── */
.metric-card {
    background: linear-gradient(135deg, #111118 0%, #15151f 100%);
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #c9a84c, #e8c97e, #c9a84c);
}
.metric-card:hover {
    transform: translateY(-2px);
    border-color: #2a2a3e;
}
.metric-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b6878;
    margin-bottom: 0.6rem;
}
.metric-value {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #e8e4dc;
    line-height: 1.1;
}
.metric-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #6b6878;
    margin-top: 0.4rem;
}
.metric-pos { color: #4ade80; }
.metric-neg { color: #f87171; }
.metric-warn { color: #c9a84c; }

/* ── SECTION HEADERS ── */
.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #e8e4dc;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}
.section-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem;
    color: #6b6878;
    letter-spacing: 0.04em;
    margin-bottom: 1.5rem;
}

/* ── DIVIDER ── */
.gold-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #c9a84c44, transparent);
    margin: 2rem 0;
}

/* ── INSIGHT CARDS ── */
.insight-card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-left: 3px solid #c9a84c;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    font-size: 0.88rem;
    color: #b8b4bc;
    line-height: 1.6;
}
.insight-card.danger { border-left-color: #f87171; }
.insight-card.success { border-left-color: #4ade80; }
.insight-card.warn { border-left-color: #c9a84c; }

/* ── CHAT ── */
.chat-bubble-user {
    background: #1a1a28;
    border: 1px solid #2a2a3e;
    border-radius: 12px 12px 4px 12px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
    color: #e8e4dc;
    max-width: 80%;
    margin-left: auto;
}
.chat-bubble-ai {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-left: 2px solid #c9a84c;
    border-radius: 12px 12px 12px 4px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
    color: #b8b4bc;
    max-width: 85%;
    line-height: 1.6;
}

/* ── AUTH FORM ── */
.auth-container {
    max-width: 420px;
    margin: 0 auto;
    padding: 2.5rem;
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
    position: relative;
}
.auth-container::before {
    content: '';
    position: absolute;
    top: 0; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, #c9a84c, transparent);
}
.auth-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 900;
    color: #e8e4dc;
    text-align: center;
    margin-bottom: 0.3rem;
}
.auth-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    color: #6b6878;
    text-align: center;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}
.logo-glyph {
    font-family: 'Playfair Display', serif;
    font-size: 2.5rem;
    color: #c9a84c;
    text-align: center;
    margin-bottom: 1rem;
    display: block;
}

/* ── STREAMLIT OVERRIDES ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > div {
    background: #0a0a0f !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 8px !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #c9a84c !important;
    box-shadow: 0 0 0 2px #c9a84c22 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #c9a84c, #e8c97e) !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em !important;
    padding: 0.6rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

.stSlider > div > div > div > div { background: #c9a84c !important; }

label, .stSelectbox label, .stNumberInput label, .stTextInput label,
.stSlider label, .stRadio label {
    color: #6b6878 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

[data-testid="stMetric"] {
    background: #111118 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

/* hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0e0e16 !important;
    border-bottom: 1px solid #1e1e2e !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6b6878 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.7rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    color: #c9a84c !important;
    border-bottom-color: #c9a84c !important;
}

/* Alert */
.stAlert {
    background: #111118 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 8px !important;
    color: #b8b4bc !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #1e1e2e; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #c9a84c44; }
</style>
""", unsafe_allow_html=True)

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = Path("fintrack.db")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        type TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        note TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)
    conn.commit()
    conn.close()

init_db()

# ── Auth helpers ──────────────────────────────────────────────────────────────
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def register(username, password):
    try:
        conn = get_conn()
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                     (username.strip(), hash_pw(password)))
        conn.commit()
        conn.close()
        return True, "Account created."
    except sqlite3.IntegrityError:
        return False, "Username already exists."

def login(username, password):
    conn = get_conn()
    row = conn.execute("SELECT id, password_hash FROM users WHERE username=?",
                       (username.strip(),)).fetchone()
    conn.close()
    if row and row[1] == hash_pw(password):
        return True, row[0]
    return False, None

# ── Data helpers ──────────────────────────────────────────────────────────────
EXPENSE_CATS = ["Food", "Travel", "Bills", "Entertainment", "Grocery", "Fuel", "Shopping", "Other"]
INCOME_CATS  = ["Salary", "Freelance", "Investment", "Business", "Other"]

def add_transaction(user_id, date, typ, category, amount, note=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO transactions (user_id, date, type, category, amount, note) VALUES (?,?,?,?,?,?)",
        (user_id, str(date), typ, category, float(amount), note)
    )
    conn.commit(); conn.close()

def delete_transaction(txn_id, user_id):
    conn = get_conn()
    conn.execute("DELETE FROM transactions WHERE id=? AND user_id=?", (txn_id, user_id))
    conn.commit(); conn.close()

def update_transaction(txn_id, user_id, date, typ, category, amount, note):
    conn = get_conn()
    conn.execute(
        "UPDATE transactions SET date=?, type=?, category=?, amount=?, note=? WHERE id=? AND user_id=?",
        (str(date), typ, category, float(amount), note, txn_id, user_id)
    )
    conn.commit(); conn.close()

def get_transactions(user_id):
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC",
        conn, params=(user_id,)
    )
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = df['amount'].astype(float)
    return df

def save_chat(user_id, role, message):
    conn = get_conn()
    conn.execute("INSERT INTO chat_history (user_id, role, message) VALUES (?,?,?)",
                 (user_id, role, message))
    conn.commit(); conn.close()

def get_chat(user_id, limit=50):
    conn = get_conn()
    rows = conn.execute(
        "SELECT role, message FROM chat_history WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return list(reversed(rows))

# ── ML Model ─────────────────────────────────────────────────────────────────
MODEL_PATH = Path("model.pkl")

@st.cache_resource
def load_model():
    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return None

def train_model():
    from xgboost import XGBRegressor

    df = pd.read_csv('/mnt/user-data/uploads/Credit_card_transactions_-_India_-_Simple.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y', errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Month'] = df['Date'].dt.month
    df['Year']  = df['Date'].dt.year

    # ── Meaningful features only: no City, Card, Gender dummies ──────────
    # Pivot category spends per (Year, Month) group
    cat_pivot = df.pivot_table(
        index=['Year', 'Month'],
        columns='Exp Type',
        values='Amount',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    cat_pivot.columns.name = None

    # Ensure all category columns exist
    for col in ['Bills', 'Entertainment', 'Food', 'Fuel', 'Grocery', 'Travel']:
        if col not in cat_pivot.columns:
            cat_pivot[col] = 0

    agg = df.groupby(['Year', 'Month']).agg(
        total_spend=('Amount', 'sum'),
        avg_spend=('Amount', 'mean'),
        txn_count=('Amount', 'count'),
    ).reset_index()

    monthly = agg.merge(cat_pivot[['Year','Month','Bills','Entertainment',
                                    'Food','Fuel','Grocery','Travel']],
                        on=['Year','Month'], how='left').fillna(0)

    # Growth ratio: what fraction of this month's spend carries to next month
    monthly = monthly.sort_values(['Year','Month']).reset_index(drop=True)
    monthly['next_spend'] = monthly['total_spend'].shift(-1)
    monthly['spend_ratio'] = monthly['next_spend'] / monthly['total_spend'].replace(0, np.nan)
    monthly = monthly.dropna(subset=['next_spend', 'spend_ratio'])

    FEATURES = ['Month', 'total_spend', 'avg_spend', 'txn_count',
                'Bills', 'Entertainment', 'Food', 'Fuel', 'Grocery', 'Travel']

    X = monthly[FEATURES]
    y = monthly['spend_ratio']   # predict ratio, not raw rupees

    model = XGBRegressor(n_estimators=300, max_depth=4, learning_rate=0.05,
                         subsample=0.8, colsample_bytree=0.8, random_state=42,
                         min_child_weight=5)
    model.fit(X, y)

    bundle = {
        'model': model,
        'features': FEATURES,
        'monthly': monthly,
        'train_ratio_mean': float(y.mean()),
        'train_ratio_std':  float(y.std()),
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(bundle, f)
    return bundle


def predict_budget(bundle, user_df):
    """
    Realistic next-month budget prediction anchored to the user's own scale.

    Steps:
    1.  Personal baseline = weighted moving average of the user's own
        monthly expense totals (recent months weighted higher).
    2.  Small-data fallback: < 3 transactions → return baseline × 1.05.
    3.  Model predicts a *spend ratio* (next/current), trained on the
        dataset's month-over-month patterns. This avoids scale mismatch.
    4.  Ratio is clamped to [0.80, 1.50] so prediction never exceeds
        1.5× current spend or drops below 0.8×.
    5.  Final prediction = baseline × clamped_ratio.
        Hard bounds: [0.8× baseline, 1.5× baseline].
    """
    if user_df is None or user_df.empty:
        return None

    expenses = user_df[user_df['type'] == 'expense'].copy()
    if expenses.empty:
        return None

    # ── 1. Personal monthly baseline ──────────────────────────────────
    expenses['_month'] = expenses['date'].dt.to_period('M')
    monthly_totals = expenses.groupby('_month')['amount'].sum().sort_index()
    n = len(monthly_totals)
    if n == 0:
        return None

    weights = np.arange(1, n + 1, dtype=float)
    weights /= weights.sum()
    personal_baseline = float(np.dot(weights, monthly_totals.values))

    # Current partial-month spend should not drop the baseline
    now = datetime.now()
    current_month = pd.Period(now, 'M')
    current_spend = float(expenses[expenses['_month'] == current_month]['amount'].sum())
    personal_baseline = max(personal_baseline, current_spend)

    # ── 2. Small-data fallback ─────────────────────────────────────────
    if len(expenses) < 3:
        return round(personal_baseline * 1.05, 2)

    # ── 3. Model ratio prediction ──────────────────────────────────────
    cats  = expenses.groupby('category')['amount'].sum()
    total = float(cats.sum())
    avg   = float(expenses['amount'].mean())
    cnt   = int(len(expenses))

    try:
        X = pd.DataFrame([{
            'Month':         now.month,
            'total_spend':   total,
            'avg_spend':     avg,
            'txn_count':     cnt,
            'Bills':         float(cats.get('Bills', 0)),
            'Entertainment': float(cats.get('Entertainment', 0)),
            'Food':          float(cats.get('Food', 0)),
            'Fuel':          float(cats.get('Fuel', 0)),
            'Grocery':       float(cats.get('Grocery', 0)),
            'Travel':        float(cats.get('Travel', 0)),
        }])
        raw_ratio = float(bundle['model'].predict(X[bundle['features']])[0])
    except Exception:
        raw_ratio = bundle.get('train_ratio_mean', 1.0)

    # ── 4. Clamp ratio to [0.80, 1.50] ────────────────────────────────
    clamped_ratio = float(np.clip(raw_ratio, 0.80, 1.50))

    # ── 5. Apply ratio + hard bounds ──────────────────────────────────
    prediction = personal_baseline * clamped_ratio
    prediction = float(np.clip(prediction, 0.80 * personal_baseline,
                                           1.50 * personal_baseline))
    return round(prediction, 2)

# ── Plotly theme ──────────────────────────────────────────────────────────────
PLOT_BG  = '#0a0a0f'
PLOT_PAPER = '#0a0a0f'
GOLD     = '#c9a84c'
COLORS   = ['#c9a84c','#e8c97e','#4ade80','#60a5fa','#f87171','#a78bfa','#34d399','#fb923c']

def apply_theme(fig):
    fig.update_layout(
        paper_bgcolor=PLOT_PAPER,
        plot_bgcolor=PLOT_BG,
        font=dict(family='DM Sans', color='#9b97a0', size=11),
        title_font=dict(family='Playfair Display', color='#e8e4dc', size=15),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#9b97a0')),
        margin=dict(l=16, r=16, t=40, b=16),
        xaxis=dict(gridcolor='#1e1e2e', tickcolor='#1e1e2e', linecolor='#1e1e2e', tickfont_color='#6b6878'),
        yaxis=dict(gridcolor='#1e1e2e', tickcolor='#1e1e2e', linecolor='#1e1e2e', tickfont_color='#6b6878'),
    )
    return fig

# ── Financial suggestions ─────────────────────────────────────────────────────
def generate_suggestions(df):
    if df.empty:
        return [("warn", "Add your income and expenses to receive personalised insights.")]
    
    expenses = df[df['type'] == 'expense']
    income   = df[df['type'] == 'income']
    
    total_exp = expenses['amount'].sum()
    total_inc = income['amount'].sum()
    suggestions = []

    if total_inc > 0:
        ratio = total_exp / total_inc
        if ratio > 0.9:
            suggestions.append(("danger", f"⚠ Critical: You're spending {ratio*100:.0f}% of your income. Immediate budget review needed."))
        elif ratio > 0.7:
            suggestions.append(("warn", f"📊 You're spending {ratio*100:.0f}% of income. Aim to keep expenses below 70%."))
        else:
            suggestions.append(("success", f"✓ Healthy spending ratio at {ratio*100:.0f}% of income. Keep it up!"))

    if not expenses.empty:
        cats = expenses.groupby('category')['amount'].sum()
        top = cats.idxmax()
        pct = cats[top] / total_exp * 100 if total_exp > 0 else 0
        if pct > 40:
            suggestions.append(("warn", f"🏷 '{top}' dominates at {pct:.0f}% of total expenses. Consider diversifying."))
        
        if total_inc > 0:
            for cat in ['Food', 'Entertainment', 'Shopping']:
                if cat in cats:
                    cat_pct = cats[cat] / total_inc * 100
                    if cat_pct > 30:
                        suggestions.append(("danger", f"🍽 {cat} spending exceeds 30% of income ({cat_pct:.0f}%). Try setting a monthly cap."))
            
        if 'Grocery' in cats and total_inc > 0:
            if cats['Grocery'] / total_inc > 0.15:
                suggestions.append(("warn", "🛒 Grocery spend is high. Bulk buying or meal planning could reduce costs."))

    savings = total_inc - total_exp
    if total_inc > 0:
        sav_rate = savings / total_inc * 100
        if sav_rate >= 20:
            suggestions.append(("success", f"💰 Excellent! You're saving {sav_rate:.0f}% of income. Consider investing the surplus."))
        elif sav_rate > 0:
            suggestions.append(("warn", f"💡 Savings rate is {sav_rate:.0f}%. Target 20%+ by trimming discretionary spending."))
        else:
            suggestions.append(("danger", "🔴 You're spending more than you earn. Review and cut non-essential expenses immediately."))

    if not df.empty and 'date' in df.columns:
        recent = df[df['date'] >= (datetime.now() - timedelta(days=7))]
        if len(recent) == 0:
            suggestions.append(("warn", "📅 No transactions logged this week. Keep your records up to date for accurate insights."))

    return suggestions if suggestions else [("success", "✓ Your finances look balanced. Continue monitoring regularly.")]

# ── AI Chatbot ────────────────────────────────────────────────────────────────
def build_financial_context(df, predicted_budget):
    """Build a rich, data-driven context string from real user stats."""
    if df.empty:
        return "User has no transactions recorded yet.", {}

    expenses = df[df['type'] == 'expense']
    income   = df[df['type'] == 'income']
    total_exp = float(expenses['amount'].sum()) if not expenses.empty else 0.0
    total_inc = float(income['amount'].sum())   if not income.empty  else 0.0
    savings   = total_inc - total_exp
    sav_rate  = (savings / total_inc * 100) if total_inc > 0 else 0.0

    cat_sums  = expenses.groupby('category')['amount'].sum().sort_values(ascending=False) if not expenses.empty else pd.Series(dtype=float)
    top_cat   = cat_sums.idxmax() if not cat_sums.empty else 'N/A'
    top_amt   = float(cat_sums.max()) if not cat_sums.empty else 0.0
    top_pct   = (top_amt / total_exp * 100) if total_exp > 0 else 0.0

    # Monthly trend
    if not expenses.empty:
        expenses = expenses.copy()
        expenses['_m'] = expenses['date'].dt.to_period('M')
        monthly = expenses.groupby('_m')['amount'].sum().sort_index()
        months_count = len(monthly)
        avg_monthly  = float(monthly.mean())
        last_month   = float(monthly.iloc[-1]) if len(monthly) > 0 else 0.0
        trend = "increasing" if (len(monthly) >= 2 and monthly.iloc[-1] > monthly.iloc[-2]) else "stable or decreasing"
    else:
        months_count, avg_monthly, last_month, trend = 0, 0.0, 0.0, "unknown"

    stats = {
        'total_inc': total_inc, 'total_exp': total_exp, 'savings': savings,
        'sav_rate': sav_rate, 'top_cat': top_cat, 'top_amt': top_amt,
        'top_pct': top_pct, 'avg_monthly': avg_monthly, 'last_month': last_month,
        'trend': trend, 'months_count': months_count,
        'predicted_budget': predicted_budget,
        'cat_breakdown': cat_sums.to_dict() if not cat_sums.empty else {},
        'txn_count': len(df),
    }

    budget_str = f"₹{predicted_budget:,.0f}" if predicted_budget else "N/A"
    cat_list = "\n".join([f"  • {k}: ₹{v:,.0f} ({v/total_exp*100:.1f}%)" for k, v in cat_sums.items()]) if not cat_sums.empty else "  • No expense data"

    context = f"""You are FinTrack AI, a premium personal finance advisor. Be concise, insightful, direct, and data-driven. Use ₹ for Indian Rupees. Always reference the user's ACTUAL numbers below in your response — never give generic advice without citing their specific data.

═══ USER FINANCIAL SNAPSHOT ═══
Income logged:        ₹{total_inc:,.0f}
Total expenses:       ₹{total_exp:,.0f}
Net savings:          ₹{savings:,.0f} ({sav_rate:.1f}% of income)
Predicted next month: {budget_str}
Months of data:       {months_count}
Avg monthly spend:    ₹{avg_monthly:,.0f}
Last month spend:     ₹{last_month:,.0f}
Spending trend:       {trend}
Transactions logged:  {len(df)}

Expense breakdown by category:
{cat_list}

Top spending category: {top_cat} at ₹{top_amt:,.0f} ({top_pct:.1f}% of total expenses)
═══════════════════════════════

Rules:
- Reference specific rupee amounts from the data above
- Keep response under 130 words
- Be direct and actionable, not vague
- If income is 0, acknowledge the user hasn't logged income yet
"""
    return context, stats


def ai_chat_response(user_msg, df, predicted_budget=None):
    """Fully data-driven chatbot with Claude API + rich fallback responses."""
    user_msg_lower = user_msg.lower()

    context, stats = build_financial_context(df, predicted_budget)

    # ── Try Claude API ────────────────────────────────────────────────
    try:
        import urllib.request, json as _json
        payload = _json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 300,
            "system": context,
            "messages": [{"role": "user", "content": user_msg}]
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
                "x-api-key": ""
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = _json.loads(resp.read())
            return data['content'][0]['text']
    except Exception:
        pass

    # ── Data-driven fallback responses ────────────────────────────────
    ti  = stats.get('total_inc', 0)
    te  = stats.get('total_exp', 0)
    sav = stats.get('savings', 0)
    sr  = stats.get('sav_rate', 0)
    top = stats.get('top_cat', 'N/A')
    top_amt = stats.get('top_amt', 0)
    top_pct = stats.get('top_pct', 0)
    avg_m   = stats.get('avg_monthly', 0)
    pb      = stats.get('predicted_budget')
    cats    = stats.get('cat_breakdown', {})

    if any(k in user_msg_lower for k in ['save', 'saving', 'savings']):
        if ti == 0:
            return "You haven't logged any income yet. Add your income first so I can calculate your savings rate and give specific advice."
        target_savings = ti * 0.20
        gap = target_savings - sav
        if sr >= 20:
            return f"Excellent savings discipline! You're saving ₹{sav:,.0f} ({sr:.1f}% of income) — above the 20% target. Consider channelling the surplus into an index fund SIP or NPS for tax-efficient growth."
        elif sr > 0:
            return f"You're saving ₹{sav:,.0f} ({sr:.1f}% of income). To hit the 20% target you need to save ₹{target_savings:,.0f}/month — a gap of ₹{gap:,.0f}. Your biggest lever is **{top}** (₹{top_amt:,.0f}, {top_pct:.0f}% of spend). Cutting it by 20% saves ₹{top_amt*0.20:,.0f}."
        else:
            return f"You're currently spending ₹{abs(sav):,.0f} more than you earn. Immediate action needed: your **{top}** category alone is ₹{top_amt:,.0f} ({top_pct:.0f}% of all expenses). Set a hard cap on it this month."

    if any(k in user_msg_lower for k in ['overspend', 'too much', 'where', 'most', 'highest']):
        if not cats:
            return "No expense data yet. Add some transactions and I'll identify exactly where your money is going."
        lines = [f"**{k}**: ₹{v:,.0f} ({v/te*100:.1f}%)" for k, v in sorted(cats.items(), key=lambda x: -x[1])[:4]]
        return f"Your top spending areas:\n" + "\n".join(lines) + f"\n\n**{top}** is your biggest category at {top_pct:.0f}% of total spend. If you can cut it by 15%, you'd save ₹{top_amt*0.15:,.0f}/month."

    if any(k in user_msg_lower for k in ['budget', 'forecast', 'predict', 'next month']):
        if pb:
            diff = pb - avg_m if avg_m else 0
            direction = f"↑ ₹{diff:,.0f} higher" if diff > 0 else f"↓ ₹{abs(diff):,.0f} lower"
            return f"Your predicted next-month budget is ₹{pb:,.0f} ({direction} than your ₹{avg_m:,.0f} monthly average). This is based on your spending patterns across {stats.get('months_count',0)} month(s) of data. Try to stay 10% below — target ₹{pb*0.9:,.0f}."
        return "Not enough transaction data to generate a forecast yet. Log at least 3 transactions and the model will activate."

    if any(k in user_msg_lower for k in ['invest', 'investment', 'mutual fund', 'sip', 'stock']):
        emergency = avg_m * 6 if avg_m else 0
        return f"Based on your avg monthly spend of ₹{avg_m:,.0f}, your emergency fund target is ₹{emergency:,.0f} (6 months). Once that's covered, consider: (1) Index fund SIP — ₹{max(sav*0.5,500):,.0f}/month, (2) NPS for 80CCD tax deduction, (3) ELSS funds for 80C benefit."

    if any(k in user_msg_lower for k in ['trend', 'pattern', 'history']):
        t = stats.get('trend', 'unknown')
        lm = stats.get('last_month', 0)
        return f"Your spending is **{t}**. Last month you spent ₹{lm:,.0f} vs a ₹{avg_m:,.0f} monthly average. {'⚠ Consider reviewing your recent transactions.' if t == 'increasing' else '✓ Good spending control recently.'}"

    return f"You've logged ₹{te:,.0f} in expenses and ₹{ti:,.0f} in income — saving ₹{sav:,.0f} ({sr:.1f}%). Ask me about savings, overspending, budget forecast, investments, or spending trends for specific advice."

# ── Pages ─────────────────────────────────────────────────────────────────────
def page_auth():
    st.markdown('<div style="height:5vh"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div class="auth-container">
            <span class="logo-glyph">◈</span>
            <div class="auth-title">FinTrack AI</div>
            <div class="auth-sub">Intelligent Wealth Management</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        
        tab_login, tab_reg = st.tabs(["SIGN IN", "CREATE ACCOUNT"])
        
        with tab_login:
            st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
            username = st.text_input("Username", key="li_user", placeholder="Enter username")
            password = st.text_input("Password", type="password", key="li_pw", placeholder="Enter password")
            if st.button("Sign In", key="btn_login", use_container_width=True):
                ok, uid = login(username, password)
                if ok:
                    st.session_state.user_id = uid
                    st.session_state.username = username
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
        
        with tab_reg:
            st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
            r_user = st.text_input("Choose Username", key="rg_user", placeholder="Pick a username")
            r_pw   = st.text_input("Password", type="password", key="rg_pw", placeholder="Min 6 characters")
            r_pw2  = st.text_input("Confirm Password", type="password", key="rg_pw2", placeholder="Repeat password")
            if st.button("Create Account", key="btn_reg", use_container_width=True):
                if len(r_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                elif r_pw != r_pw2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register(r_user, r_pw)
                    if ok:
                        st.success("Account created! Please sign in.")
                    else:
                        st.error(msg)


def page_dashboard():
    uid = st.session_state.user_id
    df  = get_transactions(uid)
    bundle = load_model()

    # Header
    st.markdown(f"""
    <div style="display:flex; align-items:baseline; justify-content:space-between; margin-bottom:0.3rem;">
        <div class="section-header">Dashboard</div>
        <div style="font-family:'DM Mono',monospace; font-size:0.72rem; color:#6b6878;">
            {datetime.now().strftime('%A, %d %B %Y')}
        </div>
    </div>
    <div class="section-sub">FINANCIAL OVERVIEW · {st.session_state.username.upper()}</div>
    """, unsafe_allow_html=True)

    # KPIs
    expenses = df[df['type'] == 'expense'] if not df.empty else pd.DataFrame()
    income   = df[df['type'] == 'income']  if not df.empty else pd.DataFrame()
    total_exp = expenses['amount'].sum() if not expenses.empty else 0
    total_inc = income['amount'].sum()   if not income.empty  else 0
    savings   = total_inc - total_exp
    pred      = predict_budget(bundle, df) if bundle else None

    sav_color = "metric-pos" if savings >= 0 else "metric-neg"
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub, cls in [
        (c1, "TOTAL INCOME",   f"₹{total_inc:,.0f}",  f"{len(income)} transactions",   ""),
        (c2, "TOTAL EXPENSES", f"₹{total_exp:,.0f}",  f"{len(expenses)} transactions", ""),
        (c3, "NET SAVINGS",    f"₹{savings:,.0f}",    f"{savings/total_inc*100:.1f}% of income" if total_inc else "—", sav_color),
        (c4, "PREDICTED BUDGET", f"₹{pred:,.0f}" if pred else "—", "Next month forecast", "metric-warn"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value {cls}">{val}</div>
                <div class="metric-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # Charts
    if not df.empty:
        row1_l, row1_r = st.columns([1.4, 1])

        with row1_l:
            # Monthly income vs expense
            df_m = df.copy()
            df_m['month'] = df_m['date'].dt.to_period('M').astype(str)
            monthly_inc = df_m[df_m['type']=='income'].groupby('month')['amount'].sum().reset_index(name='Income')
            monthly_exp = df_m[df_m['type']=='expense'].groupby('month')['amount'].sum().reset_index(name='Expense')
            monthly_all = monthly_inc.merge(monthly_exp, on='month', how='outer').fillna(0).sort_values('month')

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name='Income',  x=monthly_all['month'], y=monthly_all['Income'],
                                     marker_color=GOLD, marker_line_width=0))
            fig_bar.add_trace(go.Bar(name='Expenses',x=monthly_all['month'], y=monthly_all['Expense'],
                                     marker_color='#374151', marker_line_width=0))
            fig_bar.update_layout(barmode='group', title='Income vs Expenses', showlegend=True)
            apply_theme(fig_bar)
            st.plotly_chart(fig_bar, use_container_width=True)

        with row1_r:
            # Expense pie
            if not expenses.empty:
                cat_sums = expenses.groupby('category')['amount'].sum().reset_index()
                fig_pie = go.Figure(go.Pie(
                    labels=cat_sums['category'], values=cat_sums['amount'],
                    hole=0.6, textinfo='label+percent',
                    marker=dict(colors=COLORS, line=dict(color=PLOT_BG, width=2)),
                    textfont=dict(size=11)
                ))
                fig_pie.update_layout(title='Expense Breakdown', showlegend=False)
                apply_theme(fig_pie)
                st.plotly_chart(fig_pie, use_container_width=True)

        # Trend line
        if not expenses.empty:
            daily = expenses.groupby(expenses['date'].dt.date)['amount'].sum().reset_index()
            daily.columns = ['date', 'amount']
            daily['ma7'] = daily['amount'].rolling(7, min_periods=1).mean()
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=daily['date'], y=daily['amount'],
                               mode='lines', name='Daily', line=dict(color='#1e1e2e', width=1)))
            fig_line.add_trace(go.Scatter(x=daily['date'], y=daily['ma7'],
                               mode='lines', name='7-day avg', line=dict(color=GOLD, width=2)))
            fig_line.update_layout(title='Daily Spending Trend', showlegend=True)
            apply_theme(fig_line)
            st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.markdown("""
        <div class="insight-card warn" style="text-align:center; padding:2rem;">
            No transactions yet. Head to <strong>Add Transaction</strong> to get started.
        </div>""", unsafe_allow_html=True)

    # Insights
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="font-size:1.1rem; margin-bottom:0.8rem;">AI INSIGHTS</div>', unsafe_allow_html=True)
    for cls, msg in generate_suggestions(df):
        st.markdown(f'<div class="insight-card {cls}">{msg}</div>', unsafe_allow_html=True)


def page_add_transaction():
    uid = st.session_state.user_id

    # Header row with Export button
    hdr_l, hdr_r = st.columns([3, 1])
    with hdr_l:
        st.markdown('<div class="section-header">Add Transaction</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">LOG YOUR INCOME & EXPENSES</div>', unsafe_allow_html=True)
    with hdr_r:
        df_export = get_transactions(uid)
        if not df_export.empty:
            export_df = df_export.copy()
            export_df['date'] = export_df['date'].dt.strftime('%Y-%m-%d')
            csv_bytes = export_df[['date','type','category','amount','note']].to_csv(index=False).encode('utf-8')
            st.markdown("<div style='padding-top:1.2rem;'></div>", unsafe_allow_html=True)
            st.download_button(
                label="⬇ Export CSV",
                data=csv_bytes,
                file_name=f"fintrack_transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                help="Download all your transactions as a CSV file"
            )

    c1, c2 = st.columns(2)
    with c1:
        t_type    = st.selectbox("Type", ["expense", "income"])
        t_cat_exp = st.selectbox("Category", EXPENSE_CATS if t_type == "expense" else INCOME_CATS)
        t_amount  = st.number_input("Amount (₹)", min_value=0.0, step=100.0, format="%.2f")
    with c2:
        t_date = st.date_input("Date", value=datetime.today())
        t_note = st.text_input("Note (optional)", placeholder="e.g. Monthly rent")

    if st.button("Add Transaction", use_container_width=True):
        if t_amount <= 0:
            st.error("Amount must be greater than zero.")
        else:
            add_transaction(uid, t_date, t_type, t_cat_exp, t_amount, t_note)
            st.success(f"✓ {t_type.capitalize()} of ₹{t_amount:,.2f} added.")

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # ── Recent Transactions with Edit / Delete ──
    df = get_transactions(uid)
    if not df.empty:
        st.markdown('<div class="section-header" style="font-size:1.1rem; margin-bottom:0.3rem;">RECENT TRANSACTIONS</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub" style="margin-bottom:1rem;">CLICK ✎ TO EDIT · 🗑 TO DELETE</div>', unsafe_allow_html=True)

        # Init edit state
        if 'edit_id' not in st.session_state:
            st.session_state.edit_id = None

        # Column headers
        hcols = st.columns([1.2, 0.8, 1.1, 1, 1.4, 0.5, 0.5])
        for col, label in zip(hcols, ["DATE", "TYPE", "CATEGORY", "AMOUNT", "NOTE", "", ""]):
            col.markdown(f"<div style='font-size:0.68rem; font-weight:600; letter-spacing:0.1em; color:#6b6878; padding-bottom:0.4rem; border-bottom:1px solid #1e1e2e;'>{label}</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

        for _, row in df.head(25).iterrows():
            txn_id = int(row['id'])

            # ── EDIT MODE ──
            if st.session_state.edit_id == txn_id:
                with st.container():
                    st.markdown("<div style='background:#111118; border:1px solid #c9a84c33; border-radius:10px; padding:1rem; margin-bottom:0.5rem;'>", unsafe_allow_html=True)
                    ec1, ec2, ec3 = st.columns(3)
                    with ec1:
                        e_type = st.selectbox("Type", ["expense","income"],
                                              index=0 if row['type']=='expense' else 1,
                                              key=f"et_{txn_id}")
                        e_cat  = st.selectbox("Category",
                                              EXPENSE_CATS if e_type=="expense" else INCOME_CATS,
                                              index=(EXPENSE_CATS if e_type=="expense" else INCOME_CATS).index(row['category'])
                                              if row['category'] in (EXPENSE_CATS if e_type=="expense" else INCOME_CATS) else 0,
                                              key=f"ec_{txn_id}")
                    with ec2:
                        e_amount = st.number_input("Amount (₹)", value=float(row['amount']),
                                                   min_value=0.01, step=100.0, key=f"ea_{txn_id}")
                        e_date   = st.date_input("Date", value=row['date'].date(), key=f"ed_{txn_id}")
                    with ec3:
                        e_note = st.text_input("Note", value=row['note'] or "", key=f"en_{txn_id}")
                        st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)
                        sc1, sc2 = st.columns(2)
                        with sc1:
                            if st.button("✓ Save", key=f"save_{txn_id}", use_container_width=True):
                                update_transaction(txn_id, uid, e_date, e_type, e_cat, e_amount, e_note)
                                st.session_state.edit_id = None
                                st.success("Transaction updated.")
                                st.rerun()
                        with sc2:
                            if st.button("✕ Cancel", key=f"cancel_{txn_id}", use_container_width=True):
                                st.session_state.edit_id = None
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            # ── DISPLAY MODE ──
            else:
                dcols = st.columns([1.2, 0.8, 1.1, 1, 1.4, 0.5, 0.5])
                type_color = "#c9a84c" if row['type'] == "income" else "#9b97a0"
                amt_color  = "#4ade80" if row['type'] == "income" else "#f87171"
                dcols[0].markdown(f"<div style='font-size:0.83rem; color:#b8b4bc; padding:0.4rem 0;'>{row['date'].strftime('%d %b %Y')}</div>", unsafe_allow_html=True)
                dcols[1].markdown(f"<div style='font-size:0.75rem; font-weight:600; letter-spacing:0.05em; text-transform:uppercase; color:{type_color}; padding:0.4rem 0;'>{row['type']}</div>", unsafe_allow_html=True)
                dcols[2].markdown(f"<div style='font-size:0.83rem; color:#b8b4bc; padding:0.4rem 0;'>{row['category']}</div>", unsafe_allow_html=True)
                dcols[3].markdown(f"<div style='font-family:\"DM Mono\",monospace; font-size:0.83rem; color:{amt_color}; padding:0.4rem 0;'>₹{row['amount']:,.2f}</div>", unsafe_allow_html=True)
                dcols[4].markdown(f"<div style='font-size:0.78rem; color:#6b6878; padding:0.4rem 0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;'>{row['note'] or '—'}</div>", unsafe_allow_html=True)

                if dcols[5].button("✎", key=f"edit_{txn_id}", help="Edit transaction"):
                    st.session_state.edit_id = txn_id
                    st.rerun()

                if dcols[6].button("🗑", key=f"del_{txn_id}", help="Delete transaction"):
                    st.session_state[f"confirm_del_{txn_id}"] = True
                    st.rerun()

                # Inline delete confirmation
                if st.session_state.get(f"confirm_del_{txn_id}"):
                    conf_cols = st.columns([3, 1, 1])
                    conf_cols[0].markdown("<div style='font-size:0.8rem; color:#f87171; padding-top:0.4rem;'>⚠ Delete this transaction?</div>", unsafe_allow_html=True)
                    if conf_cols[1].button("Yes, delete", key=f"yes_{txn_id}"):
                        delete_transaction(txn_id, uid)
                        st.session_state.pop(f"confirm_del_{txn_id}", None)
                        st.success("Transaction deleted.")
                        st.rerun()
                    if conf_cols[2].button("Cancel", key=f"no_{txn_id}"):
                        st.session_state.pop(f"confirm_del_{txn_id}", None)
                        st.rerun()

                st.markdown("<div style='height:1px; background:#1a1a26; margin:0.1rem 0;'></div>", unsafe_allow_html=True)
    else:
        st.markdown('<div class="insight-card warn" style="text-align:center; padding:1.5rem;">No transactions yet. Add one above to get started.</div>', unsafe_allow_html=True)


def page_budget():
    uid = st.session_state.user_id
    df  = get_transactions(uid)
    bundle = load_model()

    st.markdown('<div class="section-header">Budget Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">AI-POWERED FORECAST · XGBOOST MODEL</div>', unsafe_allow_html=True)

    if bundle is None:
        st.info("Model loading...")
        return

    pred = predict_budget(bundle, df)
    expenses = df[df['type'] == 'expense'] if not df.empty else pd.DataFrame()
    total_exp = expenses['amount'].sum() if not expenses.empty else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">PREDICTED BUDGET</div>
            <div class="metric-value metric-warn">₹{pred:,.0f}</div>
            <div class="metric-sub">Next month forecast</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">CURRENT EXPENSES</div>
            <div class="metric-value">₹{total_exp:,.0f}</div>
            <div class="metric-sub">This period</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        diff = pred - total_exp if pred else 0
        cls  = "metric-pos" if diff >= 0 else "metric-neg"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">REMAINING BUFFER</div>
            <div class="metric-value {cls}">₹{diff:,.0f}</div>
            <div class="metric-sub">Predicted − Current</div>
        </div>""", unsafe_allow_html=True)

    if pred and not expenses.empty:
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

        # Gauge
        utilization = min(total_exp / pred * 100, 150) if pred > 0 else 0
        color = '#4ade80' if utilization < 70 else ('#c9a84c' if utilization < 90 else '#f87171')
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=utilization,
            number=dict(suffix='%', font=dict(family='Playfair Display', color='#e8e4dc', size=32)),
            delta=dict(reference=70, suffix='% vs target', font=dict(color='#9b97a0')),
            gauge=dict(
                axis=dict(range=[0,150], tickwidth=1, tickcolor='#1e1e2e', tickfont=dict(color='#6b6878')),
                bar=dict(color=color),
                bgcolor='#111118',
                bordercolor='#1e1e2e',
                steps=[
                    dict(range=[0,70],   color='#0d1f12'),
                    dict(range=[70,90],  color='#1f1a0d'),
                    dict(range=[90,150], color='#1f0d0d'),
                ],
                threshold=dict(line=dict(color='#c9a84c', width=2), thickness=0.75, value=70)
            ),
            title=dict(text="Budget Utilization", font=dict(family='Playfair Display', color='#e8e4dc'))
        ))
        fig_gauge.update_layout(paper_bgcolor=PLOT_PAPER, font_color='#9b97a0', height=280, margin=dict(t=40, b=0))
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Category bars: actual vs proportional budget cap
        cat_sums = expenses.groupby('category')['amount'].sum().reset_index()
        total_actual = cat_sums['amount'].sum()

        # Proportional cap: each category gets the same share of predicted budget
        # as it represents in actual spend — but scaled to the predicted total
        if total_actual > 0:
            cat_sums['prop_weight'] = cat_sums['amount'] / total_actual
            cat_sums['suggested_cap'] = cat_sums['prop_weight'] * pred
        else:
            cat_sums['suggested_cap'] = pred / len(cat_sums)

        # Flag over-budget categories
        cat_sums['over'] = cat_sums['amount'] > cat_sums['suggested_cap']
        bar_colors = [GOLD if not over else '#f87171' for over in cat_sums['over']]

        fig_cat = go.Figure()
        fig_cat.add_trace(go.Bar(
            name='Actual Spend',
            x=cat_sums['category'], y=cat_sums['amount'],
            marker_color=bar_colors, marker_line_width=0,
            text=[f"₹{v:,.0f}" for v in cat_sums['amount']],
            textfont=dict(color='#e8e4dc', size=10), textposition='outside'
        ))
        fig_cat.add_trace(go.Bar(
            name='Proportional Budget Cap',
            x=cat_sums['category'], y=cat_sums['suggested_cap'],
            marker_color='#2a2a3e', marker_line_color='rgba(201,168,76,0.25)',
            marker_line_width=1,
            text=[f"₹{v:,.0f}" for v in cat_sums['suggested_cap']],
            textfont=dict(color='#6b6878', size=10), textposition='outside'
        ))
        fig_cat.update_layout(
            barmode='group',
            title='Actual Spend vs Proportional Budget Cap',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        apply_theme(fig_cat)
        st.plotly_chart(fig_cat, use_container_width=True)

        # Category breakdown table
        st.markdown('<div class="section-header" style="font-size:0.95rem; margin-bottom:0.8rem; margin-top:0.5rem;">CATEGORY ALLOCATION DETAIL</div>', unsafe_allow_html=True)
        hc = st.columns([1.5, 1, 1, 1, 0.8])
        for col, lbl in zip(hc, ["CATEGORY", "ACTUAL", "BUDGET CAP", "VARIANCE", "STATUS"]):
            col.markdown(f"<div style='font-size:0.68rem; font-weight:600; letter-spacing:0.1em; color:#6b6878; padding-bottom:0.4rem; border-bottom:1px solid #1e1e2e;'>{lbl}</div>", unsafe_allow_html=True)
        for _, r in cat_sums.iterrows():
            var   = r['amount'] - r['suggested_cap']
            vcolor = '#f87171' if var > 0 else '#4ade80'
            status = "⚠ Over" if var > 0 else "✓ OK"
            scols = st.columns([1.5, 1, 1, 1, 0.8])
            scols[0].markdown(f"<div style='font-size:0.82rem; color:#b8b4bc; padding:0.35rem 0;'>{r['category']}</div>", unsafe_allow_html=True)
            scols[1].markdown(f"<div style='font-family:\"DM Mono\",monospace; font-size:0.82rem; color:#e8e4dc; padding:0.35rem 0;'>₹{r['amount']:,.0f}</div>", unsafe_allow_html=True)
            scols[2].markdown(f"<div style='font-family:\"DM Mono\",monospace; font-size:0.82rem; color:#9b97a0; padding:0.35rem 0;'>₹{r['suggested_cap']:,.0f}</div>", unsafe_allow_html=True)
            scols[3].markdown(f"<div style='font-family:\"DM Mono\",monospace; font-size:0.82rem; color:{vcolor}; padding:0.35rem 0;'>{'+'if var>0 else ''}₹{var:,.0f}</div>", unsafe_allow_html=True)
            scols[4].markdown(f"<div style='font-size:0.78rem; color:{vcolor}; padding:0.35rem 0;'>{status}</div>", unsafe_allow_html=True)
            st.markdown("<div style='height:1px; background:#1a1a26;'></div>", unsafe_allow_html=True)


def page_chatbot():
    uid = st.session_state.user_id
    df  = get_transactions(uid)
    bundle = load_model()
    pred = predict_budget(bundle, df) if bundle else None

    st.markdown('<div class="section-header">AI Advisor</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">INTELLIGENT FINANCIAL GUIDANCE</div>', unsafe_allow_html=True)

    # Init session chat
    if 'chat_msgs' not in st.session_state:
        saved = get_chat(uid)
        st.session_state.chat_msgs = list(saved) if saved else [
            ("assistant", "Hello! I'm your FinTrack AI advisor. Ask me about your spending patterns, savings strategies, or budget forecasts.")
        ]

    # Display
    for role, msg in st.session_state.chat_msgs:
        if role == "user":
            st.markdown(f'<div class="chat-bubble-user">{msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-ai">◈ {msg}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Quick prompts
    st.markdown("<div style='font-size:0.72rem; color:#6b6878; letter-spacing:0.08em; margin-bottom:0.5rem;'>QUICK QUESTIONS</div>", unsafe_allow_html=True)
    prompts = ["How can I save more?", "Where am I overspending?", "Explain my budget forecast", "Investment tips for beginners"]
    cols = st.columns(4)
    for i, p in enumerate(prompts):
        with cols[i]:
            if st.button(p, key=f"qp_{i}", use_container_width=True):
                st.session_state.pending_msg = p
                st.rerun()

    user_input = st.chat_input("Ask your financial advisor...")
    
    pending = st.session_state.pop('pending_msg', None)
    final_input = pending or user_input

    if final_input:
        st.session_state.chat_msgs.append(("user", final_input))
        save_chat(uid, "user", final_input)
        with st.spinner(""):
            reply = ai_chat_response(final_input, df, pred)
        st.session_state.chat_msgs.append(("assistant", reply))
        save_chat(uid, "assistant", reply)
        st.rerun()


def page_analytics():
    uid = st.session_state.user_id
    df  = get_transactions(uid)

    st.markdown('<div class="section-header">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">DEEP-DIVE SPENDING ANALYSIS</div>', unsafe_allow_html=True)

    if df.empty:
        st.markdown('<div class="insight-card warn" style="text-align:center; padding:2rem;">Add transactions to unlock analytics.</div>', unsafe_allow_html=True)
        return

    expenses = df[df['type'] == 'expense']
    income   = df[df['type'] == 'income']

    # Heatmap - spending by day/month
    if not expenses.empty:
        exp_copy = expenses.copy()
        exp_copy['weekday'] = exp_copy['date'].dt.day_name()
        exp_copy['month']   = exp_copy['date'].dt.strftime('%b %Y')
        heatmap_data = exp_copy.groupby(['weekday', 'month'])['amount'].sum().unstack(fill_value=0)
        day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        heatmap_data = heatmap_data.reindex([d for d in day_order if d in heatmap_data.index])

        fig_heat = go.Figure(go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns.tolist(),
            y=heatmap_data.index.tolist(),
            colorscale=[[0,'#0a0a0f'],[0.5,'#7a5c1a'],[1,'#c9a84c']],
            showscale=True
        ))
        fig_heat.update_layout(title='Spending Heatmap (Day × Month)')
        apply_theme(fig_heat)
        st.plotly_chart(fig_heat, use_container_width=True)

        # Category over time
        exp_copy['month_period'] = exp_copy['date'].dt.to_period('M').astype(str)
        cat_trend = exp_copy.groupby(['month_period','category'])['amount'].sum().reset_index()
        fig_area = px.area(cat_trend, x='month_period', y='amount', color='category',
                           color_discrete_sequence=COLORS, title='Category Trends Over Time')
        fig_area.update_traces(line_width=1)
        apply_theme(fig_area)
        st.plotly_chart(fig_area, use_container_width=True)

        # Top 5 spending categories
        top_cats = expenses.groupby('category')['amount'].sum().nlargest(5).reset_index()
        fig_h = go.Figure(go.Bar(
            x=top_cats['amount'], y=top_cats['category'],
            orientation='h', marker_color=COLORS[:5], marker_line_width=0,
            text=[f"₹{v:,.0f}" for v in top_cats['amount']],
            textfont=dict(color='#e8e4dc'), textposition='auto'
        ))
        fig_h.update_layout(title='Top 5 Expense Categories', yaxis=dict(autorange='reversed'))
        apply_theme(fig_h)
        st.plotly_chart(fig_h, use_container_width=True)


# ── Sidebar & Routing ─────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:1.5rem 1rem 1rem; border-bottom:1px solid #1e1e2e; margin-bottom:1rem;">
            <div style="font-family:'Playfair Display',serif; font-size:1.4rem; font-weight:900; color:#c9a84c;">◈ FinTrack</div>
            <div style="font-size:0.65rem; letter-spacing:0.12em; color:#6b6878; text-transform:uppercase; margin-top:0.2rem;">AI Wealth Manager</div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("dashboard",    "◉  Dashboard"),
            ("add",          "＋  Add Transaction"),
            ("budget",       "◎  Budget Predictor"),
            ("analytics",    "◈  Analytics"),
            ("chatbot",      "◆  AI Advisor"),
        ]
        for key, label in nav_items:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        st.markdown("<div style='position:absolute; bottom:1.5rem; left:1rem; right:1rem;'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:0.7rem; color:#6b6878; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:0.5rem;">
            Signed in as<br>
            <span style="color:#c9a84c;">{st.session_state.get('username','')}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", key="logout", use_container_width=True):
            for k in ['user_id','username','page','chat_msgs']:
                st.session_state.pop(k, None)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if 'user_id' not in st.session_state:
        page_auth()
        return

    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"

    sidebar()

    page = st.session_state.page
    if page == "dashboard":
        page_dashboard()
    elif page == "add":
        page_add_transaction()
    elif page == "budget":
        page_budget()
    elif page == "analytics":
        page_analytics()
    elif page == "chatbot":
        page_chatbot()


# ── Train model on startup ────────────────────────────────────────────────────
if not MODEL_PATH.exists():
    with st.spinner("Training AI model on transaction data…"):
        train_model()
    load_model.clear()

main()
