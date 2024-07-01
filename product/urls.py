from django.urls import path
from product import views

urlpatterns = [
    path('products/', views.all_product, name='all-products'),
    path('products/add-product/', views.add_product, name='add-product'),
    path('products/details/<int:id>/settings/', views.product_settings, name='product-settings'),
    path('products/details/<int:id>/analytics/', views.product_analytics, name='product-analytics'),
    path('products/details/<int:id>/', views.product_details, name='product-details'),
]