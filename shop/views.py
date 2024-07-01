from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from master.models import Shop, ProductHistory
from django.db.models import Count, Sum, OuterRef, Subquery, Max
from django.db.models.functions import Coalesce, TruncDate
from django.core.management import call_command, CommandError
import json

from shop.forms import AddShopForm

def all_shop(request):
    template = loader.get_template('all_shops.html')
    shops = Shop.objects.annotate(num_products=Count('product'), total_sold=Coalesce(Sum('product__producthistory__sold'), 0))
    unique_locations = set(shop.location for shop in shops)

    for shop in shops:
        total_sold = ProductHistory.objects.filter(product__owner=shop).aggregate(Sum('sold'))['sold__sum']
        shop.total_sold = total_sold if total_sold else 0

    location = request.GET.get('location', 'all')
    min_products = request.GET.get('minproducts', None)
    max_products = request.GET.get('maxproducts', None)
    min_sales = request.GET.get('minsales', None)
    max_sales = request.GET.get('maxsales', None)
    

    if location != 'all':
        shops = shops.filter(location=location)
    if min_products is not None and min_products != '':
        shops = shops.filter(num_products__gte=min_products)
    if max_products is not None and max_products != '':
        shops = shops.filter(num_products__lte=max_products)
    if min_sales is not None and min_sales != '':
        shops = shops.filter(total_sold__gte=min_sales)
    if max_sales is not None and max_sales != '':
        shops = shops.filter(total_sold__lte=max_sales)

    filter_values = {
        'location': location,
        'min_products': min_products,
        'max_products': max_products,
        'min_sales': min_sales,
        'max_sales': max_sales,
    }

    context = {
        'shops': shops,
        'filter_values': filter_values,
        'unique_locations': unique_locations
    }
    return HttpResponse(template.render(context, request))

def shop_analytics(request, id):
    template = loader.get_template('shop_analytics.html')
    shop = Shop.objects.get(id=id)

#   Get the 5 latest unique dates (without time) for the shop
    latest_dates = (
        ProductHistory.objects
        .filter(product__owner=shop)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .distinct()
        .order_by('-date')[:5]
    )

    # Calculate the sum of all product sales for each unique date
    # entry_sums = []
    # for date_entry in latest_dates:
    #     total_sales = ProductHistory.objects.filter(created_at__date=date_entry['date'], product__owner=shop).aggregate(sum_sales=Sum('sold'))['sum_sales'] or 0
    #     entry_sums.append({'date': date_entry['date'].strftime('%Y-%m-%d'), 'total_sales': total_sales})

    entry_sums = []
    for date_entry in latest_dates:

        subquery = ProductHistory.objects.filter(
        product=OuterRef('product'),
            created_at__date=date_entry['date']
        ).order_by('-created_at').values('created_at')[:1]

        histories = ProductHistory.objects.filter(
            product__owner=shop,
            created_at__date=date_entry['date'],
            created_at__in=Subquery(subquery)
        ).order_by('product', '-created_at')

        sales = 0

        for history in histories:
            sales += history.sold

        entry_sums.append({'date': date_entry['date'].strftime('%Y-%m-%d'), 'total_sales':sales})

    entry_sums = json.dumps(entry_sums, default='str')

    context = {
        'shop': shop,
        'entry_sums': entry_sums,
    }
    return HttpResponse(template.render(context, request))

def shop_products(request, id):
    template = loader.get_template('shop_products.html')
    shop = Shop.objects.get(id=id)
    context = {
        'shop': shop
    }
    return HttpResponse(template.render(context, request))

def add_shop(request):

    if request.method == "POST":

        form_data = AddShopForm(request.POST)

        if form_data.is_valid():
            shop_url = form_data.cleaned_data['shop_url']

            try:
                call_command('scrape_shop', shop_url)

                return HttpResponseRedirect('/shops/')
            
            except CommandError as e:

                template = loader.get_template('add_shop.html')
                context = {
                    'form': AddShopForm(),
                    'error_message': "Scrapping Error"
                }
                return HttpResponse(template.render(context, request))

    template = loader.get_template('add_shop.html')
    context = {
        'form': AddShopForm()
    }
    return HttpResponse(template.render(context, request))