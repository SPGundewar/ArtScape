# run: docker compose run --rm artwork python app/seed.py
from database import SessionLocal, engine
import models


models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

sample = [
    # ---- Vincent Van Gogh ----
    {"title": "Golden Sunset Over Ocean", "description": "A warm-toned oil painting capturing the sun dipping into the sea with glowing reflections.", "price": 180.0, "owner": "vincent_van_gogh"},
    {"title": "Midnight Cityscape", "description": "Detailed urban skyline at night with neon reflections on glass buildings.", "price": 450.0, "owner": "vincent_van_gogh"},
    {"title": "Rustic Countryside", "description": "Pastel painting of rolling hills, a red barn, and golden fields under a clear sky.", "price": 220.0, "owner": "vincent_van_gogh"},
    {"title": "Abstract Dreams", "description": "Bold brushstrokes of crimson, teal, and gold on textured canvas.", "price": 320.0, "owner": "vincent_van_gogh"},
    {"title": "Winter Forest Path", "description": "Snow-covered trees lining a winding trail, painted in soft watercolors.", "price": 270.0, "owner": "vincent_van_gogh"},
    {"title": "Harbor at Dawn", "description": "Fishing boats resting on calm waters as the sun rises.", "price": 310.0, "owner": "vincent_van_gogh"},
    {"title": "Silent Desert", "description": "Acrylic painting of sand dunes with dramatic shadows under moonlight.", "price": 280.0, "owner": "vincent_van_gogh"},
    {"title": "Mountain Reflections", "description": "Snow-capped peaks mirrored in a crystal-clear alpine lake.", "price": 500.0, "owner": "vincent_van_gogh"},

    # ---- Frida Kahlo ----
    {"title": "Blooming Lotus", "description": "Delicate lotus flowers on a pond, painted with ink and watercolor.", "price": 150.0, "owner": "frida_kahlo"},
    {"title": "Whispers of Autumn", "description": "Golden leaves scattered on a stone path, impressionist style.", "price": 200.0, "owner": "frida_kahlo"},
    {"title": "Jazz in Motion", "description": "Dynamic abstract representing the rhythm of a saxophone solo.", "price": 340.0, "owner": "frida_kahlo"},
    {"title": "Street Market Colors", "description": "Vibrant depiction of a crowded bazaar with food stalls and fabrics.", "price": 420.0, "owner": "frida_kahlo"},
    {"title": "Ocean’s Fury", "description": "Dramatic seascape of waves crashing against jagged cliffs.", "price": 390.0, "owner": "frida_kahlo"},
    {"title": "Mediterranean Courtyard", "description": "A sunlit stone courtyard with climbing vines and rustic doors.", "price": 260.0, "owner": "frida_kahlo"},
    {"title": "Moonlit Bridge", "description": "An arched bridge glowing under soft moonlight and mist.", "price": 310.0, "owner": "frida_kahlo"},
    {"title": "Carnival Night", "description": "Bright Ferris wheel lights and colorful stalls in a festival setting.", "price": 360.0, "owner": "frida_kahlo"},
    {"title": "Old Library", "description": "Detailed sketch of towering wooden shelves filled with books.", "price": 180.0, "owner": "frida_kahlo"},

    # ---- Pablo Picasso ----
    {"title": "Digital Horizons", "description": "Futuristic digital art showing neon landscapes and glowing skies.", "price": 400.0, "owner": "pablo_picasso"},
    {"title": "Cubist Portrait", "description": "Geometric cubist-style face in muted blues and ochres.", "price": 600.0, "owner": "pablo_picasso"},
    {"title": "Fragmented Still Life", "description": "Broken shapes forming a fruit bowl with bottles in cubist abstraction.", "price": 480.0, "owner": "pablo_picasso"},
    {"title": "Harmony in Chaos", "description": "Mixed-media piece layering ink, acrylic, and pencil strokes in controlled disorder.", "price": 530.0, "owner": "pablo_picasso"},
    {"title": "Bullfight Motion", "description": "Energetic strokes depicting a matador and bull in abstract style.", "price": 700.0, "owner": "pablo_picasso"},
    {"title": "The Guitar Player", "description": "Cubist interpretation of a musician playing guitar, angular shapes and muted tones.", "price": 650.0, "owner": "pablo_picasso"},
    {"title": "Broken Reflections", "description": "Surreal depiction of a mirror fractured into dreamlike fragments.", "price": 720.0, "owner": "pablo_picasso"},
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
