import pytest
from django.urls import reverse
from django.core import mail
from rest_framework import status
from rest_framework.response import Response
from backend.models import User, ConfirmEmailToken
from reference.netology_pd_diplom.tests.conftest import user_json_data, new_user


# регистрация пользователя
@pytest.mark.django_db
def test_user_reg(api_client):
    url = reverse('backend:user-register')
    # создание пользователя
    new_user = user_json_data('pydiplom2024-11@mail.ru')
    resp = api_client.post(url, new_user)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert resp_json.get('Status') == True
    # проверка что пользователь появился в базе данных
    created_user = User.objects.filter(email=new_user['email']).first()
    assert created_user
    # проверка корректности заполнения полей пользователя
    new_user.pop('password')
    for user_field in new_user.keys():
        assert getattr(created_user, user_field) == new_user[user_field]


# проверка невозможности регистрации двух пользователей с одним email
@pytest.mark.django_db
def test_user_reg_same_email(api_client):
    url = reverse('backend:user-register')
    new_user = user_json_data('pydiplom2024-11@mail.ru')
    # создание первого пользователя должно быть успешно
    resp = api_client.post(url, new_user)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert resp_json.get('Status') == True
    # создание второго пользователя (с таким же email) должно быть неуспешно
    resp = api_client.post(url, new_user)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert resp_json.get('Status') == False
    # в результате должен быть создан только один пользователь с таким email
    created_user = User.objects.filter(email=new_user['email']).count()
    assert created_user == 1

# подтверждение email пользователя
# проверка двух вариантов - корректного и некорретного токенов
@pytest.mark.parametrize('valid_token', (True, False))
@pytest.mark.django_db
def test_user_registration(api_client, new_user, valid_token):
    url = reverse('backend:user-register-confirm')
        # получение токена для последующего запроса для подтверждения email
    if valid_token:
        # выборка из БД токена для подтверждения email
        user_token = ConfirmEmailToken.objects.filter(user__email=new_user['user'].email).first()
        assert user_token
        key = user_token.key
    else:
        key = 'justsomedata'    
    data = {
        'email': new_user['user'].email,
        'token': key
    }
    # отправка запроса на подтверждение email
    resp = api_client.post(url, data)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert resp_json.get('Status') == valid_token
    # проверка что пользователь в базы данных стал активным
    created_user = User.objects.filter(email=new_user['user'].email).first()
    assert created_user.is_active == valid_token

# авторизация пользователя
@pytest.mark.parametrize('valid_password', (True, False))
@pytest.mark.django_db
def test_user_auth(api_client, new_user, valid_password):
    url=reverse('backend:user-login')
    new_user['user'].is_active = True
    new_user['user'].save()
    # отправка запроса на авторизацию пользователя
    data = {
        'email': new_user['user'].email, 
        'password': new_user['password'] if valid_password else 'wrongpassword',
    }
    resp = api_client.post(url, data)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert resp_json.get('Status') == valid_password
    if valid_password:
        assert resp_json.get('Token')
    else:
        assert resp_json.get('Errors')
