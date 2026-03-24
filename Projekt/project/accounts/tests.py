from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounts.models import Account


class AccountModelTest(TestCase):
    """Testy modelu Account"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_account(self):
        """Test tworzenia konta"""
        account = Account.objects.create(
            user=self.user,
            name='Moj Rachunek',
            balance=1000.00
        )
        self.assertEqual(account.name, 'Moj Rachunek')
        self.assertEqual(account.balance, 1000.00)
        self.assertEqual(account.user, self.user)
    
    def test_account_str(self):
        """Test reprezentacji tekstowej konta"""
        account = Account.objects.create(
            user=self.user,
            name='Moj Rachunek',
            balance=500.00
        )
        self.assertEqual(str(account), 'Moj Rachunek - testuser')
    
    def test_account_balance_update(self):
        """Test aktualizacji salda konta"""
        account = Account.objects.create(
            user=self.user,
            name='Konto',
            balance=1000.00
        )
        account.balance -= 100
        account.save()
        
        updated_account = Account.objects.get(pk=account.pk)
        self.assertEqual(updated_account.balance, 900.00)


class RegisterViewTest(TestCase):
    """Testy widoku rejestracji"""
    
    def setUp(self):
        self.client = Client()
    
    def test_register_page_loads(self):
        """Test załadowania strony rejestracji"""
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_user_registration(self):
        """Test rejestracji użytkownika"""
        response = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123',
        }, follow=True)
        
        # Sprawdzanie czy użytkownik został utworzony
        user_exists = User.objects.filter(username='newuser').exists()
        self.assertTrue(user_exists)


class DashboardViewTest(TestCase):
    """Testy widoku panelu"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_dashboard_redirect_if_not_logged_in(self):
        """Test przekierowania jeśli nie zalogowany"""
        response = self.client.get('/', follow=True)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_dashboard_displays_if_logged_in(self):
        """Test wyświetlenia panelu po zalogowaniu"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/dashboard.html')

