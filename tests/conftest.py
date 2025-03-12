import pytest
import os
import sys
from fastapi.testclient import TestClient

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)