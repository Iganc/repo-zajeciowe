import unittest
from app import app, db

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def test_login_page_loads(self):
        """Sprawdza czy strona logowania się wyświetla"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logowanie', response.data)

if __name__ == '__main__':
    unittest.main()