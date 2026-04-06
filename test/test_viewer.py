from main import app
from routers.auth import get_current_user
from starlette import status
import pytest

def override_as_viewer(): #Viewer as the user
    return {'email':'viewer@gmail.com','id':1,'role':'viewer'}

@pytest.fixture(autouse=True) #Here, autouse will automatically let all the test functions in this file use the set_override as one of its argument
def set_override():
    app.dependency_overrides[get_current_user] = override_as_viewer
    yield # 
    app.dependency_overrides.pop(get_current_user, None)  

#Testing users.py API end points
def test_my_profile(client,viewer_as_user):
    response = client.get('/users/me')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == 'viewer@gmail.com'
    
def test_read_all_user(client,viewer_as_user):
    response = client.get('/users/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_read_by_user_id(client,viewer_as_user):
    response = client.get('/users/1')
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Testing finance.py API end points

def test_read_all_records(client, viewer_as_user):
    response = client.get('/records/')
    assert response.status_code == status.HTTP_200_OK
    
    
def test_create_transaction(client,viewer_as_user,db):
    record = {
        'amount' : 100000,
        'type' : 'income',
        'category' : 'salary',
        'date': '2026-04-05',
        'notes' : ''
    }
    response = client.post('/records/',json=record)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_record(client,viewer_as_user,db):
    response = client.delete('/records/1')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
# Testing dashboard.py API end points

def test_dashboard_summary(client,sample_records):
    respone = client.get('/dashboard/')
    assert respone.status_code == status.HTTP_403_FORBIDDEN
    
def test_dashboard_by_category(client,sample_records):
    response = client.get('/dashboard/by-category')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
def test_dashboard_trends(client,sample_records):
    response = client.get('/dashboard/trends')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_dashboard_recents(client,sample_records):
    respone = client.get('/dashboard/recents')
    assert respone.status_code == status.HTTP_403_FORBIDDEN
