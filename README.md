# ◈ FinTrack AI — Intelligent Personal Finance Tracker

A production-grade AI-powered finance tracker built with Streamlit, XGBoost, and Plotly.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app will:
1. Automatically train the XGBoost model on first launch (requires the CSV in the same folder)
2. Open in your browser at http://localhost:8501

## Architecture

```
User Interface (Streamlit)
  ↓
Authentication Layer (SHA-256 hashing · SQLite)
  ↓
Financial Data Store (SQLite · Pandas)
  ↓
ML Engine (XGBoost Regressor · Scikit-learn)
  ↓
Insights + Claude AI Chatbot
```

## Features

| Feature | Tech |
|---|---|
| User auth (signup/login) | SQLite + SHA-256 |
| Transaction CRUD | Pandas + SQLite |
| Budget prediction | XGBoost Regressor |
| Interactive charts | Plotly |
| AI Advisor chatbot | Claude API (with rule-based fallback) |
| Spending insights | Rule-based engine |

## Dataset

Place `Credit_card_transactions_-_India_-_Simple.csv` in the same directory as `app.py`.
The model trains automatically on first launch and caches to `model.pkl`.
