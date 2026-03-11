from django.contrib import admin
from .models import Category, Account, Transaction, BudgetGoal, RecurringPayment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    list_filter = ('type',)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'balance')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'category', 'account')
    list_filter = ('date', 'category')
    search_fields = ('description',)

admin.site.register(BudgetGoal)
admin.site.register(RecurringPayment)