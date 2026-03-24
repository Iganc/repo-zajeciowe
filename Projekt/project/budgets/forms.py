from django import forms
from .models import BudgetGoal
from accounts.models import Account

class BudgetGoalForm(forms.ModelForm):
    """Formularz do dodawania i edytowania celów budżetowych"""
    
    class Meta:
        model = BudgetGoal
        fields = ['account', 'name', 'allocated_amount']
        widgets = {
            'account': forms.Select(attrs={
                'class': 'form-select',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nazwa celu (np. Wakacje, Nowy laptop)',
                'maxlength': '100',
            }),
            'allocated_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0.01',
            }),
        }
        labels = {
            'account': 'Konto',
            'name': 'Nazwa celu',
            'allocated_amount': 'Alokowana kwota (zł)',
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['account'].queryset = Account.objects.filter(user=user)
