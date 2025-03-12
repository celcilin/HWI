import requests
import json
import os
from datetime import datetime
from rich.console import Console
from create_test_files import create_test_excel, create_test_pdf

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {"username": "testuser", "password": "testpassword"}
console = Console()

def test_file_upload():
    """Test file upload endpoints"""
    console.print("\n[bold green]Testing File Uploads[/bold green]")
    
    # Login first
    response = requests.post(f"{BASE_URL}/token", data=TEST_USER)
    if response.status_code != 200:
        console.print("[red]Login failed![/red]")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test files
    excel_path = create_test_excel()
    pdf_path = create_test_pdf()
    
    # Test Excel upload
    with open(excel_path, "rb") as f:
        files = {"file": ("test_transactions.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = requests.post(
            f"{BASE_URL}/upload/excel",
            files=files,
            headers=headers
        )
        console.print("\n[bold blue]Excel Upload Response:[/bold blue]")
        console.print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            console.print_json(json.dumps(response.json()))
        else:
            console.print(f"[red]Error: {response.text}[/red]")
    
    # Test PDF upload
    with open(pdf_path, "rb") as f:
        files = {"file": ("test_statement.pdf", f, "application/pdf")}
        response = requests.post(
            f"{BASE_URL}/upload/pdf",
            files=files,
            headers=headers
        )
        console.print("\n[bold blue]PDF Upload Response:[/bold blue]")
        console.print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            console.print_json(json.dumps(response.json()))
        else:
            console.print(f"[red]Error: {response.text}[/red]")

if __name__ == "__main__":
    test_file_upload()