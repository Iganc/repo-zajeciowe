from django.contrib import admin
from .models import Transaction, Category

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'category', 'account')
    list_filter = ('date', 'category')
    search_fields = ('description',)
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    list_filter = ('type',)