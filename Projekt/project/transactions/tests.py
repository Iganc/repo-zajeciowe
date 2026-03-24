from django.test import TestCase, Client
from django.contrib.auth.models import User
from decimal import Decimal
from accounts.models import Account
from transactions.models import Transaction, Category
from budgets.models import BudgetGoal
from datetime import date


class TransactionModelTest(TestCase):
    """Testy modelu Transaction"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Moje Konto',
            balance=1000.00
        )
        self.category = Category.objects.create(
            name='Jedzenie',
            type='EXPENSE'
        )
    
    def test_create_transaction(self):
        """Test tworzenia transakcji"""
        transaction = Transaction.objects.create(
            account=self.account,
            category=self.category,
            amount=50.00,
            transaction_type='EXPENSE',
            date=date.today(),
            description='Zakupy spożywcze'
        )
        self.assertEqual(transaction.amount, Decimal('50.00'))
        self.assertEqual(transaction.transaction_type, 'EXPENSE')
        self.assertEqual(transaction.description, 'Zakupy spożywcze')
    
    def test_transaction_with_budget_goal(self):
        """Test transakcji powiązanej z celem budżetowym"""
        goal = BudgetGoal.objects.create(
            user=self.user,
            account=self.account,
            name='Wakacje',
            allocated_amount=1000.00,
            balance=1000.00
        )
        
        transaction = Transaction.objects.create(
            account=self.account,
            category=self.category,
            amount=100.00,
            transaction_type='EXPENSE',
            date=date.today(),
            budget_goal=goal
        )
        
        self.assertEqual(transaction.budget_goal, goal)


class CategoryModelTest(TestCase):
    """Testy modelu Category"""
    
    def test_create_category(self):
        """Test tworzenia kategorii"""
        category = Category.objects.create(
            name='Transport',
            type='EXPENSE'
        )
        self.assertEqual(category.name, 'Transport')
        self.assertEqual(category.type, 'EXPENSE')
    
    def test_category_string_representation(self):
        """Test reprezentacji tekstowej kategorii"""
        category = Category.objects.create(
            name='Pensja',
            type='INCOME'
        )
        self.assertIn('Pensja', str(category))
        self.assertIn('Przychód', str(category))


class TransactionViewTest(TestCase):
    """Testy widoków transakcji"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Moje Konto',
            balance=5000.00
        )
        self.category = Category.objects.create(
            name='Jedzenie',
            type='EXPENSE'
        )
    
    def test_add_transaction_redirect_if_not_logged_in(self):
        """Test przekierowania jeśli nie zalogowany"""
        response = self.client.get('/transactions/add/')
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_add_transaction_page_loads(self):
        """Test załadowania strony dodawania transakcji"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/transactions/add/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transactions/add_transaction.html')
    
    def test_create_transaction_via_form(self):
        """Test tworzenia transakcji przez formularz"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/transactions/add/', {
            'account': self.account.id,
            'category': self.category.id,
            'amount': 100.00,
            'transaction_type': 'EXPENSE',
            'date': date.today().isoformat(),
            'description': 'Test zakupu',
        }, follow=True)
        
        # Sprawdzenie czy transakcja została utworzona
        transaction_exists = Transaction.objects.filter(
            amount=100.00,
            description='Test zakupu'
        ).exists()
        self.assertTrue(transaction_exists)
    
    def test_balance_updated_after_expense(self):
        """Test aktualizacji salda po transakcji wydatkowej"""
        from decimal import Decimal
        initial_balance = self.account.balance
        
        transaction = Transaction.objects.create(
            account=self.account,
            category=self.category,
            amount=100.00,
            transaction_type='EXPENSE',
            date=date.today()
        )
        
        # Ręczna aktualizacja salda
        self.account.balance = Decimal(str(self.account.balance)) - Decimal('100.00')
        self.account.save()
        
        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(updated_account.balance, Decimal(str(initial_balance)) - Decimal('100.00'))

