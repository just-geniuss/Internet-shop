from django.contrib import admin
from .models import IntegrationSettings, SyncLog, SyncEntity, ImportSetting, PendingImport


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


class ImportSettingAdmin(admin.ModelAdmin):
    list_display = ['default_visibility', 'allow_price_edit', 'allow_category_edit']
    fieldsets = (
        ('Общие настройки', {
            'fields': ('default_category', 'default_visibility')
        }),
        ('Расширенные настройки', {
            'fields': ('allow_price_edit', 'allow_category_edit')
        }),
    )
    
    def has_add_permission(self, request):
        # Разрешаем создать только один объект настроек
        return ImportSetting.objects.count() == 0


class PendingImportAdmin(admin.ModelAdmin):
    list_display = ['get_product_name', 'external_id', 'status', 'created', 'updated']
    list_filter = ['status', 'created', 'updated']
    search_fields = ['external_id', 'data']
    readonly_fields = ['external_id', 'data', 'created', 'updated']
    actions = ['mark_as_imported', 'mark_as_rejected']
    
    def mark_as_imported(self, request, queryset):
        queryset.update(status='imported')
    mark_as_imported.short_description = "Отметить как импортированные"
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = "Отметить как отклоненные"


admin.site.register(IntegrationSettings, IntegrationSettingsAdmin)
admin.site.register(SyncLog, SyncLogAdmin)
admin.site.register(SyncEntity, SyncEntityAdmin)
admin.site.register(ImportSetting, ImportSettingAdmin)
admin.site.register(PendingImport, PendingImportAdmin)
