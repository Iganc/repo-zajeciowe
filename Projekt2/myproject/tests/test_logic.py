import unittest
from app import app
from models import db, User, Repository

class PyGitTestCase(unittest.TestCase):
    def setUp(self):
        """Konfiguracja środowiska testowego przed każdym testem."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Czyszczenie bazy po każdym teście."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_registration_success(self):
        """Testuje poprawną rejestrację użytkownika[cite: 44, 47]."""
        response = self.client.post('/register', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Konto stworzone', response.data)

    def test_login_required_protection(self):
        """Sprawdza, czy dostęp do Dashboardu jest chroniony logowaniem."""
        response = self.client.get('/', follow_redirects=True)
        self.assertIn(b'Logowanie', response.data)

    def test_database_model_repository(self):
        """Testuje integrację z bazą danych (Create w CRUD)."""
        with app.app_context():
            user = User(username="dev", password="hash")
            db.session.add(user)
            db.session.commit()
            
            repo = Repository(name="TestProject", folder_name="dev_test", user_id=user.id)
            db.session.add(repo)
            db.session.commit()
            
            saved_repo = Repository.query.filter_by(name="TestProject").first()
            self.assertIsNotNone(saved_repo)
            self.assertEqual(saved_repo.user_id, user.id)

    def test_error_404_template(self):
        """Testuje obsługę błędów 404 zgodnie z wymaganiami."""
        response = self.client.get('/nieistniejaca-strona-123')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404', response.data)