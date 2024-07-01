from django import template
from master.models import Product, ProductHistory

register = template.Library()

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
def latest_sales(product):
    latest_stock = ProductHistory.objects.filter(product=product).order_by('-created_at').first()
    if latest_stock:
        return latest_stock.sold
    return None

@register.filter
def latest_rating(product):
    latest_stock = ProductHistory.objects.filter(product=product).order_by('-created_at').first()
    if latest_stock:
        return latest_stock.rating
    return None
