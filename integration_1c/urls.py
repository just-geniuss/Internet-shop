from django.urls import path
from . import views

app_name = 'integration_1c'

urlpatterns = [
    path('import/', views.import_data, name='import_data'),
    path('export/', views.export_data, name='export_data'),
    path('sync-status/', views.sync_status, name='sync_status'),
    path('api/products/', views.api_products, name='api_products'),
    path('api/orders/', views.api_orders, name='api_orders'),
] 