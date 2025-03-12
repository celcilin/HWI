import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import os

def create_test_data():
    """Create realistic bank transaction data"""
    dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(25)]
    data = {
        'Date': dates,
        'Description': [
            'Salary Deposit - ABC Corp',
            'Rent Payment',
            'Walmart Groceries',
            'Netflix Subscription',
            'Amazon Purchase',
            'Electric Bill - Power Co',
            'Restaurant - Burger King',
            'Gas Station - Shell',
            'Internet Bill - Comcast',
            'Phone Bill - Verizon',
            'Transfer to Savings',
            'Target Shopping',
            'CVS Pharmacy',
            'Starbucks Coffee',
            'Gym Membership',
            'Insurance Premium',
            'Water Bill',
            'Car Payment - Toyota',
            'Home Depot Purchase',
            'Pet Store - PetSmart',
            'Doctor Visit Copay',
            'Movie Tickets - AMC',
            'Spotify Premium',
            'ATM Withdrawal',
            'Investment Transfer'
        ],
        'Amount': [
            5000.00,   # Salary
            -1500.00,  # Rent
            -225.50,   # Groceries
            -15.99,    # Netflix
            -156.73,   # Amazon
            -145.20,   # Electric
            -25.46,    # Restaurant
            -45.00,    # Gas
            -89.99,    # Internet
            -75.00,    # Phone
            -500.00,   # Savings
            -189.52,   # Target
            -43.27,    # CVS
            -5.75,     # Starbucks
            -50.00,    # Gym
            -125.00,   # Insurance
            -78.34,    # Water
            -450.00,   # Car Payment
            -234.56,   # Home Depot
            -89.27,    # Pet Store
            -40.00,    # Doctor
            -32.50,    # Movie
            -9.99,     # Spotify
            -100.00,   # ATM
            -1000.00   # Investment
        ]
    }
    return pd.DataFrame(data)

def create_test_excel():
    """Create test Excel file"""
    df = create_test_data()
    excel_path = os.path.join('m_tests', 'test_data', 'test_transactions.xlsx')
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    df.to_excel(excel_path, index=False)
    return excel_path

def create_test_pdf():
    """Create test PDF file with bank statement format"""
    df = create_test_data()
    pdf = FPDF()
    pdf.add_page('L')  # Landscape orientation for better table layout
    
    # Set up fonts
    pdf.set_font("Arial", "B", 16)
    
    # Add bank header
    pdf.cell(0, 10, "Example Bank Statement", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Statement Period: {df['Date'].min()} to {df['Date'].max()}", ln=True, align='C')
    pdf.ln(10)
    
    # Add column headers with fixed widths
    pdf.set_font("Arial", "B", 12)
    col_widths = [40, 150, 40]  # Width for Date, Description, Amount
    headers = ['Date', 'Description', 'Amount']
    
    for width, header in zip(col_widths, headers):
        pdf.cell(width, 10, header, border=1)
    pdf.ln()
    
    # Add transactions with proper formatting
    pdf.set_font("Arial", "", 10)
    for _, row in df.iterrows():
        amount = float(row['Amount'])
        amount_str = f"${amount:,.2f}"
        
        pdf.cell(col_widths[0], 10, str(row['Date']), border=1)
        pdf.cell(col_widths[1], 10, str(row['Description']), border=1)
        pdf.cell(col_widths[2], 10, amount_str, border=1)
        pdf.ln()
    
    # Save PDF
    pdf_path = os.path.join('m_tests', 'test_data', 'test_statement.pdf')
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    pdf.output(pdf_path)
    return pdf_path

if __name__ == "__main__":
    excel_file = create_test_excel()
    pdf_file = create_test_pdf()
    print(f"Created test files:\nExcel: {excel_file}\nPDF: {pdf_file}")
    print("\nTest files created successfully!")