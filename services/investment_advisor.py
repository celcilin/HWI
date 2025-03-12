
# services/investment_advisor.py
from typing import List, Dict, Any, Optional
import random
from models.financial import InvestmentSuggestion

def generate_investment_suggestions(investable_amount: float, risk_tolerance: float) -> List[InvestmentSuggestion]:
    """
    Generate investment suggestions based on available funds and risk tolerance.
    
    Args:
        investable_amount: Amount available for investment
        risk_tolerance: 0 (low risk) to 1 (high risk)
    
    Returns:
        List of investment suggestions
    """
    suggestions = []
    
    # Define investment options based on risk profiles
    low_risk_options = [
        {
            "type": "Bond",
            "name": "Treasury Bonds",
            "expected_return": 0.03,
            "risk_level": "Low",
            "description": "Government bonds with stable returns and low risk",
            "min_investment": 100
        },
        {
            "type": "ETF",
            "name": "Short-Term Bond ETF",
            "expected_return": 0.035,
            "risk_level": "Low",
            "description": "Exchange-traded fund focusing on short-term bonds",
            "min_investment": 50
        },
        {
            "type": "Fund",
            "name": "Money Market Fund",
            "expected_return": 0.02,
            "risk_level": "Very Low",
            "description": "Liquid investments in high-quality, short-term debt",
            "min_investment": 500
        }
    ]
    
    medium_risk_options = [
        {
            "type": "ETF",
            "name": "S&P 500 Index ETF",
            "expected_return": 0.07,
            "risk_level": "Medium",
            "description": "Broad market exposure to the top 500 US companies",
            "min_investment": 100
        },
        {
            "type": "Fund",
            "name": "Balanced Mutual Fund",
            "expected_return": 0.06,
            "risk_level": "Medium",
            "description": "Mix of stocks and bonds for balanced growth and income",
            "min_investment": 1000
        },
        {
            "type": "ETF",
            "name": "Dividend Aristocrats ETF",
            "expected_return": 0.055,
            "risk_level": "Medium-Low",
            "description": "Companies with a history of increasing dividends",
            "min_investment": 200
        }
    ]
    
    high_risk_options = [
        {
            "type": "ETF",
            "name": "Technology Sector ETF",
            "expected_return": 0.12,
            "risk_level": "High",
            "description": "Exposure to high-growth technology companies",
            "min_investment": 200
        },
        {
            "type": "ETF",
            "name": "Small Cap Growth ETF",
            "expected_return": 0.10,
            "risk_level": "High",
            "description": "Small companies with high growth potential",
            "min_investment": 150
        },
        {
            "type": "Fund",
            "name": "Emerging Markets Fund",
            "expected_return": 0.11,
            "risk_level": "Very High",
            "description": "Investments in developing economies with high growth potential",
            "min_investment": 500
        }
    ]
    
    # Allocate percentages based on risk tolerance
    # Higher risk tolerance = more allocation to high risk investments
    allocations = {
        "low_risk": max(10, int(100 * (1 - risk_tolerance) * 0.7)),
        "medium_risk": max(10, int(100 * (1 - abs(risk_tolerance - 0.5) * 1.5))),
        "high_risk": max(10, int(100 * risk_tolerance * 0.7))
    }
    
    # Normalize to ensure they sum to 100
    total = sum(allocations.values())
    allocations = {k: v * 100 // total for k, v in allocations.items()}
    
    # Adjust to ensure sum is 100
    remaining = 100 - sum(allocations.values())
    if risk_tolerance < 0.33:
        allocations["low_risk"] += remaining
    elif risk_tolerance < 0.66:
        allocations["medium_risk"] += remaining
    else:
        allocations["high_risk"] += remaining
    
    # Select investment options based on allocations
    if allocations["low_risk"] > 0:
        # Choose options based on available amount
        options = [opt for opt in low_risk_options if opt["min_investment"] <= investable_amount * allocations["low_risk"] / 100]
        if options:
            selection = random.choice(options)
            suggestions.append(InvestmentSuggestion(
                type=selection["type"],
                name=selection["name"],
                allocation_percentage=allocations["low_risk"],
                expected_return=selection["expected_return"],
                risk_level=selection["risk_level"],
                description=selection["description"],
                min_investment=selection["min_investment"]
            ))
    
    if allocations["medium_risk"] > 0:
        options = [opt for opt in medium_risk_options if opt["min_investment"] <= investable_amount * allocations["medium_risk"] / 100]
        if options:
            selection = random.choice(options)
            suggestions.append(InvestmentSuggestion(
                type=selection["type"],
                name=selection["name"],
                allocation_percentage=allocations["medium_risk"],
                expected_return=selection["expected_return"],
                risk_level=selection["risk_level"],
                description=selection["description"],
                min_investment=selection["min_investment"]
            ))
    
    if allocations["high_risk"] > 0:
        options = [opt for opt in high_risk_options if opt["min_investment"] <= investable_amount * allocations["high_risk"] / 100]
        if options:
            selection = random.choice(options)
            suggestions.append(InvestmentSuggestion(
                type=selection["type"],
                name=selection["name"],
                allocation_percentage=allocations["high_risk"],
                expected_return=selection["expected_return"],
                risk_level=selection["risk_level"],
                description=selection["description"],
                min_investment=selection["min_investment"]
            ))
    
    return suggestions
