from django.contrib import admin
from .models import BudgetGoal, RecurringPayment

@admin.register(BudgetGoal)
class BudgetGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'account', 'allocated_amount', 'balance')
    list_filter = ('user', 'account')

@admin.register(RecurringPayment)
class RecurringPaymentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'amount', 'day_of_month')
    list_filter = ('user', 'day_of_month')