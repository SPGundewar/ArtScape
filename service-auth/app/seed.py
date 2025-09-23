# run: docker compose run --rm auth python app/seed.py
from database import SessionLocal, engine
import models, utils, auth

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

users = [
    {"username": "vincent_van_gogh", "password": "pass", "role": "artist"},
    {"username": "frida_kahlo", "password": "pass", "role": "artist"},
    {"username": "pablo_picasso", "password": "pass", "role": "artist"},
    {"username": "sarah_johnson", "password": "pass", "role": "user"},
    {"username": "michael_lee", "password": "pass", "role": "user"},
    {"username": "admin", "password": "pass", "role": "admin"},
]


for u in users:
    existing = db.query(models.User).filter(models.User.username == u["username"]).first()
    if existing:
        print(f"User {u['username']} already exists, skipping")
        continue
    user = models.User(username=u["username"], hashed_password=utils.hash_password(u["password"]), role=u["role"])
    db.add(user)
    db.commit()
    db.refresh(user)
    token = auth.create_access_token(subject=user.username, data={"role": user.role})
    print(f"Created user {user.username} with role {user.role}")
    print(f"  Token (use this): {token}\n")

db.close()
print("Auth seeding complete.")
