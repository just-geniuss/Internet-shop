from django.contrib import admin
from .models import Category, Manufacturer, Car, Product, ProductImage, ProductAttribute, ProductAttributeValue


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'slug', 'external_id']
    list_filter = ['parent']
    search_fields = ['name', 'slug', 'external_id']
    prepopulated_fields = {'slug': ('name',)}


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'slug', 'external_id']
    list_filter = ['country']
    search_fields = ['name', 'slug', 'external_id']
    prepopulated_fields = {'slug': ('name',)}


class CarAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model', 'year_start', 'year_end', 'engine_type', 'external_id']
    list_filter = ['brand', 'year_start', 'engine_type']
    search_fields = ['brand', 'model', 'external_id']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'manufacturer', 'price', 'stock', 'available', 'is_visible', 'created', 'updated']
    list_filter = ['available', 'is_visible', 'created', 'updated', 'category', 'manufacturer']
    list_editable = ['price', 'stock', 'available', 'is_visible']
    search_fields = ['name', 'sku', 'external_id']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductAttributeValueInline]
    actions = ['make_visible', 'make_invisible']
    
    def make_visible(self, request, queryset):
        queryset.update(is_visible=True)
    make_visible.short_description = "Показывать выбранные товары на сайте"
    
    def make_invisible(self, request, queryset):
        queryset.update(is_visible=False)
    make_invisible.short_description = "Скрыть выбранные товары с сайта"


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttribute, ProductAttributeAdmin)
