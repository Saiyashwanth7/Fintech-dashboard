import pytest
from main import app
from routers.auth import get_current_user
from starlette import status
from models import Users,FinancialRecords

def override_as_admin():
    return {'email': 'admin@gmail.com', 'id': 1, 'role': 'admin'}

@pytest.fixture(autouse=True)
def set_override():
    app.dependency_overrides[get_current_user] = override_as_admin
    yield
    app.dependency_overrides.pop(get_current_user, None)  # clean up after each test

# Testing User.py API end points
def test_my_profile(client, admin_as_user):
    response = client.get('/users/me')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == 'admin@gmail.com'
    assert response.json()['role'] == 'admin'

def test_read_all_user(client, admin_as_user):
    response = client.get('/users/')
    assert response.status_code == status.HTTP_200_OK
    
def test_read_by_user_id(client,admin_as_user):
    response = client.get('/users/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == 'admin@gmail.com'
    
def test_read_by_user_id_404(client,admin_as_user):
    response = client.get('/users/99999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
def test_update_user(client,admin_as_user,db):
    request_data = {
        'name' : 'testing_user',
        'email' : 'testinguser@gmail.com',
        'role' : 'viewer'
    }
    response = client.put('/users/1',json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    user_model = db.query(Users).filter(Users.id == 1).first()
    assert user_model.email == 'testinguser@gmail.com'

# Testing finance.py API end points
def test_create_transaction(client,admin_as_user,db):
    record = {
        'amount' : 100000,
        'type' : 'income',
        'category' : 'salary',
        'date': '2026-04-05',
        'notes' : ''
    }
    response = client.post('/records/',json=record)
    assert response.status_code == status.HTTP_201_CREATED

def test_delete_record(client,admin_as_user,sample_records,db):
    response = client.delete('/records/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    record = db.query(FinancialRecords).filter(FinancialRecords.id == 1).first()
    assert record.is_deleted == True
    
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