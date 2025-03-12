from rich.console import Console
import requests
import datetime
import json
import os
import tabula
from datetime import datetime, timedelta
from create_test_files import create_test_pdf

class FinancialAPITester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.console = Console()
        self.token = None
        self.file_id = None
        self.test_user = {"username": "testuser", "password": "testpassword"}

    def print_test(self, title, response):
        """Print test results in color"""
        self.console.print(f"\n[bold blue]{title}[/bold blue]")
        self.console.print(f"Status: [{'green' if response.status_code == 200 else 'red'}]{response.status_code}[/]")
        try:
            self.console.print_json(json.dumps(response.json(), indent=2))
        except:
            self.console.print(response.text)

    def test_auth(self):
        """Test authentication"""
        self.console.print("\n[bold cyan]1. Testing Authentication[/bold cyan]")
        response = requests.post(
            f"{self.base_url}/token",
            data=self.test_user
        )
        self.print_test("Authentication", response)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        return False

    def test_pdf_upload(self):
        """Test PDF upload and processing"""
        self.console.print("\n[bold cyan]2. Testing PDF Upload[/bold cyan]")
        headers = {"Authorization": f"Bearer {self.token}"}

        # Generate and upload PDF
        try:
            pdf_path = create_test_pdf()
            with open(pdf_path, "rb") as f:
                response = requests.post(
                    f"{self.base_url}/upload/pdf",
                    files={"file": ("test_statement.pdf", f, "application/pdf")},
                    headers=headers
                )
            self.print_test("PDF Upload and Processing", response)
            
            if response.status_code == 200:
                data = response.json()
                self.file_id = data.get("file_id")
                
                # Verify transaction data
                if "transactions" in data:
                    for trans in data["transactions"]:
                        # Verify date format
                        datetime.strptime(trans["date"], '%Y-%m-%d')
                        # Verify numeric amount
                        assert isinstance(trans["amount"], (int, float))
                        
                return True
            return False
        except Exception as e:
            self.console.print(f"[bold red]Error during PDF upload: {str(e)}[/bold red]")
            return False

    def test_analysis(self):
        """Test analysis endpoints with uploaded PDF data"""
        self.console.print("\n[bold cyan]3. Testing Analysis[/bold cyan]")
        headers = {"Authorization": f"Bearer {self.token}"}
        # Test transaction summary
        response = requests.get(
            f"{self.base_url}/analysis/summary/{self.file_id}",
            headers=headers
        )
        self.print_test("Transaction Summary", response)
        # Test spending patterns
        response = requests.get(
            f"{self.base_url}/analysis/spending/{self.file_id}",
            headers=headers
        )
        self.print_test("Spending Analysis", response)

    def test_predictions(self):
        """Test prediction endpoints"""
        self.console.print("\n[bold cyan]4. Testing Predictions[/bold cyan]")
        headers = {"Authorization": f"Bearer {self.token}"}
        # Test expense forecasting
        response = requests.get(
            f"{self.base_url}/predict/expenses/{self.file_id}",
            params={"months": 3},
            headers=headers
        )
        self.print_test("Expense Forecast", response)

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.console.print("[bold green]Starting PDF Processing Tests[/bold green]")
        if not self.test_auth():
            self.console.print("[bold red]❌ Authentication failed![/bold red]")
            return
        if not self.test_pdf_upload():
            self.console.print("[bold red]❌ PDF upload failed![/bold red]")
            return
        self.test_analysis()
        self.test_predictions()
        self.console.print("\n[bold green]✓ All tests completed![/bold green]")

if __name__ == "__main__":
    def main():
        try:
            requests.get("http://localhost:8000")
        except requests.exceptions.ConnectionError:
            print("Error: FastAPI server is not running!")
            print("Start the server with: uvicorn main:app --reload")
            return

        tester = FinancialAPITester()
        tester.run_all_tests()

    main()