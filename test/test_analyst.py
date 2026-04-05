from main import app
from routers.auth import get_current_user
from starlette import status
import pytest
from models import FinancialRecords

def override_as_analyst(): #analyst as the user
    return {'email':'analyst@gmail.com','id':1,'role':'analyst'}


@pytest.fixture(autouse=True)
def set_override():
    app.dependency_overrides[get_current_user] = override_as_analyst
    yield
    app.dependency_overrides.pop(get_current_user, None)  

# Testing user.py API end points
def test_my_profile(client,analyst_as_user):   # fixture passed as argument
    response = client.get('/users/me')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == 'analyst@gmail.com'
    
def test_read_all_user(client,analyst_as_user):
    response = client.get('/users/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_read_by_user_id(client,analyst_as_user):
    response = client.get('/users/1')
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Testing finance.py API end points
def test_create_transaction(client,analyst_as_user,db):
    record = {
        'amount' : 100000,
        'type' : 'income',
        'category' : 'salary',
        'date': '2026-04-05',
        'notes' : ''
    }
    response = client.post('/records/',json=record)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_record(client,analyst_as_user,db):
    response = client.delete('/records/1')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
# Testing dashboard.py API end points

def test_dashboard_summary(client,sample_records):
    respone = client.get('/dashboard/')
    assert respone.status_code == status.HTTP_200_OK
    data=respone.json()
    assert data['total income']==128000
    assert data['total expense'] == 7800
    assert data['net balance'] == 120200
    
def test_dashboard_by_category(client,sample_records):
    response = client.get('/dashboard/by-category')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['food']['expense'] == 5000
    assert response.json()['salary']['income'] == 100000
    assert response.json()['stocks']['income'] == 28000
    assert response.json()['air fryer']['expense'] == 2800
    
def test_dashboard_trends(client,sample_records):
    response = client.get('/dashboard/trends')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["2026-04"]['income']==128000

def test_dashboard_recents(client,sample_records):
    respone = client.get('/dashboard/recents')
    assert respone.status_code == status.HTTP_200_OK