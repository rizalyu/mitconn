from django.http import HttpResponse
from django.template import loader
from master.models import *
from django.db.models import Sum, Max, Subquery, OuterRef
from django.db.models.functions import Coalesce
import json


def dashboard(request):
    template = loader.get_template('dashboard.html')
    shop_count = Shop.objects.count()
    product_count = Product.objects.count()
    location_count = Shop.objects.values('location').distinct().count()

    # Subquery to get the latest created_at for each product
    latest_created_at_subquery = ProductHistory.objects.values('product').annotate(latest_created_at=Max('created_at')).values('latest_created_at')

    # Use the subquery to get the latest ProductHistory entries
    latest_product_history_entries = ProductHistory.objects.filter( created_at__in=latest_created_at_subquery)

    # Calculate the sum of 'sold' for the latest entries
    total_sales = latest_product_history_entries.aggregate(total_sales=Sum('sold'))['total_sales']

    
    # Subquery to get the latest created_at for each product in each shop
    latest_created_at_subquery = ProductHistory.objects.values('product__owner').annotate(
        latest_created_at=Max('created_at')
    ).values('latest_created_at', 'product__owner')

    # Use the subquery to get the latest ProductHistory entries for each shop
    latest_product_history_entries = ProductHistory.objects.filter(
        created_at__in=Subquery(latest_created_at_subquery.values('latest_created_at'))
    ).annotate(
        total_sales=Coalesce(Sum('sold'), 0)
    )

    # Retrieve unique shops
    unique_shops = latest_product_history_entries.values_list('product__owner', flat=True).distinct()

    participants_latest_sales = []

    for shop in Shop.objects.all():
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

        shop_data = {
            'shop_id': shop.id,
            'shop_name': shop.name
        }

        participants_latest_sales.append({'shop': shop_data, 'latest_sales': sales})

    participants_latest_sales = json.dumps(participants_latest_sales)

    # Subquery to get the maximum created_at for each product_id
    max_created_at_subquery = ProductHistory.objects.filter(
        product_id=OuterRef('product_id'),
    ).order_by('-created_at').values('created_at')[:1]

    # Query to get the entire ProductHistory objects for the latest entries based on product_id
    histories = ProductHistory.objects.filter(
        created_at__in=Subquery(max_created_at_subquery)
    ).order_by('-created_at')

    sales = 0

    for history in histories:
        sales += history.sold
    
    context = {
        'shop_count': shop_count,
        'product_count': product_count,
        'location_count':  location_count,
        'total_sales': sales,
        'shop_latest_sales': participants_latest_sales
    }
    return HttpResponse(template.render(context, request))
