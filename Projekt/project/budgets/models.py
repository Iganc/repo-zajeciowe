from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account
from transactions.models import Category

# Create your models here.
class BudgetGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budget_goals')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='budget_goals')
    name = models.CharField(max_length=100)
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Budget Goals"

    def __str__(self):
        return f"{self.name} ({self.user.username}) - balance: {self.balance}"

class RecurringPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    day_of_month = models.PositiveIntegerField() # 1-31
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} (dzień: {self.day_of_month})"