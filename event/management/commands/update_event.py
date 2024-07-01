from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from master.models import Event
from django.utils import timezone

class Command(BaseCommand):
    help = 'Update an event status'

    def handle(self, *args: Any, **options: Any):

        try:

            for event in Event.objects.all():

                if event.startdate <= timezone.now():
                    event.status = 'active'
                elif event.startdate >= timezone.now():
                    event.status = 'upcoming'
                elif event.enddate < timezone.now():
                    event.status = 'completed'

                event.save()
        
        except Exception as e:
            print(f'Error Occured \n Error message : {e}')
            