import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from backend.models import Shop, Order
# from reference.netology_pd_diplom.tests.conftest import api_client, user_shop

# обновить прайс партнера - проверка
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_shop_without_shop_token', status.HTTP_200_OK),
                             ('user_buyer_token', status.HTTP_403_FORBIDDEN),                             
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_partner_update(api_client, token, expected_status, request):
    url = reverse('backend:partner-update')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    data = {'url': 'https://raw.githubusercontent.com/bku4erov/py-diplom/master/data/shop1.yaml'}
    resp = api_client.post(url, data)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if expected_status == status.HTTP_200_OK:
        assert resp_json.get('Status') is True
        assert resp_json.get('task_id')
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False


# получить статус партнера - проверка
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_shop_token', status.HTTP_200_OK),
                             ('user_buyer_token', status.HTTP_403_FORBIDDEN),
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_partner_state(api_client, token, expected_status, request):
    url = reverse('backend:partner-state')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    resp = api_client.get(url)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if expected_status == status.HTTP_200_OK:
        assert {'name', 'state'} <= set(resp_json.keys())
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False

# обновить статус партнера
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_shop_token', status.HTTP_200_OK),
                             ('user_buyer_token', status.HTTP_403_FORBIDDEN),
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_partner_state(api_client, token, expected_status, request):
    url = reverse('backend:partner-state')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    data = {'state': 'false'}
    resp = api_client.post(url, data)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if expected_status == status.HTTP_200_OK:
        assert {'Status', } <= set(resp_json.keys())
        assert resp_json.get('Status') is True
        assert Shop.objects.first().state is False
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False

# получить сформированные заказы - проверка
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_shop_token', status.HTTP_200_OK),
                             ('user_buyer_token', status.HTTP_403_FORBIDDEN),
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_partner_orders(api_client, orders_for_shop, token, expected_status, request):
    url = reverse('backend:partner-orders')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    resp = api_client.get(url)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if expected_status == status.HTTP_200_OK:
        assert len(resp_json) == (len(orders_for_shop)-2)
        assert {'id', 'ordered_items'} <= set(resp_json[0].keys())
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False


# обновить статус заказа
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_shop_token', status.HTTP_200_OK),
                             ('user_buyer_token', status.HTTP_403_FORBIDDEN),
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_partner_orders(api_client, orders_for_shop, token, expected_status, request):
    url = reverse('backend:partner-orders')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    data = {        
        'id': orders_for_shop[0].id, 
        'state': 'confirmed'
    }
    resp = api_client.put(url, data)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if expected_status == status.HTTP_200_OK:
        assert resp_json.get('Status') is True
        assert Order.objects.filter(id=data['id']).first().state == 'confirmed'
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False