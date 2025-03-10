from django.urls import path
from . import views

app_name = 'integration_1c'

urlpatterns = [
    path('import/', views.import_data, name='import_data'),
    path('export/', views.export_data, name='export_data'),
    path('sync-status/', views.sync_status, name='sync_status'),
    path('api/products/', views.api_products, name='api_products'),
    path('api/orders/', views.api_orders, name='api_orders'),
    path('pending-imports/', views.pending_imports, name='pending_imports'),
    path('edit-pending-import/<int:pending_id>/', views.edit_pending_import, name='edit_pending_import'),
    path('process-pending-import/<int:pending_id>/', views.process_pending_import, name='process_pending_import'),
    path('reject-pending-import/<int:pending_id>/', views.reject_pending_import, name='reject_pending_import'),
] 