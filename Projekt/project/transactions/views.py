from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal
from .models import Transaction, Category
from .forms import TransactionForm
from accounts.models import Account
from budgets.models import BudgetGoal

@login_required
def add_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction_type = form.cleaned_data.get('transaction_type')
            transaction.transaction_type = transaction_type
            
            if not form.cleaned_data.get('category'):
                transaction.category = None
            
            account = transaction.account
            budget_goal = transaction.budget_goal
            amount = Decimal(str(transaction.amount))
            
            # Jeśli transakcja powiązana z celem
            if budget_goal:
                if transaction_type == 'EXPENSE':
                    budget_goal.balance -= amount
                    budget_goal.save()
                else:
                    # Przychód na cel - dodaj do celu
                    budget_goal.balance += amount
                    budget_goal.save()
            else:
                # Bez celu - zmień saldo konta
                if transaction_type == 'EXPENSE':
                    account.balance -= amount
                else:
                    account.balance += amount
                account.save()
            
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm(user=request.user)
        
        user_accounts = Account.objects.filter(user=request.user)
        if user_accounts.count() == 1:
            form.fields['account'].initial = user_accounts.first()
    
    return render(request, 'transactions/add_transaction.html', {'form': form})

def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    return render(request, 'transactions/transaction_detail.html', {'transaction': transaction})

def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        account = transaction.account
        budget_goal = transaction.budget_goal
        amount = Decimal(str(transaction.amount))
        
        # Zwróć pieniądze tam gdzie je zabrano
        if budget_goal:
            if transaction.transaction_type == 'EXPENSE':
                budget_goal.balance += amount
            else:
                budget_goal.balance -= amount
            budget_goal.save()
        else:
            if transaction.transaction_type == 'EXPENSE':
                account.balance += amount
            else:
                account.balance -= amount
            account.save()
        
        transaction.delete()
        return redirect('dashboard')
    return render(request, 'transactions/transaction_confirm_delete.html', {'transaction': transaction})

@login_required
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            old_amount = Decimal(str(Transaction.objects.get(pk=pk).amount))
            old_type = Transaction.objects.get(pk=pk).transaction_type
            old_budget_goal = Transaction.objects.get(pk=pk).budget_goal
            
            new_amount = Decimal(str(form.cleaned_data.get('amount')))
            new_type = form.cleaned_data.get('transaction_type')
            new_budget_goal = form.cleaned_data.get('budget_goal')
            
            transaction_obj = form.save(commit=False)
            
            if not form.cleaned_data.get('category'):
                transaction_obj.category = None
            
            account = transaction_obj.account
            
            # Cofnij starą transakcję
            if old_budget_goal:
                if old_type == 'EXPENSE':
                    old_budget_goal.balance += old_amount
                else:
                    old_budget_goal.balance -= old_amount
                old_budget_goal.save()
            else:
                if old_type == 'EXPENSE':
                    account.balance += old_amount
                else:
                    account.balance -= old_amount
            
            # Zastosuj nową transakcję
            if new_budget_goal:
                if new_type == 'EXPENSE':
                    new_budget_goal.balance -= new_amount
                else:
                    new_budget_goal.balance += new_amount
                new_budget_goal.save()
            else:
                if new_type == 'EXPENSE':
                    account.balance -= new_amount
                else:
                    account.balance += new_amount
            
            account.save()
            transaction_obj.save()
            
            return redirect('transaction_detail', pk=pk)
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    
    context = {
        'form': form, 
        'transaction': transaction,
    }
    return render(request, 'transactions/edit_transaction.html', context)


def get_budget_goals(request):
    """AJAX endpoint - zwraca cele budżetowe dla wybranego konta"""
    
    # Sprawdzenie czy użytkownik jest zalogowany (bez redirect)
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    
    try:
        account_id = request.GET.get('account_id')
        
        if not account_id:
            return JsonResponse([], safe=False)
        
        # Pobierz cele budżetowe dla wybranego konta i zalogowanego użytkownika
        goals = list(BudgetGoal.objects.filter(
            user=request.user,
            account_id=account_id
        ).values('id', 'name', 'balance'))
        
        # Konwertuj Decimal na float
        for goal in goals:
            goal['balance'] = float(goal['balance'])
        
        return JsonResponse(goals, safe=False)
    except Exception as e:
        print(f"DEBUG: Exception: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)