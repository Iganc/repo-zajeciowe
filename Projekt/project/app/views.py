from django.shortcuts import render, redirect
from .models import Transaction, Account
from .forms import TransactionForm
from django.shortcuts import get_object_or_404

def dashboard(request):
    transactions = Transaction.objects.all().order_by('-date')[:5]
    accounts = Account.objects.all()
    
    context = {
        'transactions': transactions,
        'accounts': accounts,
    }
    return render(request, 'app/dashboard.html', context)



def add_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()
    
    return render(request, 'app/add_transaction.html', {'form': form})

def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    return render(request, 'app/transaction_detail.html', {'transaction': transaction})

def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        transaction.delete()
        return redirect('dashboard')
    return render(request, 'app/transaction_confirm_delete.html', {'transaction': transaction})