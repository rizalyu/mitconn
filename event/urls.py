from django.urls import path
from event import views

urlpatterns = [
    path('events/<str:status>/', views.all_events, name='all-events'),
    path('events/<int:id>/analytics', views.event_analytics, name='event-analytics'),
    path('events/<int:id>/participants', views.event_participants, name='event-participants'),
    path('events/add-event', views.add_event, name='add-event'),
    path('events/<int:id>/manage', views.manage_event, name='manage-event'),
    path('events/<int:id>/participants/add', views.add_participant, name='add-participant'),
    path('events/<int:event_id>/participants/<int:participant_id>/delete', views.delete_participant, name='delete_participant')
]