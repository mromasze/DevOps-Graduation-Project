import os
import sys
import json
import csv
from datetime import datetime

# Dodaj katalog nadrzędny do ścieżki
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Teraz import będzie działał
from src.app import app, db, User, Task, Product


def seed():
    with app.app_context():
        print("Starting database seeding...")

        # Utwórz tabele (jeśli jeszcze nie istnieją)
        db.create_all()

        # Wyczyść istniejące dane (opcjonalnie)
        print("Clearing existing data...")
        Task.query.delete()
        Product.query.delete()
        User.query.delete()
        db.session.commit()

        # Seedowanie Users
        print("Seeding users...")
        users_data = [
            User(name="Jan Kowalski", email="jan@example.com"),
            User(name="Anna Nowak", email="anna@example.com"),
            User(name="Piotr Wiśniewski", email="piotr@example.com"),
            User(name="Maria Lewandowska", email="maria@example.com"),
            User(name="Krzysztof Dąbrowski", email="krzysztof@example.com"),
        ]
        db.session.add_all(users_data)
        db.session.commit()
        print(f"Created {len(users_data)} users")

        # Seedowanie Tasks
        print("Seeding tasks...")
        tasks_data = [
            Task(title="Zrobić zakupy", completed=False, user_id=1),
            Task(title="Napisać raport", completed=True, user_id=2),
            Task(title="Umówić się na spotkanie", completed=False, user_id=1),
            Task(title="Przeczytać książkę", completed=False, user_id=3),
            Task(title="Zadzwonić do klienta", completed=True, user_id=4),
        ]
        db.session.add_all(tasks_data)
        db.session.commit()
        print(f"Created {len(tasks_data)} tasks")

        # Seedowanie Products
        print("Seeding products...")
        products_data = [
            Product(name="Laptop", price=2999.99, stock=15),
            Product(name="Mysz", price=89.99, stock=50),
            Product(name="Klawiatura", price=199.99, stock=30),
            Product(name="Monitor", price=899.99, stock=20),
            Product(name="Słuchawki", price=299.99, stock=40),
        ]
        db.session.add_all(products_data)
        db.session.commit()
        print(f"Created {len(products_data)} products")

        # Utworzenie katalogu na pliki wyjściowe
        output_dir = os.path.join(parent_dir, 'seed_output')
        os.makedirs(output_dir, exist_ok=True)

        # Zapisz log
        log_path = os.path.join(output_dir, "seed.log")
        with open(log_path, "w") as f:
            f.write(f"Seed completed at: {datetime.now()}\n")
            f.write(f"Created {len(users_data)} users\n")
            f.write(f"Created {len(tasks_data)} tasks\n")
            f.write(f"Created {len(products_data)} products\n")
            f.write("\n=== Users ===\n")
            for user in users_data:
                f.write(f"ID: {user.id}, Name: {user.name}, Email: {user.email}\n")

        print(f"Log saved to: {log_path}")

        # Zapisz users do CSV
        csv_path = os.path.join(output_dir, "users.csv")
        with open(csv_path, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Name', 'Email'])
            for user in users_data:
                writer.writerow([user.id, user.name, user.email])

        print(f"CSV saved to: {csv_path}")

        # Zapisz products do JSON
        json_path = os.path.join(output_dir, "products.json")
        products_list = [p.to_dict() for p in products_data]
        with open(json_path, "w", encoding='utf-8') as jsonfile:
            json.dump(products_list, jsonfile, indent=2, ensure_ascii=False)

        print(f"JSON saved to: {json_path}")

        print("\n✅ Seeding completed successfully!")
        print(f"📁 Output directory: {output_dir}")


if __name__ == "__main__":
    seed()
