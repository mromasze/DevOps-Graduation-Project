import pytest
import sys
import os

# Dodaj katalog nadrzędny do ścieżki
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# WAŻNE: Ustaw zmienną środowiskową PRZED importem aplikacji
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from src.app import app, db

@pytest.fixture(scope='function')
def test_app():
    """Fixture dla aplikacji testowej"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

@pytest.fixture
def client(test_app):
    """Fixture tworzący klienta testowego z czystą bazą"""
    with test_app.test_client() as client:
        with test_app.app_context():
            db.create_all()
        yield client
        with test_app.app_context():
            db.session.remove()
            db.drop_all()

@pytest.fixture
def app_context(test_app):
    """Fixture dla kontekstu aplikacji z czystą bazą"""
    with test_app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()
