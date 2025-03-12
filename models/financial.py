# models/financial.py
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime

class TransactionCategory(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    SAVINGS = "savings"
    INVESTMENT = "investment"
    TRANSFER = "transfer"
    OTHER = "other"

class Transaction(BaseModel):
    id: str
    date: datetime
    description: str
    amount: float
    category: TransactionCategory
    subcategory: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class PDFTransaction(BaseModel):
    date: str
    description: str
    amount: float
    category: Optional[TransactionCategory] = TransactionCategory.OTHER
    tags: Optional[List[str]] = []

class PDFExtractResponse(BaseModel):
    file_id: str
    transactions: List[PDFTransaction]
    metadata: Optional[Dict[str, Any]] = {}

class FinancialData(BaseModel):
    user_id: Optional[str] = None
    file_id: str
    transactions: List[Transaction]
    summary: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    
class InvestmentSuggestion(BaseModel):
    type: str
    name: str
    allocation_percentage: float
    expected_return: float
    risk_level: str
    description: str
    min_investment: Optional[float] = None

