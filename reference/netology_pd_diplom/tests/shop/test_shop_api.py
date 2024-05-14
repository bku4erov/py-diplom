import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from backend.models import User, Shop, Product, ProductInfo, Order, OrderItem
from backend.serializers import ProductInfoSerializer

# получение списка категорий
@pytest.mark.django_db
def test_categories_get(api_client, category_factory):
    url = reverse('backend:categories')
    categories = category_factory(_quantity=5)
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json.get('count')
    assert resp_json.get('count') == 5
    assert resp_json.get('results')
    assert resp_json.get('results')[0]
    names = set()
    for category in categories:
        names |= {category.name}
    assert resp_json.get('results')[0].get('name') in names


# получение списка магазинов
@pytest.mark.django_db
def test_shops_get(api_client, user_shop):
    url = reverse('backend:shops')
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json.get('results')
    assert resp_json.get('results')[0].get('name') == Shop.objects.first().name


# получение списка продуктов
@pytest.mark.django_db
def test_products_get(api_client, products_for_shop):
    url = reverse('backend:products')
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert len(resp_json) == Product.objects.count()
    assert set(ProductInfoSerializer.Meta.fields) <= set(resp_json[0].keys())


# получение списка продуктов с фильтром
@pytest.mark.django_db
def test_products_get_filtered(api_client, products_for_shop):
    url = reverse('backend:products')
    resp = api_client.get(f'{url}?shop_id=0&category_id=0')
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert len(resp_json) == 0


# добавить товары в корзину
@pytest.mark.parametrize(['user', 'token', 'expected_status'], 
                         (
                             ('user_buyer', 'user_buyer_token', status.HTTP_200_OK),                            
                             (None, None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_basket_post(api_client, user, token, expected_status, request, products_for_shop):
    url = reverse('backend:basket')
    basket = []  
    for product in products_for_shop[:2]:
        basket_item = f'{{"product_info":{product.product_infos.first().id}, "quantity": 2}}'
        basket.append(basket_item)
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    data = {'items': f'[{','.join(basket)}]'}
    resp = api_client.post(url, data)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if token:
        assert resp_json.get('Status') is True
        assert Order.objects.filter(state='basket',user=request.getfixturevalue(user)).count() == 1
        assert OrderItem.objects.filter(order=Order.objects.filter(state='basket',user=request.getfixturevalue(user)).first()).count() == 2
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False


# редактировать количество товаров в корзине
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_buyer_token', status.HTTP_200_OK),                            
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_basket_update(api_client, token, expected_status, request, products_for_shop, basket):
    url = reverse('backend:basket')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    basket_update = []
    order_items_ids = []
    for ordered_item in basket.ordered_items.all()[:2]:
        basket_item = f'{{"id":{ordered_item.id}, "quantity": 10}}'
        basket_update.append(basket_item)
        order_items_ids.append(ordered_item.id)
    data = {'items': f'[{','.join(basket_update)}]'}
    resp = api_client.put(url, data)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if token:
        assert resp_json.get('Status') is True
        for order_item_id in order_items_ids:
            assert OrderItem.objects.filter(id=order_item_id).first().quantity == 10
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False


# удалить товары из корзины
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_buyer_token', status.HTTP_200_OK),                            
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_basket_del_items(api_client, token, expected_status, request, products_for_shop, basket):
    url = reverse('backend:basket')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    old_items_num = basket.ordered_items.count()
    data = {'items': ','.join([str(ordered_item.id) for ordered_item in basket.ordered_items.all()[:2]])}
    resp = api_client.delete(url, data)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if token:
        assert resp_json.get('Status') is True
        assert OrderItem.objects.filter(order=basket).count() < old_items_num
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False


# получить содержимое корзины
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_buyer_token', status.HTTP_200_OK),                            
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_basket_get(api_client, token, expected_status, request, products_for_shop, basket):
    url = reverse('backend:basket')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    resp = api_client.get(url)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if token:
        assert {'id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact'} <= set(resp_json[0].keys())
        assert resp_json[0].get('id') == basket.id
        assert len(resp_json[0].get('ordered_items')) == basket.ordered_items.count()
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False


# получить мои заказы
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_buyer_token', status.HTTP_200_OK),                            
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_order_get(api_client, token, expected_status, request, products_for_shop, orders_for_shop):
    url = reverse('backend:order')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    resp = api_client.get(url)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if token:
        assert len(resp_json) == len([order for order in orders_for_shop if order.state != 'basket'])
        assert {'id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact'} <= set(resp_json[0].keys())
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False


# разместить заказ
@pytest.mark.parametrize(['token', 'expected_status'], 
                         (
                             ('user_buyer_token', status.HTTP_200_OK),                            
                             (None, status.HTTP_403_FORBIDDEN),
                         ))
@pytest.mark.django_db
def test_order_post(api_client, token, expected_status, request, products_for_shop, basket):
    url = reverse('backend:order')
    if token:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + request.getfixturevalue(token).key)
    data = {'id': str(basket.id), 'contact': str(basket.contact.pk)}
    resp = api_client.post(url, data)
    assert resp.status_code == expected_status
    resp_json = resp.json()
    assert resp_json
    if token:
        assert {'Status',} <= set(resp_json.keys())
        assert resp_json.get('Status') is True
        Order.objects.filter(id=basket.id).first().state == 'new'
    else:
        assert {'Status', 'Error'} <= set(resp_json.keys())
        assert resp_json.get('Status') is False