from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    NAME_CHOICES = [
        ('EXPENSE', 'Wydatek'),
        ('INCOME', 'Przychód'),
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=NAME_CHOICES, default='EXPENSE')
    icon = models.CharField(max_length=50, blank=True) 

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} | {self.amount} | {self.category.name if self.category else 'Brak'}"

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