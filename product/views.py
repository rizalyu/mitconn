from django.template import loader
from django.db.models import OuterRef, Subquery
from django.http import HttpResponse, HttpResponseRedirect
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.serializers import serialize
from master.models import Product, ProductHistory, Category
from django.db.models import Count, Sum, F
from django.db.models.functions import Coalesce, TruncDate
from product.forms import AddProductForm

def all_product(request):
    template = loader.get_template('all_product.html')
    categories = Category.objects.all()

    latest_product_history_subquery = ProductHistory.objects.filter(
        product=OuterRef('pk')
    ).order_by('-created_at').values('price', 'sold')[:1]

    products = Product.objects.select_related('owner', 'category').annotate(
        latest_price=Subquery(latest_product_history_subquery.values('price')),
        latest_sales=Subquery(latest_product_history_subquery.values('sold'))
    )

    category_filter = request.GET.get('categories', 'all')
    min_price = request.GET.get('minprice', None)
    max_price = request.GET.get('maxprice', None)
    min_sales = request.GET.get('minsales', None)
    max_sales = request.GET.get('maxsales', None)

    if category_filter != 'all':
        products = products.filter(category__name=category_filter)

    if min_price is not None and min_price != '':
        products = products.filter(latest_price__gte=min_price)

    if max_price is not None and max_price != '':
        products = products.filter(latest_price__lte=max_price)

    if min_sales is not None and min_sales != '':
        products = products.filter(latest_sales__gte=min_sales)

    if max_sales is not None and max_sales != '':
        products = products.filter(latest_sales__lte=max_sales)

    context = {
        'products': products,
        'categories': categories,
        'filter_values': {
            'categories': category_filter,
            'min_price': min_price,
            'max_price': max_price,
            'min_sales': min_sales,
            'max_sales': max_sales,
        },
    }

    return HttpResponse(template.render(context, request))

def add_product(request):

    if request.method == "POST":

        form_data = AddProductForm(request.POST)

        if form_data.is_valid():
            try:
                product_url = form_data.cleaned_data['product_url']
                selected_shop = form_data.cleaned_data['shop']

                call_command('scrape_product', product_url, selected_shop.name)

                return HttpResponseRedirect('/products/')
        
            except Exception as e:
                print(e)
                error_message = "Product Scraping Failed"

                template = loader.get_template('add_product.html')
                context = {
                    'form': AddProductForm(),
                    'error_message': error_message
                }
                return HttpResponse(template.render(context, request))


    template = loader.get_template('add_product.html')
    context = {
        'form': AddProductForm()
    }
    return HttpResponse(template.render(context, request))
    

def product_details(request, id):
    template = loader.get_template('product_details_data.html')
    product = Product.objects.get(id=id)
    context = {
        'product': product
    }
    return HttpResponse(template.render(context, request))

def product_analytics(request, id):
    template = loader.get_template('product_analytics.html')
    product = Product.objects.get(id=id)
    history = (
        ProductHistory.objects
        .filter(
            product=product,
            created_at=Subquery(
                ProductHistory.objects
                .filter(product=OuterRef('product'))
                .annotate(date=TruncDate('created_at'))
                .order_by('-date', '-created_at')[:1]
                .values('created_at')
            )
        )
        .order_by('-created_at')[:5]
    )
    history_json = serialize('json', history)
    context = {
        'history': history_json,
        'product': product
    }
    return HttpResponse(template.render(context, request))

def product_settings(request, id):
    template = loader.get_template('product_settings.html')
    product = Product.objects.get(id=id)
    context = {
        'product': product
    }
    return HttpResponse(template.render(context, request))