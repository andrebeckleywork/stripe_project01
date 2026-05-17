from django.contrib import admin
from .models import Product, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ('name', 'price_display', 'emoji', 'available', 'created_at')
    list_editable = ('available',)
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ('id', 'product', 'customer_email',
                       'amount_display', 'status', 'created_at')
    list_filter     = ('status',)
    readonly_fields = ('stripe_session_id', 'created_at')