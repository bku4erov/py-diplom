import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.response import Response
from model_bakery import baker
from rest_framework.authtoken.models import Token
from backend.models import User, Category, Shop, OrderItem, ProductInfo, \
    Order, Product, Category, Parameter, ProductParameter


USER_DATA = {
        'first_name': 'User''s first name', 
        'last_name': 'User''s last name', 
        # 'email': 'pydiplom2024-1@mail.ru', 
        'password': 'Super_Secret_P@assword1', 
        'company': 'The best company ever', 
        'position': 'The greatest position',
        # 'is_active': True
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
def category_factory():
    def factory(**kwargs):
        return baker.make('backend.Category', **kwargs)
    return factory


@pytest.fixture
def shop_factory():
    def factory(**kwargs):
        return baker.make('backend.Shop', **kwargs)
    return factory


@pytest.fixture
def order_factory():
    def factory(**kwargs):
        return baker.make('backend.Order', **kwargs)
    return factory


@pytest.fixture
def order_item_factory():
    def factory(**kwargs):
        return baker.make('backend.OrderItem', **kwargs)
    return factory


@pytest.fixture
def product_factory():
    def factory(**kwargs):
        return baker.make('backend.Product', **kwargs)
    return factory


@pytest.fixture
def product_info_factory():
    def factory(**kwargs):
        return baker.make('backend.ProductInfo', **kwargs)
    return factory


@pytest.fixture
def category_factory():
    def factory(**kwargs):
        return baker.make('backend.Category', **kwargs)
    return factory


@pytest.fixture
def parameter_factory():
    def factory(**kwargs):
        return baker.make('backend.Parameter', **kwargs)
    return factory


@pytest.fixture
def product_parameter_factory():
    def factory(**kwargs):  
        return baker.make('backend.ProductParameter', **kwargs)
    return factory


@pytest.fixture
def user_buyer():
    user = User.objects.create_user(email='pydiplom2024-1@mail.ru', is_active=True, **USER_DATA)
    user.type = 'buyer'
    user.save()
    return user

@pytest.fixture
def user_shop_without_shop():
    user = User.objects.create_user(email='pydiplom2024@mail.ru', is_active=True, **USER_DATA)
    user.type = 'shop'
    user.save()
    return user


@pytest.fixture
def user_buyer_token(user_buyer):
    token, _ = Token.objects.get_or_create(user=user_buyer)
    return token


@pytest.fixture
def user_shop(user_shop_without_shop, shop_factory):
    shop_factory(user=user_shop_without_shop, state=True)
    return user_shop_without_shop


@pytest.fixture
def user_shop_token(user_shop):
    token, _ = Token.objects.get_or_create(user=user_shop)
    return token

@pytest.fixture
def user_shop_without_shop_token(user_shop_without_shop):
    token, _ = Token.objects.get_or_create(user=user_shop_without_shop)
    return token


@pytest.fixture
def products_for_shop(user_shop, product_factory, category_factory,\
                      product_info_factory, product_parameter_factory, parameter_factory):
    category = category_factory()
    parameters = parameter_factory(_quantity=3)
    products = product_factory(category=category, _quantity=3)
    for product in products:
        product_info = product_info_factory(product=product, shop=user_shop.shop)
        for parameter in parameters:
            product_parameter = product_parameter_factory(product_info=product_info, parameter=parameter)
    return products

@pytest.fixture
def orders_for_shop(user_buyer, products_for_shop, order_factory, order_item_factory):
    orders = order_factory(user=user_buyer, state='new', _quantity=3)
    basket = order_factory(user=user_buyer, state='basket', _quantity=2)
    orders += basket
    for order in orders:
        for product in products_for_shop:
            order_item_factory(order=order, product_info=product.product_infos.first(), quantity=1)
    return orders