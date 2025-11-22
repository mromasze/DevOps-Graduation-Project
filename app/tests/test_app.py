import pytest
import sys
import os

# Dodaj katalog nadrzędny do ścieżki
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Ustaw zmienną środowiskową PRZED importem
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from src.app import app, db, User, Task, Product


# Test 1: Test jednostkowy - model User
def test_user_model(app_context):
    """Test tworzenia i walidacji modelu User"""
    user = User(name="Jan Kowalski", email="jan@example.com")

    assert user.name == "Jan Kowalski"
    assert user.email == "jan@example.com"
    assert user.id is None  # Przed zapisem do bazy

    # Zapisz do bazy
    db.session.add(user)
    db.session.commit()

    # Po zapisie powinien mieć ID
    assert user.id is not None

    # Test metody to_dict
    user_dict = user.to_dict()
    assert "name" in user_dict
    assert "email" in user_dict
    assert user_dict["name"] == "Jan Kowalski"
    assert user_dict["email"] == "jan@example.com"


# Test 2: Test endpointu HTTP - /health
def test_health_endpoint(client):
    """Test endpointu health check"""
    response = client.get('/health')
    assert response.status_code == 200

    data = response.get_json()
    assert data['status'] == 'ok'
    assert 'database' in data
    assert data['database'] == 'connected'


# Test 3: Test logiki aplikacji - CRUD na Users
def test_users_crud_logic(client):
    """Test pełnej logiki CRUD dla użytkowników"""
    # CREATE - utworzenie użytkownika
    response = client.post('/users',
                           json={
                               'name': 'Test User',
                               'email': 'test@example.com'
                           },
                           content_type='application/json'
                           )
    assert response.status_code == 201

    created_user = response.get_json()
    assert created_user['name'] == 'Test User'
    assert created_user['email'] == 'test@example.com'
    assert 'id' in created_user
    user_id = created_user['id']

    # READ - pobranie wszystkich użytkowników
    response = client.get('/users')
    assert response.status_code == 200

    users = response.get_json()
    assert len(users) == 1
    assert users[0]['name'] == 'Test User'

    # READ - pobranie pojedynczego użytkownika
    response = client.get(f'/users/{user_id}')
    assert response.status_code == 200
    user = response.get_json()
    assert user['email'] == 'test@example.com'
    assert user['name'] == 'Test User'


# Test 4: Test endpointu index
def test_index_endpoint(client):
    """Test głównego endpointu API"""
    response = client.get('/')
    assert response.status_code == 200

    data = response.get_json()
    assert 'message' in data
    assert 'endpoints' in data
    assert data['message'] == 'Flask API is running'

    # Sprawdź czy wszystkie endpointy są wymienione
    endpoints = data['endpoints']
    assert 'health' in endpoints
    assert 'users' in endpoints
    assert 'tasks' in endpoints
    assert 'products' in endpoints


# Test 5: Test relacji między modelami
def test_user_task_relationship(client):
    """Test relacji User-Task"""
    # Utwórz użytkownika
    response = client.post('/users',
                           json={
                               'name': 'Anna Nowak',
                               'email': 'anna@example.com'
                           },
                           content_type='application/json'
                           )
    assert response.status_code == 201
    user = response.get_json()

    # Utwórz zadanie dla użytkownika
    response = client.post('/tasks',
                           json={
                               'title': 'Zrobić zakupy',
                               'completed': False,
                               'user_id': user['id']
                           },
                           content_type='application/json'
                           )
    assert response.status_code == 201

    task = response.get_json()
    assert task['user_id'] == user['id']
    assert task['title'] == 'Zrobić zakupy'
    assert task['completed'] is False


# Test 6: Test Products endpoint
def test_products_endpoint(client):
    """Test operacji na produktach"""
    # CREATE
    response = client.post('/products',
                           json={
                               'name': 'Laptop',
                               'price': 2999.99,
                               'stock': 10
                           },
                           content_type='application/json'
                           )
    assert response.status_code == 201

    product = response.get_json()
    assert product['name'] == 'Laptop'
    assert product['price'] == 2999.99
    assert product['stock'] == 10

    # READ - pobranie wszystkich produktów
    response = client.get('/products')
    assert response.status_code == 200
    products = response.get_json()
    assert len(products) == 1
    assert products[0]['name'] == 'Laptop'


# Test 7: Test Task model
def test_task_model(app_context):
    """Test modelu Task"""
    task = Task(title="Testowe zadanie", completed=False)

    assert task.title == "Testowe zadanie"
    assert task.completed is False
    assert task.user_id is None

    db.session.add(task)
    db.session.commit()

    assert task.id is not None

    task_dict = task.to_dict()
    assert task_dict['title'] == "Testowe zadanie"
    assert task_dict['completed'] is False


# Test 8: Test Product model
def test_product_model(app_context):
    """Test modelu Product"""
    product = Product(name="Test Product", price=99.99, stock=5)

    assert product.name == "Test Product"
    assert product.price == 99.99
    assert product.stock == 5

    db.session.add(product)
    db.session.commit()

    assert product.id is not None

    product_dict = product.to_dict()
    assert product_dict['name'] == "Test Product"
    assert product_dict['price'] == 99.99


# Test 9: Test update task
def test_update_task(client):
    """Test aktualizacji zadania"""
    # Utwórz zadanie
    response = client.post('/tasks',
                           json={
                               'title': 'Zadanie do zrobienia',
                               'completed': False
                           },
                           content_type='application/json'
                           )
    assert response.status_code == 201
    task = response.get_json()
    task_id = task['id']

    # Zaktualizuj zadanie (oznacz jako zakończone)
    response = client.put(f'/tasks/{task_id}',
                          json={'completed': True},
                          content_type='application/json'
                          )
    assert response.status_code == 200

    updated_task = response.get_json()
    assert updated_task['completed'] is True
    assert updated_task['title'] == 'Zadanie do zrobienia'
