import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from database import db, create_document, get_documents
from schemas import Hero, Project, Simulator, About, Skill, Resume, Contact, Theme, SEO

app = FastAPI(title="Souradeep CMS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility

def collection_name(model_cls):
    return model_cls.__name__.lower()

# Health
@app.get("/")
def read_root():
    return {"message": "Souradeep CMS API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Generic getters
@app.get("/api/hero", response_model=List[Hero])
def get_hero():
    return get_documents(collection_name(Hero))

@app.get("/api/projects", response_model=List[Project])
def get_projects():
    return get_documents(collection_name(Project))

@app.get("/api/simulators", response_model=List[Simulator])
def get_simulators():
    return get_documents(collection_name(Simulator))

@app.get("/api/about", response_model=List[About])
def get_about():
    return get_documents(collection_name(About))

@app.get("/api/skills", response_model=List[Skill])
def get_skills():
    return get_documents(collection_name(Skill))

@app.get("/api/resume", response_model=List[Resume])
def get_resume():
    return get_documents(collection_name(Resume))

@app.get("/api/contact", response_model=List[Contact])
def get_contact():
    return get_documents(collection_name(Contact))

@app.get("/api/theme", response_model=List[Theme])
def get_theme():
    return get_documents(collection_name(Theme))

@app.get("/api/seo", response_model=List[SEO])
def get_seo():
    return get_documents(collection_name(SEO))

# Minimal Admin endpoints (no auth for demo; can be extended later)
class UpsertPayload(BaseModel):
    data: dict

@app.post("/admin/upsert/{model}")
def upsert_model(model: str, payload: UpsertPayload):
    model = model.lower()
    valid = {m.__name__.lower(): m for m in [Hero, Project, Simulator, About, Skill, Resume, Contact, Theme, SEO]}
    if model not in valid:
        raise HTTPException(status_code=400, detail="Invalid model")
    inserted_id = create_document(model, payload.data)
    return {"inserted_id": inserted_id}

# File upload for resume or images
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/admin/upload")
def upload_file(file: UploadFile = File(...), kind: str = Form("asset")):
    filename = file.filename
    dest_path = os.path.join(UPLOAD_DIR, filename)
    with open(dest_path, "wb") as f:
        f.write(file.file.read())
    url = f"/uploads/{filename}"
    # If resume, also create a Resume doc that references local URL (can be served statically)
    if kind == "resume":
        create_document(collection_name(Resume), {"url": url})
    return {"url": url}

@app.get("/uploads/{filename}")
def serve_upload(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)

# Preload initial content if empty
@app.post("/admin/seed")
def seed_content():
    created = {}
    def ensure_one(model_cls, data_list: list):
        col = collection_name(model_cls)
        if db[col].count_documents({}) == 0:
            for d in data_list:
                create_document(col, d)
            created[col] = len(data_list)
    # Hero
    ensure_one(Hero, [{
        "title": "Souradeep Das",
        "subtitle": "Physics • Astrophysics • Quantum Mechanics",
        "ctas": ["View Projects", "Explore Simulators", "Download Resume"],
        "quotes": [
            "Love is the one thing that transcends time and space.",
            "Do not go gentle into that good night.",
            "Mankind was born on Earth. It was never meant to die here."
        ],
        "featured": ["black-hole", "quantum-wave"],
        "background_animations": ["spline-cover", "stars", "nebula", "lens"]
    }])
    # Projects
    ensure_one(Project, [
        {"title": "Quantum Wave Simulator", "description": "Interactive exploration of wave interference.", "tags": ["quantum", "simulation"], "category": "Quantum"},
        {"title": "Black Hole Visualizer", "description": "Accretion disk and lensing demo.", "tags": ["gr","relativity"], "category": "Astro"},
        {"title": "Stellar Evolution Model", "description": "Lifecycle of stars.", "tags": ["stellar", "evolution"], "category": "Astro"},
        {"title": "Cosmology Visualization", "description": "Expanding universe graphics.", "tags": ["cosmology"], "category": "Cosmo"},
        {"title": "Particle Sandbox", "description": "Forces and collisions.", "tags": ["particles"], "category": "Physics"},
        {"title": "Quantum ML Prototype", "description": "Hybrid quantum-classical ML.", "tags": ["quantum", "ml"], "category": "Quantum"}
    ])
    # Simulators
    ensure_one(Simulator, [
        {"name": "Quantum Wave / Double Slit", "description": "Wave interference", "parameters": [
            {"key": "wavelength", "label": "Wavelength", "min": 0.2, "max": 5, "step": 0.1, "value": 1.0},
            {"key": "slit_distance", "label": "Slit Distance", "min": 0.1, "max": 2, "step": 0.05, "value": 0.5}
        ]},
        {"name": "Black Hole Lensing Sandbox", "description": "Simple photon ring lensing", "parameters": [
            {"key": "mass", "label": "Mass", "min": 0.1, "max": 10, "step": 0.1, "value": 1.0}
        ]},
        {"name": "Harmonic Oscillator", "description": "Oscillation demo", "parameters": [
            {"key": "k", "label": "k", "min": 0.1, "max": 10, "step": 0.1, "value": 1.0},
            {"key": "m", "label": "m", "min": 0.1, "max": 10, "step": 0.1, "value": 1.0}
        ]},
        {"name": "Particle Sandbox", "description": "Particles under gravity", "parameters": [
            {"key": "count", "label": "Count", "min": 10, "max": 500, "step": 10, "value": 100}
        ]},
        {"name": "Stellar Lifecycle Demo", "description": "From protostar to supernova", "parameters": []},
        {"name": "Orbital System (2/3-body)", "description": "Simplified orbits", "parameters": [
            {"key": "bodies", "label": "Bodies", "min": 2, "max": 3, "step": 1, "value": 2}
        ]}
    ])
    # About
    ensure_one(About, [{
        "bio": "Physicist exploring the cosmos, quantum phenomena, and computational models.",
        "journey": [
            {"year": "2016", "title": "Began Physics Journey", "description": "Foundations in mechanics and electromagnetism"},
            {"year": "2020", "title": "Astrophysics Research", "description": "Black hole accretion studies"},
            {"year": "2024", "title": "Quantum ML", "description": "Hybrid models for quantum data"}
        ],
        "images": []
    }])
    # Skills
    ensure_one(Skill, [
        {"category": "Physics", "chips": ["Quantum", "Relativity", "Astrophysics"], "icon": "atom", "color": "#60A5FA"},
        {"category": "Programming", "chips": ["Python", "JS", "NumPy", "PyTorch"], "icon": "code", "color": "#A78BFA"}
    ])
    # Contact
    ensure_one(Contact, [{
        "email": "souradeep897@gmail.com",
        "socials": ["https://github.com/", "https://twitter.com/"],
        "metadata": {"location": "Earth"}
    }])
    # Theme
    ensure_one(Theme, [{
        "primary_color": "#00E5FF",
        "accent_color": "#A78BFA",
        "background_variant": "dark",
        "animation_intensity": 4
    }])
    # SEO
    ensure_one(SEO, [
        {"page": "home", "title": "Souradeep Das — Physics", "description": "Interstellar portfolio", "og_image": None},
        {"page": "projects", "title": "Projects", "description": "Research & simulations", "og_image": None}
    ])
    return {"created": created}

# Simple public quote-of-the-day (placeholder)
QUOTES = [
    "We must think not as individuals but as a species.",
    "Time is relative; perspective is everything.",
    "There is no such thing as a coincidence in physics — only variables we have yet to identify."
]
@app.get("/api/quote")
def quote_of_day(index: Optional[int] = None):
    if index is None:
        index = 0
    return {"quote": QUOTES[index % len(QUOTES)]}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
