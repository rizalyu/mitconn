from django.urls import path
from master import views

urlpatterns = [
    path('', views.dashboard, name='dashboard')
]