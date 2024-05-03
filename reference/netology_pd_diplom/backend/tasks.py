from celery import shared_task
from celery.contrib.django.task import DjangoTask
from django.core.mail import EmailMultiAlternatives
from yaml import load as load_yaml, Loader

from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from backend.serializers import ShopExportSerializer

@shared_task(base=DjangoTask)
def send_email(title, message, sender, recipients):
    """
    Sends an email with the given title, message, sender, and recipients.

    Args:
        title (str): The title of the email.
        message (str): The content of the email.
        sender (str): The email address of the sender.
        recipients (list): A list of email addresses of the recipients.

    Returns:
        None
    """
    
    msg = EmailMultiAlternatives(
            # title:
            title,
            # message:
            message,
            # from:
            sender,
            # to:
            recipients
        )
    msg.send()


@shared_task
def update_partner_info(stream, user_id):
    """
    Updates the partner information with the given stream and user ID.

    Parameters:
        stream (stream): The stream containing the partner information in YAML format.
        user_id (int): The ID of the user associated with the partner.

    Returns:
        None
    """

    data = load_yaml(stream, Loader=Loader)

    shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=user_id)
    for category in data['categories']:
        category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
        category_object.shops.add(shop.id)
        category_object.save()
    
    ProductInfo.objects.filter(shop_id=shop.id).delete()

    for item in data['goods']:
        product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

        product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item['id'],
                                                              model=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id)
        for name, value in item['parameters'].items():
            parameter_object, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)


@shared_task
def export_partner_info(user_id):
    """
    Export the partner information for a given user.

    Parameters:
        user_id (int): The ID of the user whose partner information should be exported.

    Returns:
        dict: The serialized data of the partner information.
    """

    shop = Shop.objects.filter(user_id=user_id).first()
    serializer = ShopExportSerializer(shop)
    return serializer.data