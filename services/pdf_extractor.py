import tabula
import pandas as pd
import uuid
from typing import List, Dict, Any
from datetime import datetime
from models.financial import TransactionCategory, PDFTransaction

def extract_from_pdf(file_path: str) -> Dict[str, Any]:
    try:
        # Read tables from PDF
        tables = tabula.read_pdf(file_path, pages='all')
        
        if not tables:
            raise ValueError("No tables found in PDF")
        
        # Process first table found
        df = tables[0]
        
        # Expected columns: Date, Description, Amount
        required_columns = ['Date', 'Description', 'Amount']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"PDF must contain columns: {', '.join(required_columns)}")
        
        # Convert DataFrame to list of transactions
        transactions = []
        for _, row in df.iterrows():
            try:
                # Convert date string to standard format
                date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
                
                # Clean and convert amount
                amount_str = str(row['Amount']).replace('$', '').replace(',', '')
                amount = float(amount_str)
                
                # Create transaction
                transaction = PDFTransaction(
                    date=date_str,
                    description=str(row['Description']).strip(),
                    amount=amount,
                    category=TransactionCategory.EXPENSE if amount < 0 else TransactionCategory.INCOME,
                    tags=[]
                )
                transactions.append(transaction.dict())
            except Exception as e:
                continue
        
        return {
            "file_id": str(uuid.uuid4()),
            "transactions": transactions,
            "metadata": {
                "source": "pdf",
                "processed_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "total_transactions": len(transactions)
            }
        }
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")