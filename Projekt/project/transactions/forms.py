from django import forms
from django.utils import timezone
from .models import Transaction, Category
from budgets.models import BudgetGoal

class TransactionForm(forms.ModelForm):
    transaction_type = forms.ChoiceField(
        choices=[('EXPENSE', 'Wydatek'), ('INCOME', 'Przychód')],
        widget=forms.RadioSelect(attrs={'class': 'transaction-type-toggle'}),
        label='Typ transakcji',
        initial='EXPENSE'
    )
    
    budget_goal = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Powiąż z celem budżetowym',
        empty_label='Brak - na konto'
    )
    
    class Meta:
        model = Transaction
        fields = ['account', 'transaction_type', 'category', 'amount', 'date', 'description', 'budget_goal']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'value': timezone.now().strftime('%Y-%m-%d')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Opis transakcji (opcjonalnie)'
            }),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Ustawienie dzisiejszej daty jako domyślnej
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
        
        # Kategoria nie obowiązkowa
        self.fields['category'].required = False
        self.fields['description'].required = False
        
        # Ustaw queryset dla budget_goal na podstawie zalogowanego użytkownika
        if user:
            self.fields['budget_goal'].queryset = BudgetGoal.objects.filter(user=user)
        else:
            self.fields['budget_goal'].queryset = BudgetGoal.objects.none()
