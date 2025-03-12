
# services/data_processor.py
import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any
from models.financial import FinancialData, Transaction, TransactionCategory
import uuid

def preprocess_financial_data(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Preprocess raw financial data:
    - Handle missing values
    - Normalize date formats
    - Standardize amounts
    - Remove duplicates
    - Detect and flag anomalies
    """
    if not raw_data:
        return []
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(raw_data)
    
    # Handle missing values
    if 'description' in df.columns:
        df['description'] = df['description'].fillna('Unknown Transaction')
    
    if 'amount' in df.columns:
        # Flag potential anomalies (amounts significantly larger than average)
        mean_amount = df['amount'].mean()
        std_amount = df['amount'].std()
        threshold = mean_amount + 3 * std_amount
        
        anomalies = df[df['amount'] > threshold]
        for idx, row in anomalies.iterrows():
            df.loc[idx, 'tags'] = df.loc[idx, 'tags'] + ['potential_anomaly'] if isinstance(df.loc[idx, 'tags'], list) else ['potential_anomaly']
    
    # Remove duplicates
    if 'date' in df.columns and 'amount' in df.columns and 'description' in df.columns:
        df = df.drop_duplicates(subset=['date', 'amount', 'description'])
    
    # Ensure all transactions have IDs
    if 'id' not in df.columns:
        df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    
    # Convert back to list of dicts
    return df.to_dict('records')

def categorize_transactions(transactions: List[Dict[str, Any]]) -> FinancialData:
    """
    Categorize transactions into income, expenses, savings, investments, etc.
    Apply machine learning or rule-based approaches to determine subcategories.
    """
    # Keywords for categorization
    category_keywords = {
        TransactionCategory.INCOME: [
            'salary', 'deposit', 'payroll', 'interest', 'dividend', 'refund', 'reimbursement',
            'payment received', 'income', 'revenue', 'wage', 'bonus', 'commission'
        ],
        TransactionCategory.EXPENSE: [
            'payment', 'purchase', 'bill', 'withdrawal', 'fee', 'charge', 'subscription',
            'restaurant', 'food', 'grocery', 'transport', 'uber', 'taxi', 'shopping'
        ],
        TransactionCategory.SAVINGS: [
            'saving', 'transfer to savings', 'reserve', 'emergency fund'
        ],
        TransactionCategory.INVESTMENT: [
            'investment', 'stock', 'bond', 'etf', 'mutual fund', 'brokerage', '401k', 'ira', 'roth'
        ],
        TransactionCategory.TRANSFER: [
            'transfer', 'zelle', 'venmo', 'paypal', 'wire', 'ach'
        ]
    }
    
    # Subcategory keywords
    subcategory_keywords = {
        'Housing': ['rent', 'mortgage', 'property tax', 'hoa', 'maintenance', 'repair'],
        'Utilities': ['electricity', 'water', 'gas', 'internet', 'phone', 'cable', 'utility'],
        'Food': ['grocery', 'restaurant', 'meal', 'doordash', 'uber eats', 'dining'],
        'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'public transport', 'car', 'auto', 'vehicle'],
        'Healthcare': ['medical', 'doctor', 'hospital', 'pharmacy', 'prescription', 'health', 'dental', 'vision'],
        'Entertainment': ['movie', 'theatre', 'concert', 'subscription', 'netflix', 'spotify', 'game'],
        'Shopping': ['amazon', 'walmart', 'target', 'store', 'mall', 'clothing', 'electronics'],
        'Education': ['tuition', 'book', 'course', 'class', 'school', 'university', 'college', 'student'],
        'Personal': ['haircut', 'salon', 'spa', 'gym', 'fitness'],
        'Travel': ['hotel', 'flight', 'airbnb', 'vacation', 'trip', 'airline', 'booking'],
        'Insurance': ['insurance', 'premium', 'coverage', 'policy'],
        'Debt': ['loan', 'credit card', 'interest', 'debt', 'payment'],
        'Salary': ['salary', 'payroll', 'wage', 'income', 'earnings'],
        'Investment': ['dividend', 'capital gain', 'interest', 'stock', 'bond', 'etf', 'mutual fund'],
        'Savings': ['savings', 'deposit', 'emergency fund'],
        'Gift': ['gift', 'donation', 'charity']
    }
    
    for transaction in transactions:
        # Default category if nothing matches
        if 'category' not in transaction or transaction['category'] is None:
            transaction['category'] = TransactionCategory.OTHER
        
        # Try to determine category based on description
        description = transaction.get('description', '').lower()
        
        for category, keywords in category_keywords.items():
            if any(keyword in description for keyword in keywords):
                transaction['category'] = category
                break
        
        # Determine subcategory
        for subcategory, keywords in subcategory_keywords.items():
            if any(keyword in description for keyword in keywords):
                transaction['subcategory'] = subcategory
                break
        
        # If no subcategory was found, use a generic one based on the category
        if 'subcategory' not in transaction or transaction['subcategory'] is None:
            if transaction['category'] == TransactionCategory.INCOME:
                transaction['subcategory'] = 'Other Income'
            elif transaction['category'] == TransactionCategory.EXPENSE:
                transaction['subcategory'] = 'Other Expense'
            elif transaction['category'] == TransactionCategory.SAVINGS:
                transaction['subcategory'] = 'General Savings'
            elif transaction['category'] == TransactionCategory.INVESTMENT:
                transaction['subcategory'] = 'General Investment'
            else:
                transaction['subcategory'] = 'Uncategorized'
        
        # Ensure tags is a list
        if 'tags' not in transaction or transaction['tags'] is None:
            transaction['tags'] = []
        
        # Initialize metadata if not present
        if 'metadata' not in transaction:
            transaction['metadata'] = {}
    
    # Create FinancialData object
    financial_data = FinancialData(
        file_id=str(uuid.uuid4()),
        transactions=transactions,
        summary={
            'total_income': sum(t['amount'] for t in transactions if t['category'] == TransactionCategory.INCOME),
            'total_expenses': sum(t['amount'] for t in transactions if t['category'] == TransactionCategory.EXPENSE),
            'total_savings': sum(t['amount'] for t in transactions if t['category'] == TransactionCategory.SAVINGS),
            'total_investments': sum(t['amount'] for t in transactions if t['category'] == TransactionCategory.INVESTMENT)
        }
    )
    
    return financial_data
