from fastapi.testclient import TestClient
from main import app
from starlette import status

client = TestClient(app)

def test_health_check():
    response = client.get('/')
    assert response.json() == {'Health Status':'Alive'}
    assert response.status_code == status.HTTP_200_OK