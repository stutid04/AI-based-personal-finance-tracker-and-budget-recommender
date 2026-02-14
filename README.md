💰 AI-Based Personal Finance Tracker & Budget Recommender
An intelligent personal finance management system built using Machine Learning (XGBoost) and Streamlit, designed to track income, analyze expenses, and provide AI-powered budget recommendations.

🚀 Overview
This project helps users:
Track monthly income and expenses
Visualize spending patterns
Receive AI-based budget predictions
Compare income vs expenses
Analyze category-wise expense distribution
The system uses a trained XGBoost regression model to predict a recommended budget based on user financial inputs.

🧠 Machine Learning Model
Algorithm Used: XGBoost Regressor
Model File: xgboost_budget_model.pkl

Features Used:
City
Gender
Year
Month
Expense categories (Food, Travel, Bills, Shopping, Entertainment)

Preprocessing:
One-hot encoding using pd.get_dummies()
Feature alignment with trained model columns

The model predicts an optimal monthly budget based on spending behavior patterns.
🛠️ Tech Stack
🔹 Frontend & UI

Streamlit
Custom CSS Styling
Plotly (Interactive Charts)

🔹 Backend
Python

🔹 Machine Learning
XGBoost
Scikit-learn
Pandas
NumPy
Joblib

📊 Features

🏠 Dashboard
Enter monthly financial details
View total income, total expense, and savings
Store multiple monthly records

🤖 AI Insights
Predict recommended monthly budget
Income vs Expense comparison graph
Spending alert if expense exceeds income

📈 Analytics
Category-wise expense distribution (Pie Chart)
Visual expense breakdown

Project Structure
AI-Personal-Finance-Tracker/
│
├── app.py
├── xgboost_budget_model.pkl
├── requirements.txt
├── .gitignore
└── README.md

⚙️ Installation & Setup
Step 1: Clone Repository
git clone https://github.com/yourusername/ai-personal-finance-tracker.git
cd ai-personal-finance-tracker
Step 2: Create Virtual Environment (Optional but Recommended)
python -m venv venv
venv\Scripts\activate      (Windows)
Step 3: Install Dependencies
pip install -r requirements.txt
Step 4: Run the Application
streamlit run app.py
