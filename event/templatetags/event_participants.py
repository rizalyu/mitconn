from django import template
from django.db.models import OuterRef, Subquery, Sum, Count, Max
from master.models import Event, EventParticipant, Shop, Product, ProductHistory

register = template.Library()

@register.filter
def participant_count(event):
    count = EventParticipant.objects.filter(event=event).count()
    return count

@register.filter
def participant_product(event):
    return EventParticipant.objects.filter(event=event).count()

@register.filter
def latest_sales(product, event):
    latest_stock = ProductHistory.objects.filter(
        product=product,
        created_at__range=(event.startdate, event.enddate)
    ).order_by('-created_at').first()
    
    if latest_stock:
        return latest_stock.sold
    return 0


@register.filter
def event_sales(event):
    latest_sales_subquery = ProductHistory.objects.filter(
        product=OuterRef('participant__id')
    ).order_by('-created_at').values('sold')[:1]

    total_sales = EventParticipant.objects.filter(event=event).annotate(
        latest_event_sales=Subquery(latest_sales_subquery)
    ).aggregate(total_sales=Sum('latest_event_sales'))['total_sales']

    return total_sales if total_sales else 0

@register.filter
def event_locations(event):
    locations = EventParticipant.objects.filter(event=event) \
        .values('participant__owner__location') \
        .distinct() \
        .annotate(location_count=Count('participant__owner__location')).count()

    return locations

@register.filter
def total_sales(shop):
    # Subquery to get the latest created_at for each product
    latest_created_at_subquery = ProductHistory.objects.filter(
        product__owner=shop
    ).values('product').annotate(latest_created_at=Max('created_at')).values('latest_created_at')

    # Use the subquery to get the latest ProductHistory entries
    latest_product_history_entries = ProductHistory.objects.filter(
        product__owner=shop, created_at__in=latest_created_at_subquery
    )

    # Calculate the sum of 'sold' for the latest entries
    total_sales = latest_product_history_entries.aggregate(total_sales=Sum('sold'))['total_sales']

    return total_sales if total_sales else 0

@register.filter
def latest_price(product):
    latest_history = ProductHistory.objects.filter(product=product).order_by('-created_at').first()
    if latest_history:
        return latest_history.price
    return None


@register.filter
def net_sales(participant, event):
    product = participant.participant

    # Get the latest sales before the event starts
    latest_sales_before_event_query = ProductHistory.objects.filter(
        product=product,
        created_at__lt=event.startdate
    ).order_by('-created_at').values('sold')[:1]

    latest_sales_before_event = latest_sales_before_event_query[0]['sold'] if latest_sales_before_event_query else 0

    # Get the latest sales within the event date range
    latest_sales_within_event_query = ProductHistory.objects.filter(
        product=product,
        created_at__range=(event.startdate, event.enddate)
    ).order_by('-created_at').values('sold')[:1]

    latest_sales_within_event = latest_sales_within_event_query[0]['sold'] if latest_sales_within_event_query else 0

    # Calculate the net sales (sales within the event minus sales before the event)
    net_sales = max(0, latest_sales_within_event - latest_sales_before_event)

    return net_sales

@register.filter
def latest_event_sales(event):
    participants_latest_sales = []

    for participant in EventParticipant.objects.filter(event=event):
        product = participant.participant

        # Get the latest sales before the event starts
        latest_sales_before_event_query = ProductHistory.objects.filter(
            product=product,
            created_at__lt=event.startdate
        ).order_by('-created_at').values('sold')[:1]
        
        latest_sales_before_event = latest_sales_before_event_query[0]['sold'] if latest_sales_before_event_query else 0

        # Get the latest sales within the event date range
        latest_sales_within_event_query = ProductHistory.objects.filter(
            product=product,
            created_at__range=(event.startdate, event.enddate)
        ).order_by('-created_at').values('sold')[:1]

        latest_sales_within_event = latest_sales_within_event_query[0]['sold'] if latest_sales_within_event_query else 0

        # Calculate the net sales (sales within the event minus sales before the event)
        net_sales = max(0, latest_sales_within_event - latest_sales_before_event)

        participants_latest_sales.append(net_sales)

    return sum(participants_latest_sales)