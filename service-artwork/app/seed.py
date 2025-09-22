# run: docker compose run --rm artwork python app/seed.py
from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

sample = [
    {"title": "Sunset", "description": "Vivid sunset painting", "price": 100.0, "owner": "artist1"},
    {"title": "Cityscape", "description": "Night city", "price": 250.0, "owner": "artist1"},
]

for s in sample:
    existing = db.query(models.Artwork).filter(models.Artwork.title == s["title"]).first()
    if existing:
        print(f"Artwork {s['title']} exists, skipping")
        continue
    a = models.Artwork(title=s["title"], description=s["description"], price=s["price"], owner=s["owner"])
    db.add(a)
    db.commit()
    db.refresh(a)
    print(f"Seeded artwork id={a.id} title={a.title}")

db.close()
print("Artwork seeding complete.")
