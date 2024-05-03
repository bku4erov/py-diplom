import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from backend.models import User, ConfirmEmailToken, Contact
from reference.netology_pd_diplom.tests.conftest import USER_DATA


# регистрация пользователя
@pytest.mark.django_db
def test_user_reg(api_client):
    url = reverse('backend:user-register')
    # создание пользователя
    new_user = {'email': 'pydiplom2024-1@mail.ru', **USER_DATA}
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
    new_user = {'email': 'pydiplom2024-1@mail.ru', **USER_DATA}
    # создание первого пользователя должно быть успешно
    resp = api_client.post(url, new_user)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert resp_json.get('Status') is True
    # создание второго пользователя (с таким же email) должно быть неуспешно
    resp = api_client.post(url, new_user)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert resp_json.get('Status') is False
    # в результате должен быть создан только один пользователь с таким email
    created_user = User.objects.filter(email=new_user['email']).count()
    assert created_user == 1

# подтверждение email пользователя
# проверка двух вариантов - корректного и некорретного токенов
@pytest.mark.parametrize('valid_token', (True, False))
@pytest.mark.django_db
def test_user_registration(api_client, valid_token):
    url = reverse('backend:user-register-confirm')
    new_user = User.objects.create_user(email='pydiplom2024-1@mail.ru', is_active=False, **USER_DATA)
    # получение токена для последующего запроса для подтверждения email
    if valid_token:
        # выборка из БД токена для подтверждения email
        user_token = ConfirmEmailToken.objects.filter(user__email=new_user.email).first()
        assert user_token
        key = user_token.key
    else:
        key = 'justsomedata'    
    data = {
        'email': new_user.email,
        'token': key
    }
    # отправка запроса на подтверждение email
    resp = api_client.post(url, data)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert resp_json.get('Status') == valid_token
    # проверка что пользователь в базы данных стал активным
    created_user = User.objects.filter(email=new_user.email).first()
    assert created_user.is_active == valid_token

# получить список контактов пользователя
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_buyer_token', status.HTTP_200_OK),                            
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_user_contact_get(api_client, token, expected_status, request, user_buyer, contact_factory):
    url = reverse('backend:user-contact')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    contacts = contact_factory(user=user_buyer, _quantity=3)
    resp = api_client.get(url)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if token:
        assert len(resp_json) == len(contacts)
        assert {'id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone'} <= set(resp_json[0].keys())
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False



# создать контакт пользователя
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_buyer_token', status.HTTP_200_OK),                            
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_user_contact_post(api_client, token, expected_status, request, user_buyer):
    url = reverse('backend:user-contact')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    resp = api_client.post(
        url, 
        data={
            'city': 'Sandy Springs',
            'street': 'Angus Viaduct',
            'house': '896',
            'structure': '946',
            'building': '374',
            'apartment': '429',
            'phone': '925-599-6387'
        },
        format='multipart'
    )
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if token:
        assert {'Status',} <= set(resp_json.keys())
        assert resp_json.get('Status') is True
        assert Contact.objects.filter(user=user_buyer).count() == 1
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False


# редактировать контакт пользователя
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_buyer_token', status.HTTP_200_OK),                            
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_user_contact_put(api_client, token, expected_status, request, user_buyer, contact_factory):
    url = reverse('backend:user-contact')
    contacts = contact_factory(user=user_buyer, _quantity=3)
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    resp = api_client.put(
        url, 
        data={
            'id': contacts[0].id,
            'city': 'Sandy Springs',
            'street': 'Angus Viaduct',
            'house': '896',
            'structure': '946',
            'building': '374',
            'apartment': '429',
            'phone': '925-599-6387'
        },
        format='multipart'
    )
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if token:
        assert {'Status',} <= set(resp_json.keys())
        assert resp_json.get('Status') is True
        assert Contact.objects.filter(id=contacts[0].id).count() == 1
        assert Contact.objects.filter(id=contacts[0].id).first().city == 'Sandy Springs'
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False


# удалить контакт пользователя
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_buyer_token', status.HTTP_200_OK),                            
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_user_contact_del(api_client, token, expected_status, request, user_buyer, contact_factory):
    url = reverse('backend:user-contact')
    contacts = contact_factory(user=user_buyer, _quantity=3)
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    resp = api_client.delete(
        url, 
        data={
            'items': ','.join([str(contact.id) for contact in contacts]),
        }
    )
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if token:
        assert {'Status',} <= set(resp_json.keys())
        assert resp_json.get('Status') is True
        assert Contact.objects.filter(user=user_buyer).count() == 0
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False


# редактировать пользователя
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_buyer_token', status.HTTP_200_OK),                            
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_user_details_edit(api_client, token, expected_status, request, user_buyer):
    url = reverse('backend:user-details')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    resp = api_client.post(
        url, 
        data={
            'first_name': 'New first name',
            'last_name': 'New last name',
            'email': 'pydiplom2024-1@mail.ru',
            'password': 'Super_Mega_Pa$$w0Rd_2024',
            'company': 'New company',
            'position': 'New position'
        }
    )
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if token:
        assert {'Status',} <= set(resp_json.keys())
        assert resp_json.get('Status') is True
        assert User.objects.get(id=user_buyer.id).first_name == 'New first name'
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False


# получить сведения о пользователе
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_buyer_token', status.HTTP_200_OK),                            
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_user_details_get(api_client, token, expected_status, request, user_buyer):
    url = reverse('backend:user-details')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    resp = api_client.get(url)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if token:
        assert {'id', 'first_name', 'last_name', 'email', 'company', 'position'} <= set(resp_json.keys())
        assert resp_json.get('first_name') == user_buyer.first_name
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False


# авторизация пользователя
@pytest.mark.parametrize('valid_password', (True, False))
@pytest.mark.django_db
def test_user_auth(api_client, user_buyer, user_buyer_token, valid_password):
    url=reverse('backend:user-login')
    # отправка запроса на авторизацию пользователя
    data = {
        'email':user_buyer.email, 
        'password': USER_DATA['password'] if valid_password else 'wrongpassword',
    }
    resp = api_client.post(url, data)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert resp_json.get('Status') == valid_password
    if valid_password:
        assert resp_json.get('Token') == user_buyer_token.key
    else:
        assert resp_json.get('Errors')


# сброс пароля
@pytest.mark.django_db
def test_password_reset(api_client, user_buyer):
    url = reverse('backend:password-reset')
    resp = api_client.post(
        url,
        data={
            'email': user_buyer.email
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert {'status', } <= set(resp_json.keys())
    assert resp_json.get('status') == 'OK'