# app.py - Main FastAPI Application
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import pandas as pd
import numpy as np
import uvicorn
import jwt
import datetime
from passlib.context import CryptContext
import os
import io
import uuid
from pydantic import BaseModel
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from prophet import Prophet
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from dataclasses import dataclass
import logging
import json
from models.user import User, UserInDB, Token, TokenData
from models.financial import FinancialData, TransactionCategory, InvestmentSuggestion
from models.prediction import PredictionResult
from services.pdf_extractor import extract_from_pdf
from services.excel_extractor import extract_from_excel
from services.data_processor import preprocess_financial_data, categorize_transactions
from services.prediction_engine import forecast_expenses, predict_savings_potential
from services.investment_advisor import generate_investment_suggestions
from services.visualization import generate_spending_chart, generate_savings_forecast
from services.security import get_password_hash, verify_password, create_access_token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial Analysis API",
    description="API for processing financial statements and providing predictive analytics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify the actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-dev-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    # In a real app, fetch from database
    fake_users_db = {
        "testuser": {
            "username": "testuser",
            "hashed_password": get_password_hash("testpassword"),
            "email": "test@example.com"
        }
    }
    
    user = fake_users_db.get(token_data.username)
    if user is None:
        raise credentials_exception
    return UserInDB(**user)

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real app, authenticate against a database
    fake_users_db = {
        "testuser": {
            "username": "testuser",
            "hashed_password": get_password_hash("testpassword"),
            "email": "test@example.com"
        }
    }
    
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Upload endpoints
@app.post("/upload/pdf", response_model=PDFExtractResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process PDF
        result = extract_from_pdf(temp_path)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return PDFExtractResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )

@app.post("/upload/excel", response_model=FinancialData)
async def upload_excel(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Uploading Excel for user: {current_user.username}")
        contents = await file.read()
        file_id = str(uuid.uuid4())
        
        # Extract data from Excel
        raw_data = extract_from_excel(io.BytesIO(contents))
        
        # Preprocess and categorize data
        processed_data = preprocess_financial_data(raw_data)
        categorized_data = categorize_transactions(processed_data)
        
        # Save to temporary storage (in production, save to database)
        temp_path = f"temp/{file_id}.json"
        os.makedirs("temp", exist_ok=True)
        with open(temp_path, "w") as f:
            json.dump(categorized_data.dict(), f)
        
        return categorized_data
    except Exception as e:
        logger.error(f"Error processing Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# Analysis endpoints
@app.get("/analysis/spending", response_model=dict)
async def analyze_spending(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        temp_path = f"temp/{file_id}.json"
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(temp_path, "r") as f:
            data = FinancialData(**json.load(f))
        
        # Analyze spending patterns
        spending_by_category = {}
        for transaction in data.transactions:
            if transaction.category in [TransactionCategory.EXPENSE]:
                category = transaction.subcategory or "Other"
                if category not in spending_by_category:
                    spending_by_category[category] = 0
                spending_by_category[category] += transaction.amount
        
        # Generate visualization
        chart_data = generate_spending_chart(spending_by_category)
        
        return {
            "spending_by_category": spending_by_category,
            "total_spending": sum(spending_by_category.values()),
            "chart": chart_data
        }
    except Exception as e:
        logger.error(f"Error analyzing spending: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing spending: {str(e)}")

@app.get("/analysis/cashflow", response_model=dict)
async def analyze_cashflow(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        temp_path = f"temp/{file_id}.json"
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(temp_path, "r") as f:
            data = FinancialData(**json.load(f))
        
        # Organize transactions by date
        transactions_by_date = {}
        for transaction in data.transactions:
            date_str = transaction.date.strftime("%Y-%m-%d")
            if date_str not in transactions_by_date:
                transactions_by_date[date_str] = {"income": 0, "expense": 0}
            
            if transaction.category == TransactionCategory.INCOME:
                transactions_by_date[date_str]["income"] += transaction.amount
            elif transaction.category == TransactionCategory.EXPENSE:
                transactions_by_date[date_str]["expense"] += transaction.amount
        
        # Calculate net cashflow
        net_cashflow = {}
        cumulative_cashflow = 0
        for date, flows in sorted(transactions_by_date.items()):
            net = flows["income"] - flows["expense"]
            cumulative_cashflow += net
            net_cashflow[date] = {
                "income": flows["income"],
                "expense": flows["expense"],
                "net": net,
                "cumulative": cumulative_cashflow
            }
        
        return {
            "cashflow_by_date": net_cashflow,
            "total_income": sum(flow["income"] for flow in transactions_by_date.values()),
            "total_expense": sum(flow["expense"] for flow in transactions_by_date.values()),
            "net_cashflow": sum(flow["income"] - flow["expense"] for flow in transactions_by_date.values())
        }
    except Exception as e:
        logger.error(f"Error analyzing cashflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing cashflow: {str(e)}")

# Prediction endpoints
@app.get("/predict/expenses", response_model=PredictionResult)
async def predict_expenses(
    file_id: str,
    horizon_days: int = 30,
    current_user: User = Depends(get_current_user)
):
    try:
        temp_path = f"temp/{file_id}.json"
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(temp_path, "r") as f:
            data = FinancialData(**json.load(f))
        
        # Extract expense time series
        expense_df = pd.DataFrame([
            {"ds": t.date, "y": t.amount}
            for t in data.transactions
            if t.category == TransactionCategory.EXPENSE
        ])
        
        if expense_df.empty:
            raise HTTPException(status_code=400, detail="No expense data found")
        
        # Forecast using Prophet
        forecast_result = forecast_expenses(expense_df, horizon_days)
        
        return PredictionResult(
            prediction_type="expense_forecast",
            time_series=forecast_result["forecast"].to_dict(orient="records"),
            summary={
                "total_predicted": float(forecast_result["forecast"]["yhat"].sum()),
                "average_daily": float(forecast_result["forecast"]["yhat"].mean()),
                "upper_bound": float(forecast_result["forecast"]["yhat_upper"].sum()),
                "lower_bound": float(forecast_result["forecast"]["yhat_lower"].sum())
            },
            chart_data=forecast_result["chart_data"]
        )
    except Exception as e:
        logger.error(f"Error predicting expenses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error predicting expenses: {str(e)}")

@app.get("/predict/savings", response_model=PredictionResult)
async def predict_savings(
    file_id: str,
    horizon_days: int = 30,
    saving_rate: Optional[float] = None,
    current_user: User = Depends(get_current_user)
):
    try:
        temp_path = f"temp/{file_id}.json"
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(temp_path, "r") as f:
            data = FinancialData(**json.load(f))
        
        # Calculate historical income and expenses
        income_by_date = {}
        expense_by_date = {}
        
        for t in data.transactions:
            date_str = t.date.strftime("%Y-%m-%d")
            
            if t.category == TransactionCategory.INCOME:
                if date_str not in income_by_date:
                    income_by_date[date_str] = 0
                income_by_date[date_str] += t.amount
            
            elif t.category == TransactionCategory.EXPENSE:
                if date_str not in expense_by_date:
                    expense_by_date[date_str] = 0
                expense_by_date[date_str] += t.amount
        
        # Create net savings dataframe
        dates = sorted(set(list(income_by_date.keys()) + list(expense_by_date.keys())))
        savings_df = pd.DataFrame([
            {
                "ds": datetime.datetime.strptime(date, "%Y-%m-%d"),
                "y": income_by_date.get(date, 0) - expense_by_date.get(date, 0)
            }
            for date in dates
        ])
        
        if savings_df.empty:
            raise HTTPException(status_code=400, detail="Insufficient data for savings prediction")
        
        # Predict savings potential
        forecast_result = predict_savings_potential(savings_df, horizon_days, saving_rate)
        
        return PredictionResult(
            prediction_type="savings_forecast",
            time_series=forecast_result["forecast"].to_dict(orient="records"),
            summary={
                "total_predicted_savings": float(forecast_result["forecast"]["yhat"].sum()),
                "average_daily_savings": float(forecast_result["forecast"]["yhat"].mean()),
                "optimistic_scenario": float(forecast_result["forecast"]["yhat_upper"].sum()),
                "conservative_scenario": float(forecast_result["forecast"]["yhat_lower"].sum())
            },
            chart_data=forecast_result["chart_data"]
        )
    except Exception as e:
        logger.error(f"Error predicting savings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error predicting savings: {str(e)}")

# Investment endpoints
@app.get("/investment/suggestions", response_model=List[InvestmentSuggestion])
async def get_investment_suggestions(
    file_id: str,
    risk_tolerance: float = 0.5,  # 0 = low risk, 1 = high risk
    current_user: User = Depends(get_current_user)
):
    try:
        temp_path = f"temp/{file_id}.json"
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(temp_path, "r") as f:
            data = FinancialData(**json.load(f))
        
        # Calculate total income and expenses
        total_income = sum(t.amount for t in data.transactions if t.category == TransactionCategory.INCOME)
        total_expenses = sum(t.amount for t in data.transactions if t.category == TransactionCategory.EXPENSE)
        
        # Calculate investable amount
        net_cashflow = total_income - total_expenses
        investable_amount = max(0, net_cashflow * 0.3)  # Assume 30% of surplus can be invested
        
        # Generate investment suggestions
        suggestions = generate_investment_suggestions(investable_amount, risk_tolerance)
        
        return suggestions
    except Exception as e:
        logger.error(f"Error generating investment suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating investment suggestions: {str(e)}")

@app.post("/investment/auto-rules", response_model=dict)
async def set_auto_investment_rules(
    file_id: str,
    rules: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        # In a real application, save these rules to a database
        return {
            "status": "success",
            "message": "Auto-investment rules set successfully",
            "rules": rules
        }
    except Exception as e:
        logger.error(f"Error setting auto-investment rules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error setting auto-investment rules: {str(e)}")

# Dashboard endpoints
@app.get("/dashboard/summary", response_model=dict)
async def get_dashboard_summary(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        temp_path = f"temp/{file_id}.json"
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(temp_path, "r") as f:
            data = FinancialData(**json.load(f))
        
        # Calculate key metrics
        total_income = sum(t.amount for t in data.transactions if t.category == TransactionCategory.INCOME)
        total_expenses = sum(t.amount for t in data.transactions if t.category == TransactionCategory.EXPENSE)
        total_savings = sum(t.amount for t in data.transactions if t.category == TransactionCategory.SAVINGS)
        total_investments = sum(t.amount for t in data.transactions if t.category == TransactionCategory.INVESTMENT)
        
        # Calculate expense breakdown
        expense_categories = {}
        for t in data.transactions:
            if t.category == TransactionCategory.EXPENSE:
                category = t.subcategory or "Other"
                if category not in expense_categories:
                    expense_categories[category] = 0
                expense_categories[category] += t.amount
        
        # Sort categories by amount
        sorted_categories = dict(sorted(
            expense_categories.items(),
            key=lambda item: item[1],
            reverse=True
        ))
        
        # Generate recommendations
        recommendations = []
        
        # Check savings rate
        savings_rate = total_savings / total_income if total_income > 0 else 0
        if savings_rate < 0.2:
            recommendations.append("Consider increasing your savings rate to at least 20% of income.")
        
        # Check if any expense category exceeds 30% of total expenses
        for category, amount in sorted_categories.items():
            if amount / total_expenses > 0.3 and category not in ["Housing", "Mortgage"]:
                recommendations.append(f"Your spending on {category} is relatively high at {amount/total_expenses:.1%} of expenses. Consider evaluating this area for potential savings.")
        
        # Check investment allocation
        if total_investments < total_income * 0.15:
            recommendations.append("Consider allocating at least 15% of your income to investments for long-term growth.")
        
        return {
            "financial_summary": {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "total_savings": total_savings,
                "total_investments": total_investments,
                "net_cashflow": total_income - total_expenses,
                "savings_rate": savings_rate
            },
            "expense_breakdown": sorted_categories,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating dashboard summary: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)