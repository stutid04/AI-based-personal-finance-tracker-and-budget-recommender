import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Finance Tracker", layout="wide")

# ---------------- GLOBAL STYLES ----------------
st.markdown("""
<style>

html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px circle at 20% -10%, #0b1220 10%, #0a0f1a 40%, #080d16 80%) fixed;
  color: #e6edf3;
  font-family: 'Inter', sans-serif;
}
h1,h2,h3,h4 { color: #e6edf3; }

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
    justify-content:center;
    gap:2rem;
}
.stTabs [data-baseweb="tab"]{
    font-size:1.1rem;
    font-weight:700;
    padding:0.8rem 1.2rem;
    border-radius:12px;
}
.stTabs [data-baseweb="tab"]:hover{
    background:#182235;
}

/* Tiles */
.tile{
  background:linear-gradient(180deg,#111a2b 0%,#0e1726 100%);
  border:1px solid #1b2a44;
  border-radius:16px;
  padding:14px 16px;
  box-shadow:0 10px 30px rgba(0,0,0,.25);
}
.tile .label{
  color:#9fb0c9;
  font-size:.9rem;
}
.tile .value{
  color:#e6edf3;
  font-size:1.6rem;
  font-weight:800;
}

/* Cards */
.card{
  background:linear-gradient(180deg,#0f1828 0%,#0c1422 100%);
  border:1px solid #1b2a44;
  border-radius:16px;
  padding:18px;
  margin-bottom:16px;
  box-shadow:0 8px 24px rgba(0,0,0,.25);
}

/* Inputs */
.stTextInput>div>div>input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"]{
  background:#0e1726 !important;
  color:#e6edf3 !important;
  border:1px solid #1b2a44 !important;
}

/* Buttons */
.stButton>button{
  background:#1b2a44;
  border:1px solid #2b4772;
  color:#e6edf3;
  font-weight:700;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    return joblib.load("xgboost_budget_model.pkl")

model = load_model()

# ---------------- SESSION ----------------
if "user_data" not in st.session_state:
    st.session_state.user_data = []

# ---------------- HERO ----------------
st.markdown("""
<div style='padding:20px 0;'>
  <h2>💼 AI Finance Tracker</h2>
  <div style='color:#9fb0c9;'>Smart Budget Prediction & Expense Analytics</div>
</div>
""", unsafe_allow_html=True)

# ---------------- TABS ----------------
tab_dashboard, tab_insights, tab_analytics = st.tabs(
    ["🏠 Dashboard", "🤖 Insights", "📊 Analytics"]
)

# ================= DASHBOARD =================
with tab_dashboard:

    # Tiles Row
    total_income = sum(d["Income"] for d in st.session_state.user_data)
    total_expense = sum(
        d["Food"]+d["Travel"]+d["Bills"]+d["Shopping"]+d["Entertainment"]
        for d in st.session_state.user_data
    )
    savings = total_income - total_expense

    t1, t2, t3 = st.columns(3)

    with t1:
        st.markdown(f"<div class='tile'><div class='label'>Total Income</div><div class='value'>₹ {total_income:,.0f}</div></div>", unsafe_allow_html=True)
    with t2:
        st.markdown(f"<div class='tile'><div class='label'>Total Expense</div><div class='value'>₹ {total_expense:,.0f}</div></div>", unsafe_allow_html=True)
    with t3:
        st.markdown(f"<div class='tile'><div class='label'>Savings</div><div class='value'>₹ {savings:,.0f}</div></div>", unsafe_allow_html=True)

    st.write("")

    # Input Card
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Enter Monthly Financial Details")

    col1, col2 = st.columns(2)

    with col1:
        city = st.selectbox("City", ["Delhi","Mumbai","Bangalore","Chennai"])
        gender = st.selectbox("Gender", ["Male","Female"])
        year = st.number_input("Year", 2020, 2035, 2025)
        month = st.number_input("Month", 1, 12, 6)

    with col2:
        income = st.number_input("Monthly Income", min_value=0.0)
        food = st.number_input("Food Expense", min_value=0.0)
        travel = st.number_input("Travel Expense", min_value=0.0)
        bills = st.number_input("Bills Expense", min_value=0.0)
        shopping = st.number_input("Shopping Expense", min_value=0.0)
        entertainment = st.number_input("Entertainment Expense", min_value=0.0)

    if st.button("Save Data"):
        st.session_state.user_data.append({
            "City":city,"Gender":gender,"Year":year,"Month":month,
            "Income":income,"Food":food,"Travel":travel,
            "Bills":bills,"Shopping":shopping,"Entertainment":entertainment
        })
        st.success("Saved successfully!")

    st.markdown("</div>", unsafe_allow_html=True)

# ================= INSIGHTS =================
with tab_insights:

    if not st.session_state.user_data:
        st.info("No data available yet.")
    else:
        latest = st.session_state.user_data[-1]

        # Prepare model input
        df = pd.DataFrame([latest]).drop(columns=["Income"])
        df = pd.get_dummies(df)
        df = df.reindex(columns=model.get_booster().feature_names, fill_value=0)

        predicted = model.predict(df)[0]

        total_exp = (
            latest["Food"] +
            latest["Travel"] +
            latest["Bills"] +
            latest["Shopping"] +
            latest["Entertainment"]
        )

        income = latest["Income"]

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.subheader("AI Budget Insights")

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"<div class='tile'><div class='label'>Predicted Budget</div><div class='value'>₹ {predicted:,.0f}</div></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='tile'><div class='label'>Your Expense</div><div class='value'>₹ {total_exp:,.0f}</div></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='tile'><div class='label'>Your Income</div><div class='value'>₹ {income:,.0f}</div></div>", unsafe_allow_html=True)

        st.write("")

        # Income vs Expense Chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name="Income",
            x=["This Month"],
            y=[income],
            marker_color="#22c55e"
        ))

        fig.add_trace(go.Bar(
            name="Expense",
            x=["This Month"],
            y=[total_exp],
            marker_color="#ef4444"
        ))

        fig.update_layout(
            barmode="group",
            paper_bgcolor="#0c1422",
            plot_bgcolor="#0c1422",
            font_color="#e6edf3",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#1b2a44")
        )

        st.plotly_chart(fig, use_container_width=True)

        if total_exp > income:
            st.error("⚠ You are spending more than your income!")
        else:
            st.success("✅ Your spending is within income.")

        st.markdown("</div>", unsafe_allow_html=True)


# ================= ANALYTICS =================
with tab_analytics:

    if not st.session_state.user_data:
        st.info("No data available.")
    else:
        df = pd.DataFrame(st.session_state.user_data)

        expense_totals = df[["Food","Travel","Bills","Shopping","Entertainment"]].sum()

        fig = go.Figure(data=[go.Pie(labels=expense_totals.index, values=expense_totals.values)])
        fig.update_layout(paper_bgcolor="#0c1422", font_color="#e6edf3")
        st.plotly_chart(fig, use_container_width=True)
