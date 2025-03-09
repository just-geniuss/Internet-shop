from django.contrib import admin
from .models import IntegrationSettings, SyncLog, SyncEntity


class IntegrationSettingsAdmin(admin.ModelAdmin):
    list_display = ['connection_string', 'username', 'enabled', 'last_sync']
    list_filter = ['enabled']
    readonly_fields = ['last_sync']


class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['sync_type', 'status', 'start_time', 'end_time']
    list_filter = ['sync_type', 'status', 'start_time']
    search_fields = ['details']
    readonly_fields = ['sync_type', 'status', 'start_time', 'end_time', 'details']
    date_hierarchy = 'start_time'


class SyncEntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'entity_type', 'is_active', 'last_sync']
    list_filter = ['entity_type', 'is_active']
    search_fields = ['name']
    readonly_fields = ['last_sync']


admin.site.register(IntegrationSettings, IntegrationSettingsAdmin)
admin.site.register(SyncLog, SyncLogAdmin)
admin.site.register(SyncEntity, SyncEntityAdmin)
