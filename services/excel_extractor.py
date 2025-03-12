# services/excel_extractor.py
import io
import pandas as pd
import uuid
from datetime import datetime
from typing import List, Dict, Any, BinaryIO
from models.financial import TransactionCategory

def extract_from_excel(file: BinaryIO) -> List[Dict[str, Any]]:
    try:
        # Read Excel file
        df = pd.read_excel(file)
        
        # Convert DataFrame to transactions
        transactions = []
        for _, row in df.iterrows():
            try:
                # Convert Timestamp to string format
                date = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
                
                amount = float(row['Amount'])
                description = str(row['Description'])
                
                # Determine category based on amount
                category = TransactionCategory.EXPENSE if amount < 0 else TransactionCategory.INCOME
                
                transactions.append({
                    "id": str(uuid.uuid4()),
                    "date": date,  # Now a string in YYYY-MM-DD format
                    "description": description.strip(),
                    "amount": abs(amount),
                    "category": category,
                    "subcategory": None,
                    "tags": []
                })
            except Exception as e:
                continue
                
        return transactions
    except Exception as e:
        raise Exception(f"Failed to extract data from Excel: {str(e)}")
