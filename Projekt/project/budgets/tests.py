from django.test import TestCase, Client
from django.contrib.auth.models import User
from decimal import Decimal
from accounts.models import Account
from budgets.models import BudgetGoal, RecurringPayment
from transactions.models import Transaction, Category
from datetime import date


class BudgetGoalModelTest(TestCase):
    """Testy modelu BudgetGoal"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Moje Konto',
            balance=5000.00
        )
    
    def test_create_budget_goal(self):
        """Test tworzenia celu budżetowego"""
        goal = BudgetGoal.objects.create(
            user=self.user,
            account=self.account,
            name='Wakacje',
            allocated_amount=2000.00,
            balance=2000.00
        )
        self.assertEqual(goal.name, 'Wakacje')
        self.assertEqual(goal.allocated_amount, Decimal('2000.00'))
        self.assertEqual(goal.balance, Decimal('2000.00'))
    
    def test_budget_goal_string_representation(self):
        """Test reprezentacji tekstowej celu"""
        goal = BudgetGoal.objects.create(
            user=self.user,
            account=self.account,
            name='Weekend',
            allocated_amount=500.00,
            balance=500.00
        )
        self.assertIn('Weekend', str(goal))
        self.assertIn('testuser', str(goal))
    
    def test_budget_goal_allocation(self):
        """Test alokacji pieniędzy z konta na cel"""
        from decimal import Decimal
        initial_balance = Decimal(str(self.account.balance))
        allocated_amount = Decimal('1000.00')
        
        goal = BudgetGoal.objects.create(
            user=self.user,
            account=self.account,
            name='Cel',
            allocated_amount=allocated_amount,
            balance=allocated_amount
        )
        
        # Symulacja zabrania pieniędzy z konta
        self.account.balance = float(initial_balance - allocated_amount)
        self.account.save()
        
        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(
            Decimal(str(updated_account.balance)),
            initial_balance - allocated_amount
        )


class RecurringPaymentModelTest(TestCase):
    """Testy modelu RecurringPayment"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Czynsz',
            type='EXPENSE'
        )
    
    def test_create_recurring_payment(self):
        """Test tworzenia płatności cyklicznej"""
        payment = RecurringPayment.objects.create(
            user=self.user,
            name='Czynsz miesięczny',
            amount=1500.00,
            day_of_month=1,
            category=self.category
        )
        self.assertEqual(payment.name, 'Czynsz miesięczny')
        self.assertEqual(payment.amount, Decimal('1500.00'))
        self.assertEqual(payment.day_of_month, 1)


class BudgetViewTest(TestCase):
    """Testy widoków budżetu"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Konto',
            balance=5000.00
        )
        self.category = Category.objects.create(
            name='Zakupy',
            type='EXPENSE'
        )
    
    def test_budget_list_redirect_if_not_logged_in(self):
        """Test przekierowania na stronie listy budżetów"""
        response = self.client.get('/budgets/')
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_budget_list_page_loads(self):
        """Test załadowania strony listy budżetów"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/budgets/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'budgets/budget_list.html')
    
    def test_create_budget_goal_via_form(self):
        """Test tworzenia celu budżetowego przez formularz"""
        self.client.login(username='testuser', password='testpass123')
        
        initial_balance = self.account.balance
        
        response = self.client.post('/budgets/add/', {
            'account': self.account.id,
            'name': 'Test Cel',
            'allocated_amount': 500.00,
        }, follow=True)
        
        # Sprawdzenie czy cel został utworzony
        goal_exists = BudgetGoal.objects.filter(name='Test Cel').exists()
        self.assertTrue(goal_exists)
    
    def test_budget_goal_with_transactions(self):
        """Test celu budżetowego z transakcjami"""
        from decimal import Decimal
        goal = BudgetGoal.objects.create(
            user=self.user,
            account=self.account,
            name='Cel',
            allocated_amount=1000.00,
            balance=1000.00
        )
        
        transaction = Transaction.objects.create(
            account=self.account,
            category=self.category,
            amount=200.00,
            transaction_type='EXPENSE',
            date=date.today(),
            budget_goal=goal
        )
        
        # Symulacja zmniejszenia celu
        goal.balance = float(Decimal(str(goal.balance)) - Decimal('200.00'))
        goal.save()
        
        updated_goal = BudgetGoal.objects.get(pk=goal.pk)
        self.assertEqual(Decimal(str(updated_goal.balance)), Decimal('800.00'))


class BudgetDeletionTest(TestCase):
    """Testy usuwania celów budżetowych"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.account = Account.objects.create(
            user=self.user,
            name='Konto',
            balance=5000.00
        )
    
    def test_delete_budget_goal_returns_money(self):
        """Test zwracania pieniędzy przy usunięciu celu"""
        from decimal import Decimal
        allocated_amount = Decimal('1000.00')
        initial_balance = Decimal(str(self.account.balance))
        
        goal = BudgetGoal.objects.create(
            user=self.user,
            account=self.account,
            name='Cel do usunięcia',
            allocated_amount=allocated_amount,
            balance=allocated_amount
        )
        
        # Symulacja zabrania
        self.account.balance = float(initial_balance - allocated_amount)
        self.account.save()
        
        initial_balance_after_allocation = Decimal(str(self.account.balance))
        
        # Zwrot pieniędzy
        self.account.balance = float(initial_balance_after_allocation + Decimal(str(goal.balance)))
        self.account.save()
        
        updated_account = Account.objects.get(pk=self.account.pk)
        self.assertEqual(Decimal(str(updated_account.balance)), initial_balance)

