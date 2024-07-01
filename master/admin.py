from django.contrib import admin
from master.models import *

admin.site.register([Category, Shop, ShopHistory, Product, ProductHistory, Event, EventParticipant])

