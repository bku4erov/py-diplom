import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from backend.models import User, Shop, Product
from backend.serializers import ProductInfoSerializer
from reference.netology_pd_diplom.tests.conftest import category_factory, shop_factory

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