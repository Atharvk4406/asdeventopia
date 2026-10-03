import json
import pytest
from app import app
from ml_chatbot import predict_intent

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_route(client):
    """Test login route returns 200 OK."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Eventopia' in response.data or b'Login' in response.data or b'login' in response.data

def test_register_route(client):
    """Test register route returns 200 OK."""
    response = client.get('/register')
    assert response.status_code == 200

def test_health_route(client):
    """Test health check route for DevOps monitoring."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert data['service'] == 'AI Event Management System'

def test_info_route(client):
    """Test system metadata API endpoint."""
    response = client.get('/api/info')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'devops_stack' in data
    assert 'Jira' in data['devops_stack']

def test_ml_chatbot_intent():
    """Test ML chatbot intent classification."""
    intent, confidence = predict_intent("What events are happening?")
    assert isinstance(intent, str)
    assert confidence >= 0.0
