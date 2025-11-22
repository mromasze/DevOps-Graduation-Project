import pytest
from app.src.app import app, db, User, Task, Product


@pytest.fixture
def client():
    """Fixture tworzący klienta testowego z bazą w pamięci"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


# Test 1: Test jednostkowy - model User
def test_user_model():
    """Test tworzenia i walidacji modelu User"""
    user = User(name="Jan Kowalski", email="jan@example.com")

    assert user.name == "Jan Kowalski"
    assert user.email == "jan@example.com"
    assert user.id is None  # Przed zapisem do bazy

    user_dict = user.to_dict()
    assert "name" in user_dict
    assert "email" in user_dict
    assert user_dict["name"] == "Jan Kowalski"


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
    response = client.post('/users', json={
        'name': 'Test User',
        'email': 'test@example.com'
    })
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


# Test 4 (bonus): Test endpointu index
def test_index_endpoint(client):
    """Test głównego endpointu API"""
    response = client.get('/')
    assert response.status_code == 200

    data = response.get_json()
    assert 'message' in data
    assert 'endpoints' in data
    assert '/health' in str(data['endpoints'])


# Test 5 (bonus): Test relacji między modelami
def test_user_task_relationship(client):
    """Test relacji User-Task"""
    # Utwórz użytkownika
    response = client.post('/users', json={
        'name': 'Anna Nowak',
        'email': 'anna@example.com'
    })
    user = response.get_json()

    # Utwórz zadanie dla użytkownika
    response = client.post('/tasks', json={
        'title': 'Zrobić zakupy',
        'completed': False,
        'user_id': user['id']
    })
    assert response.status_code == 201

    task = response.get_json()
    assert task['user_id'] == user['id']
    assert task['title'] == 'Zrobić zakupy'


# Test 6 (bonus): Test Products endpoint
def test_products_endpoint(client):
    """Test operacji na produktach"""
    response = client.post('/products', json={
        'name': 'Laptop',
        'price': 2999.99,
        'stock': 10
    })
    assert response.status_code == 201

    product = response.get_json()
    assert product['name'] == 'Laptop'
    assert product['price'] == 2999.99
    assert product['stock'] == 10

    # Pobranie wszystkich produktów
    response = client.get('/products')
    assert response.status_code == 200
    products = response.get_json()
    assert len(products) == 1
