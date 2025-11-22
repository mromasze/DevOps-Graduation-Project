from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)

# Konfiguracja bazy - priorytet dla zmiennej środowiskowej
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://flask_user:flask_password@localhost:5432/flask_docker_db'
)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Model 1: Users
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}


# Model 2: Tasks
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "user_id": self.user_id
        }


# Model 3: Products
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock
        }


# Endpoint 1: Index
@app.route("/")
def index():
    return jsonify({
        "message": "Flask API is running",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "users": "/users",
            "tasks": "/tasks",
            "products": "/products"
        }
    })


# Endpoint 2: Health check
@app.route("/health")
def health():
    try:
        # Sprawdź połączenie z bazą
        db.session.execute(db.text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({
        "status": "ok",
        "database": db_status,
        "database_url": DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else "unknown"
    })


# Endpoint 3: Users
@app.route("/users", methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        data = request.get_json()
        user = User(name=data['name'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201

    users = User.query.all()
    return jsonify([u.to_dict() for u in users])


@app.route("/users/<int:user_id>", methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


# Endpoint 4: Tasks
@app.route("/tasks", methods=['GET', 'POST'])
def tasks():
    if request.method == 'POST':
        data = request.get_json()
        task = Task(
            title=data['title'],
            completed=data.get('completed', False),
            user_id=data.get('user_id')
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201

    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks])


@app.route("/tasks/<int:task_id>", methods=['GET', 'PUT'])
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'PUT':
        data = request.get_json()
        task.completed = data.get('completed', task.completed)
        db.session.commit()

    return jsonify(task.to_dict())


# Endpoint 5: Products
@app.route("/products", methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        data = request.get_json()
        product = Product(
            name=data['name'],
            price=data['price'],
            stock=data.get('stock', 0)
        )
        db.session.add(product)
        db.session.commit()
        return jsonify(product.to_dict()), 201

    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])


@app.route("/products/<int:product_id>", methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
