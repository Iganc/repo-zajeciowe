from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction
from .forms import TransactionForm

def add_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()
    
    return render(request, 'transactions/add_transaction.html', {'form': form})

def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    return render(request, 'transactions/transaction_detail.html', {'transaction': transaction})

def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        transaction.delete()
        return redirect('dashboard')
    return render(request, 'transactions/transaction_confirm_delete.html', {'transaction': transaction})