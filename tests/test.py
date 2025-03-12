from fastapi.testclient import TestClient
from main import app
import pytest
import pandas as pd
import os
from datetime import datetime

from models.financial import TransactionCategory

# Initialize test client
client = TestClient(app)

@pytest.fixture
def test_token():
    """Fixture to get authentication token"""
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    return response.json()["access_token"]

@pytest.fixture
def test_excel_file():
    """Fixture to create test Excel file"""
    excel_path = "tests/test_data/bank.xlsx"
    
    # Create sample financial data
    today = datetime.now().strftime('%Y-%m-%d')
    data = {
        'Date': [today] * 3,
        'Description': ['Salary', 'Rent Payment', 'Groceries'],
        'Amount': [5000.00, -1500.00, -200.00]
    }
    df = pd.DataFrame(data)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    
    # Save to Excel
    df.to_excel(excel_path, index=False)
    return excel_path

@pytest.fixture
def test_files():
    """Fixture to get test file paths"""
    return {
        'excel': os.path.join('tests', 'test_data', 'test_transactions.xlsx'),
        'pdf': os.path.join('tests', 'test_data', 'test_statement.pdf')
    }

def test_login():
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_upload_excel(test_token, test_files):
    with open(test_files['excel'], "rb") as f:
        files = {"file": ("test_transactions.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        headers = {"Authorization": f"Bearer {test_token}"}
        response = client.post("/upload/excel", files=files, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert len(data["transactions"]) > 0

def test_upload_pdf(test_token, test_files):
    with open(test_files['pdf'], "rb") as f:
        files = {"file": ("test_statement.pdf", f, "application/pdf")}
        headers = {"Authorization": f"Bearer {test_token}"}
        response = client.post("/upload/pdf", files=files, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert len(data["transactions"]) > 0

def test_upload_excel(test_token, test_excel_file):
    with open(test_excel_file, "rb") as f:
        files = {"file": ("bank.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        headers = {"Authorization": f"Bearer {test_token}"}
        response = client.post("/upload/excel", files=files, headers=headers)
    
    assert response.status_code == 200, f"Error: {response.text}"
    data = response.json()
    assert "transactions" in data
    assert len(data["transactions"]) > 0
    
    # Test that transactions were properly categorized
    transactions = data["transactions"]
    assert any(t["category"] == TransactionCategory.INCOME.value for t in transactions)
    assert any(t["category"] == TransactionCategory.EXPENSE.value for t in transactions)

    # Verify data types
    for transaction in transactions:
        assert isinstance(transaction["date"], str)
        assert isinstance(transaction["amount"], (int, float))
        assert isinstance(transaction["description"], str)