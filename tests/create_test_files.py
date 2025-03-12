import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import os

def create_test_excel():
    # Create sample transaction data
    dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(10)]
    data = {
        'Date': dates,
        'Description': [
            'Salary Deposit',
            'Rent Payment',
            'Grocery Shopping',
            'Internet Bill',
            'Investment Transfer',
            'Restaurant Dinner',
            'Gas Station',
            'Online Shopping',
            'Medical Expense',
            'Savings Transfer'
        ],
        'Amount': [
            5000.00,
            -1500.00,
            -200.50,
            -80.00,
            -1000.00,
            -75.30,
            -45.00,
            -120.75,
            -250.00,
            -500.00
        ]
    }
    
    df = pd.DataFrame(data)
    excel_path = os.path.join('tests', 'test_data', 'test_transactions.xlsx')
    df.to_excel(excel_path, index=False)
    print(f"Created test Excel file: {excel_path}")

def create_test_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add header
    pdf.cell(200, 10, txt="Bank Statement", ln=1, align='C')
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=1, align='C')
    
    # Add transactions
    pdf.cell(200, 10, txt="Transaction Details:", ln=1, align='L')
    transactions = [
        ['2024-03-01', 'Salary Deposit', '5000.00'],
        ['2024-03-02', 'Rent Payment', '-1500.00'],
        ['2024-03-03', 'Grocery Shopping', '-200.50'],
        ['2024-03-04', 'Internet Bill', '-80.00'],
        ['2024-03-05', 'Investment Transfer', '-1000.00']
    ]
    
    for date, desc, amount in transactions:
        pdf.cell(50, 10, txt=date, border=1)
        pdf.cell(90, 10, txt=desc, border=1)
        pdf.cell(50, 10, txt=amount, border=1, ln=1)
    
    pdf_path = os.path.join('tests', 'test_data', 'test_statement.pdf')
    pdf.output(pdf_path)
    print(f"Created test PDF file: {pdf_path}")

if __name__ == "__main__":
    # Create test files
    create_test_excel()
    create_test_pdf()