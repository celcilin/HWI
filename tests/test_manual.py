import requests
import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {"username": "testuser", "password": "testpassword"}
console = Console()

def print_response(response, title="Response"):
    """Pretty print response"""
    console.print(f"\n[bold blue]{title}[/bold blue]")
    try:
        console.print_json(json.dumps(response.json()))
    except:
        console.print(response.text)
    console.print(f"Status Code: {response.status_code}")

def test_auth():
    """Test authentication endpoints"""
    console.print("\n[bold green]Testing Authentication[/bold green]")
    
    # Test login
    response = requests.post(
        f"{BASE_URL}/token",
        data=TEST_USER
    )
    print_response(response, "Login Response")
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_file_upload(token):
    """Test file upload endpoints"""
    console.print("\n[bold green]Testing File Uploads[/bold green]")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test Excel upload
    excel_path = "tests/test_data/test_transactions.xlsx"
    if os.path.exists(excel_path):
        with open(excel_path, "rb") as f:
            response = requests.post(
                f"{BASE_URL}/upload/excel",
                files={"file": ("test_transactions.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                headers=headers
            )
        print_response(response, "Excel Upload Response")
        
        if response.status_code == 200:
            return response.json().get("file_id")
    else:
        console.print("[red]Excel test file not found![/red]")
    return None

def test_analysis(token, file_id):
    """Test analysis endpoints"""
    console.print("\n[bold green]Testing Analysis Endpoints[/bold green]")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test transaction summary
    response = requests.get(
        f"{BASE_URL}/analysis/summary/{file_id}",
        headers=headers
    )
    print_response(response, "Transaction Summary")
    
    # Test spending analysis
    response = requests.get(
        f"{BASE_URL}/analysis/spending/{file_id}",
        headers=headers
    )
    print_response(response, "Spending Analysis")

def main():
    """Run all manual tests"""
    console.print("[bold yellow]Starting Manual Tests[/bold yellow]")
    
    # Test authentication
    token = test_auth()
    if not token:
        console.print("[red]Authentication failed! Stopping tests.[/red]")
        return
    
    # Test file upload
    file_id = test_file_upload(token)
    if not file_id:
        console.print("[red]File upload failed! Stopping tests.[/red]")
        return
    
    # Test analysis endpoints
    test_analysis(token, file_id)
    
    console.print("\n[bold green]Manual Tests Completed![/bold green]")

if __name__ == "__main__":
    main()