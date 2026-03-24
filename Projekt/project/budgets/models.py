from django.db import models
from django.contrib.auth.models import User
from transactions.models import Transaction, Category

# Create your models here.
class BudgetGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    related_transactions = models.ManyToManyField(Transaction, blank=True)

    def __str__(self):
        return self.name

class RecurringPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    day_of_month = models.PositiveIntegerField() # 1-31
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} (dzień: {self.day_of_month})"