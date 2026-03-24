from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from decimal import Decimal
from .models import BudgetGoal, RecurringPayment
from accounts.models import Account
from transactions.models import Transaction
from .forms import BudgetGoalForm

@login_required
def budget_list(request):
    """Lista wszystkich celów budżetowych użytkownika"""
    # Pobierz cele dla zalogowanego użytkownika
    budget_goals = BudgetGoal.objects.filter(user=request.user)
    
    # Oblicz postęp dla każdego celu
    for goal in budget_goals:
        # Ilość pieniędzy wydanych z celu
        spent = goal.transactions.filter(transaction_type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        goal.current_amount = spent
        goal.progress_percent = min(int((spent / goal.allocated_amount) * 100), 100) if goal.allocated_amount > 0 else 0
        goal.remaining = goal.balance  # balance jest bieżącą kwotą na celu
    
    context = {
        'budget_goals': budget_goals,
    }
    return render(request, 'budgets/budget_list.html', context)

@login_required
def budget_detail(request, pk):
    """Szczegóły celu budżetowego"""
    goal = get_object_or_404(BudgetGoal, pk=pk, user=request.user)
    
    # Ilość pieniędzy wydanych z celu
    spent = goal.transactions.filter(transaction_type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    goal.current_amount = spent
    goal.progress_percent = min(int((spent / goal.allocated_amount) * 100), 100) if goal.allocated_amount > 0 else 0
    goal.remaining = goal.balance
    
    # Transakcje przypisane do tego celu
    transactions = goal.transactions.all().order_by('-date')[:10]
    
    context = {
        'goal': goal,
        'transactions': transactions,
    }
    return render(request, 'budgets/budget_detail.html', context)

@login_required
def budget_create(request):
    """Tworzenie nowego celu budżetowego"""
    
    if request.method == "POST":
        form = BudgetGoalForm(request.POST, user=request.user)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.balance = goal.allocated_amount  # Ustaw początkowe saldo = alokowana kwota
            goal.save()
            
            # Zabierz pieniądze z konta
            account = goal.account
            account.balance -= goal.allocated_amount
            account.save()
            
            return redirect('budget_detail', pk=goal.pk)
    else:
        form = BudgetGoalForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Nowy cel budżetowy',
    }
    return render(request, 'budgets/budget_form.html', context)

@login_required
def budget_edit(request, pk):
    """Edycja celu budżetowego"""
    goal = get_object_or_404(BudgetGoal, pk=pk, user=request.user)
    old_allocated = goal.allocated_amount
    old_balance = goal.balance
    
    if request.method == "POST":
        form = BudgetGoalForm(request.POST, instance=goal, user=request.user)
        if form.is_valid():
            goal = form.save(commit=False)
            
            # Jeśli zmieniono alokowaną kwotę
            if goal.allocated_amount != old_allocated:
                # Różnica do zwrotu lub dodania
                difference = goal.allocated_amount - old_allocated  # może być ujemna
                
                # Zaktualizuj balance proporcjonalnie
                if old_allocated > 0:
                    # Zaoszczędzono
                    spent = old_allocated - old_balance
                    goal.balance = goal.allocated_amount - spent
                else:
                    goal.balance = goal.allocated_amount
                
                # Zwróć / zabierz z konta
                account = goal.account
                account.balance -= difference
                account.save()
            
            goal.save()
            return redirect('budget_detail', pk=goal.pk)
    else:
        form = BudgetGoalForm(instance=goal, user=request.user)
    
    context = {
        'form': form,
        'goal': goal,
        'title': f'Edytuj: {goal.name}',
    }
    return render(request, 'budgets/budget_form.html', context)

@login_required
def budget_delete(request, pk):
    """Usuwanie celu budżetowego"""
    goal = get_object_or_404(BudgetGoal, pk=pk, user=request.user)
    
    if request.method == "POST":
        # Zwróć pieniądze na konto
        account = goal.account
        account.balance += goal.balance  # Zwróć to co zostało na celu
        account.save()
        
        goal.delete()
        return redirect('budget_list')
    
    context = {
        'goal': goal,
    }
    return render(request, 'budgets/budget_confirm_delete.html', context)
