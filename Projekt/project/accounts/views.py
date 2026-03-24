from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from transactions.models import Transaction
from .models import Account
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import AccountForm


@login_required
def dashboard(request):
    # Filtruj transakcje tylko dla kont zalogowanego użytkownika
    transactions = Transaction.objects.filter(
        account__user=request.user
    ).order_by('-date')
    # Filtruj konta tylko dla zalogowanego użytkownika
    accounts = Account.objects.filter(user=request.user)
    
    context = {
        'transactions': transactions,
        'accounts': accounts,
    }
    return render(request, 'accounts/dashboard.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def account(request):
    """Wyświetl konta użytkownika"""
    accounts = Account.objects.filter(user=request.user)
    context = {
        'accounts': accounts,
    }
    return render(request, 'accounts/account.html', context)

def account_edit(request):
    pass


@login_required
def add_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            return redirect('dashboard')
    else:
        form = AccountForm()
    
    return render(request, 'accounts/add_account.html', {'form': form})
    return render(request, 'accounts/add_account.html', {'form': form})