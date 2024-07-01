from django import template
from django.db.models import OuterRef, Subquery, Max, Sum
from master.models import Shop, ShopHistory, ProductHistory, EventParticipant, Product

register = template.Library()

@register.filter
def latest_rating(shop):
    latest_history = ShopHistory.objects.filter(shop=shop).order_by('-created_at').first()
    if latest_history:
        return latest_history.rating
    return None

@register.filter
def latest_sales(shop):
    # Subquery to get the maximum created_at for each product_id
    max_created_at_subquery = ProductHistory.objects.filter(
        product_id=OuterRef('product_id'),
        product__owner=shop
    ).order_by('-created_at').values('created_at')[:1]

    # Query to get the entire ProductHistory objects for the latest entries based on product_id
    histories = ProductHistory.objects.filter(
        product__owner=shop,
        created_at__in=Subquery(max_created_at_subquery)
    ).order_by('-created_at')

    sales = 0

    for history in histories:
        sales += history.sold
    
    return sales

@register.filter
def event_participated(shop):
    return EventParticipant.objects.filter(participant__owner=shop).count()

@register.filter
def latest_price(product):
    latest_history = ProductHistory.objects.filter(product=product).order_by('-created_at').first()
    if latest_history:
        return latest_history.price
    return None

@register.filter
def latest_stock(product):
    latest_stock = ProductHistory.objects.filter(product=product).order_by('-created_at').first()
    if latest_stock:
        return latest_stock.stock
    return None

@register.filter
def latest_product_sales(product):
    latest_stock = ProductHistory.objects.filter(product=product).order_by('-created_at').first()
    if latest_stock:
        return latest_stock.sold
    return None

@register.filter
def product_count(shop):
    products = Product.objects.filter(owner=shop).count()
    return products
