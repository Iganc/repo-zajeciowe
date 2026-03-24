from django.shortcuts import render
from transactions.models import Transaction
from .models import Account

def dashboard(request):
    transactions = Transaction.objects.all().order_by('-date')[:5]
    accounts = Account.objects.all()
    
    context = {
        'transactions': transactions,
        'accounts': accounts,
    }
    return render(request, 'accounts/dashboard.html', context)

def account(request):
    pass

def account_edit(request):
    pass