
# services/prediction_engine.py
import pandas as pd
import numpy as np
from typing import Dict, Any
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import plotly.graph_objects as go
import json

def forecast_expenses(expense_df: pd.DataFrame, horizon_days: int = 30) -> Dict[str, Any]:
    """
    Forecast future expenses using Prophet time series model
    """
    # Ensure DataFrame has required columns
    if 'ds' not in expense_df.columns or 'y' not in expense_df.columns:
        raise ValueError("DataFrame must have 'ds' (date) and 'y' (value) columns")
    
    # Group by date if there are multiple transactions per day
    daily_expenses = expense_df.groupby('ds')['y'].sum().reset_index()
    
    # Create and fit Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )
    
    model.fit(daily_expenses)
    
    # Create future dataframe for prediction
    future = model.make_future_dataframe(periods=horizon_days)
    
    # Make predictions
    forecast = model.predict(future)
    
    # Create visualization data
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=daily_expenses['ds'],
        y=daily_expenses['y'],
        mode='markers',
        name='Historical Expenses',
        marker=dict(color='blue', size=8)
    ))
    
    # Forecast line
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color='red', width=2)
    ))
    
    # Uncertainty interval
    fig.add_trace(go.Scatter(
        x=forecast['ds'].tolist() + forecast['ds'].iloc[::-1].tolist(),
        y=forecast['yhat_upper'].tolist() + forecast['yhat_lower'].iloc[::-1].tolist(),
        fill='toself',
        fillcolor='rgba(255,0,0,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Uncertainty Interval'
    ))
    
    fig.update_layout(
        title='Expense Forecast',
        xaxis_title='Date',
        yaxis_title='Amount',
        template='plotly_white'
    )
    
    # Convert figure to JSON for API response
    chart_data = json.loads(fig.to_json())
    
    return {
        "forecast": forecast,
        "chart_data": chart_data
    }

def predict_savings_potential(savings_df: pd.DataFrame, horizon_days: int = 30, saving_rate: float = None) -> Dict[str, Any]:
    """
    Predict potential savings based on historical data and optional saving rate
    """
    # Ensure DataFrame has required columns
    if 'ds' not in savings_df.columns or 'y' not in savings_df.columns:
        raise ValueError("DataFrame must have 'ds' (date) and 'y' (value) columns")
    
    # Group by date if there are multiple transactions per day
    daily_savings = savings_df.groupby('ds')['y'].sum().reset_index()
    
    # If saving rate is provided, adjust the historical data
    if saving_rate is not None:
        # Calculate average daily savings
        avg_daily_savings = daily_savings['y'].mean()
        
        # Calculate the adjustment factor
        adjustment_factor = saving_rate / (avg_daily_savings / daily_savings['y'].abs().mean())
        
        # Adjust historical data
        daily_savings['y'] = daily_savings['y'] * adjustment_factor
    
    # Create and fit Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05  # More flexible trend changes
    )
    
    model.fit(daily_savings)
    
    # Create future dataframe for prediction
    future = model.make_future_dataframe(periods=horizon_days)
    
    # Make predictions
    forecast = model.predict(future)
    
    # Create visualization data
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=daily_savings['ds'],
        y=daily_savings['y'].cumsum(),
        mode='lines+markers',
        name='Historical Cumulative Savings',
        marker=dict(color='blue', size=6)
    ))
    
    # Forecast line (cumulative)
    future_dates = forecast['ds'].iloc[-horizon_days:]
    future_values = forecast['yhat'].iloc[-horizon_days:]
    
    # Calculate cumulative savings projection
    last_cumulative = daily_savings['y'].cumsum().iloc[-1] if not daily_savings.empty else 0
    cumulative_forecast = [last_cumulative]
    
    for val in future_values:
        cumulative_forecast.append(cumulative_forecast[-1] + val)
    
    cumulative_forecast = cumulative_forecast[1:]  # Remove the initial value
    
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=cumulative_forecast,
        mode='lines',
        name='Projected Cumulative Savings',
        line=dict(color='green', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title='Savings Projection',
        xaxis_title='Date',
        yaxis_title='Cumulative Amount',
        template='plotly_white'
    )
    
    # Convert figure to JSON for API response
    chart_data = json.loads(fig.to_json())
    
    return {
        "forecast": forecast,
        "chart_data": chart_data
    }
