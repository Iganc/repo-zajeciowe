from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account

class Category(models.Model):
    NAME_CHOICES = [
        ('EXPENSE', 'Wydatek'),
        ('INCOME', 'Przychód'),
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=NAME_CHOICES, default='EXPENSE')
    icon = models.CharField(max_length=50, blank=True) 

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.date} | {self.amount} | {self.category.name if self.category else 'Brak'}"

