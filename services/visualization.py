
# services/visualization.py
from typing import Dict, Any
import plotly.express as px
import plotly.graph_objects as go
import json

def generate_spending_chart(spending_by_category: Dict[str, float]) -> Dict[str, Any]:
    """Generate a pie chart for spending by category"""
    # Create pie chart
    fig = px.pie(
        values=list(spending_by_category.values()),
        names=list(spending_by_category.keys()),
        title="Spending by Category",
        color_discrete_sequence=px.colors.sequential.Blues
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    
    # Convert to JSON for API response
    return json.loads(fig.to_json())

def generate_savings_forecast(historical_data: Dict[str, float], forecast_data: Dict[str, float]) -> Dict[str, Any]:
    """Generate a line chart for historical and forecasted savings"""
    fig = go.Figure()
    
    # Historical data
    historical_dates = list(historical_data.keys())
    historical_values = list(historical_data.values())
    
    fig.add_trace(go.Scatter(
        x=historical_dates,
        y=historical_values,
        mode='lines+markers',
        name='Historical Savings',
        line=dict(color='blue', width=2)
    ))
    
    # Forecast data
    forecast_dates = list(forecast_data.keys())
    forecast_values = list(forecast_data.values())
    
    fig.add_trace(go.Scatter(
        x=forecast_dates,
        y=forecast_values,
        mode='lines',
        name='Forecasted Savings',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title='Savings Forecast',
        xaxis_title='Date',
        yaxis_title='Amount',
        legend_title='Data Type',
        template='plotly_white'
    )
    
    # Convert to JSON for API response
    return json.loads(fig.to_json())
