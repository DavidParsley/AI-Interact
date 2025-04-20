from models import Users, Session, engine, Base
from auth import hash_password

print("⚠️ Dropping existing tables...")
Base.metadata.drop_all(bind=engine)
print("✅ Tables dropped.")

print("📦 Creating new tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created.")

db = Session()

def seed():
    users = [
        Users(name="Dave", email="dave@example.com", password=hash_password("1234")),
        Users(name="Anne", email="anne@example.com", password=hash_password("1234")),
        Users(name="Hamza", email="hamza@example.com", password=hash_password("1234")),
    ]

    db.add_all(users)
    db.commit()

    for user in users:
        db.refresh(user)
        print(f"🚀 Seeded user: {user.name} - {user.email}")

if __name__ == "__main__":
    seed()
