from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from event.forms import AddEventForm, EditEventForm, AddEventParticipantForms
from master.models import Event, EventParticipant, Shop, ProductHistory, Product
from django.db.models import Max, Sum, F, ExpressionWrapper, fields
from django.utils import timezone
from django.urls import reverse
from django.core.serializers import serialize
import json
from django.core.management import call_command

def all_events(request, status):

    template = loader.get_template('all_events.html')

    call_command('update_event')

    if status == 'upcoming':
        context = {
            'status': status,
            'events': Event.objects.filter(status='upcoming')
        }
        return HttpResponse(template.render(context, request))
    elif status == 'active':
        context = {
            'status': status,
            'events': Event.objects.filter(status='active')
        }
        return HttpResponse(template.render(context, request))
    elif status == 'completed':
        context = {
            'status': status,
            'events': Event.objects.filter(status='completed')
        }
        return HttpResponse(template.render(context, request))
    else:
        raise Http404("Invalid Event Status")


def event_analytics(request, id):
    template = loader.get_template('event_analytics.html')
    event = Event.objects.get(id=id)
    call_command('update_event')

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

        participant_data = {
            'event': participant.event.id,
            'product': participant.participant.name,
            'latest_sales': net_sales,
        }

        participants_latest_sales.append(participant_data)

    participants_latest_sales = json.dumps(participants_latest_sales)

    context = {
        'latest_sales': participants_latest_sales,
        'participants': EventParticipant.objects.filter(event=event),
        'event': event,
    }

    return HttpResponse(template.render(context, request))

def event_participants(request, id):
    template = loader.get_template('event_participants.html')
    event = Event.objects.get(id=id)
    participants = EventParticipant.objects.filter(event=event)
    context = {
        'event': event,
        'participants': participants
    }
    call_command('update_event')
    return HttpResponse(template.render(context, request))

def add_event(request):
    call_command('update_event')
    if request.method == "POST":

        form_data = AddEventForm(request.POST)

        if form_data.is_valid():

            current_dt = timezone.now()

            if current_dt < form_data.cleaned_data['start_date']:
                status = 'upcoming'
            elif current_dt > form_data.cleaned_data['start_date'] and current_dt < form_data.cleaned_data['end_date']:
                status = 'active'
            elif current_dt > form_data.cleaned_data['end_date']:
                status = 'completed'
            else:
                status = 'unknown'

            if form_data.cleaned_data['start_date'] > form_data.cleaned_data['end_date']:
                return HttpResponseRedirect(reverse('all-events', args=['active']))
            
            else:
                Event.objects.create(name=form_data.cleaned_data['event_name'], startdate=form_data.cleaned_data['start_date'], enddate=form_data.cleaned_data['end_date'], status=status)

            return HttpResponseRedirect(reverse('all-events', args=['active']))

    template = loader.get_template('add_event.html')
    context = {
        'form': AddEventForm()
    }
    return HttpResponse(template.render(context, request))

def manage_event(request, id):
    call_command('update_event')
    event = Event.objects.get(id=id)

    if request.method == "POST":

        form_data = EditEventForm(request.POST)

        if form_data.is_valid():

            current_dt = timezone.now()

            if current_dt < form_data.cleaned_data['start_date']:
                status = 'upcoming'
            elif current_dt > form_data.cleaned_data['start_date'] and current_dt < form_data.cleaned_data['end_date']:
                status = 'active'
            elif current_dt > form_data.cleaned_data['end_date']:
                status = 'completed'
            else:
                status = 'unknown'

            event.name = form_data.cleaned_data['event_name']
            event.startdate = form_data.cleaned_data['start_date']
            event.enddate = form_data.cleaned_data['end_date']
            event.status = status

            event.save()

            return HttpResponseRedirect(reverse('event-analytics', args=[event.id]))

    template = loader.get_template('manage_event.html')
    form = EditEventForm(initial={
        'event_name': event.name,
        'start_date': event.startdate,
        'end_date': event.enddate
    })
    context = {
        'form': form
    }
    return HttpResponse(template.render(context, request))

def add_participant(request, id):
    call_command('update_event')
    event = Event.objects.get(id=id)

    if request.method == "POST":

        form_data = AddEventParticipantForms(request.POST)

        if form_data.is_valid():

            participant = form_data.cleaned_data['participant']

            if EventParticipant.objects.filter(event=event, participant=participant).exists():
                return HttpResponseRedirect(reverse('event-participants', args=[event.id]))
            
            else:
                EventParticipant.objects.create(event=event, participant=participant)


            return HttpResponseRedirect(reverse('event-participants', args=[event.id]))

    template = loader.get_template('add_participant.html')
    context = {
        'event': event,
        'part_form': AddEventParticipantForms()
    }
    return HttpResponse(template.render(context, request))

def delete_participant(request, event_id, participant_id):

    target = EventParticipant.objects.get(event=Event.objects.get(id=event_id), participant=Product.objects.get(id=participant_id))

    if request.method == "POST":

        target.delete()

        return HttpResponseRedirect(reverse('event-participants', args=[event_id]))