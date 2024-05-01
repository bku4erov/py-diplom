import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.response import Response
from model_bakery import baker
from backend.models import User

def user_json_data(email):
    return {
        'first_name': 'User''s first name', 
        'last_name': 'User''s last name', 
        'email': email, 
        'password': 'Super_Secret_P@assword1', 
        'company': 'The best company ever', 
        'position': 'The greatest position'
    }

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_factory():
    def factory(**kwargs):
        return baker.make('backend.User', **kwargs)
    return factory

@pytest.fixture
def new_user(api_client):
    url = reverse('backend:user-register')
    new_user = user_json_data('pydiplom2024-11@mail.ru')
    resp = api_client.post(url, new_user)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert resp_json.get('Status') == True
    created_user = User.objects.filter(email=new_user['email']).first()
    assert created_user
    return {'user': created_user, 'password': new_user['password']}
