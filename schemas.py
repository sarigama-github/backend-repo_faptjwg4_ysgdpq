"""
Database Schemas for Souradeep Das — Physics | Astrophysics | Quantum Mechanics

Each Pydantic model below maps to a MongoDB collection with the lowercase class name.
Examples:
- Project -> "project"
- Simulator -> "simulator"

These schemas power the CMS and public site content.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

# THEME / SEO
class Theme(BaseModel):
    primary_color: str = Field("#6EE7F9")
    accent_color: str = Field("#A78BFA")
    background_variant: str = Field("dark", description="dark | light")
    animation_intensity: int = Field(3, ge=0, le=5)

class SEO(BaseModel):
    page: str = Field(..., description="route key like home, projects, about, skills, contact")
    title: str
    description: str
    og_image: Optional[HttpUrl] = None

# CORE CONTENT
class Hero(BaseModel):
    title: str
    subtitle: str
    ctas: List[str] = Field(default_factory=lambda: ["View Projects", "Explore Simulators"]) 
    quotes: List[str] = Field(default_factory=list)
    featured: List[str] = Field(default_factory=list)
    background_animations: List[str] = Field(default_factory=lambda: ["spline-cover", "stars", "nebula"])  

class Project(BaseModel):
    title: str
    description: str
    tags: List[str] = Field(default_factory=list)
    cover_image: Optional[HttpUrl] = None
    demo_link: Optional[HttpUrl] = None
    modal_content: Optional[str] = None
    category: Optional[str] = None

class SimulatorParameter(BaseModel):
    key: str
    label: str
    min: float
    max: float
    step: float
    value: float

class Simulator(BaseModel):
    name: str
    description: str
    parameters: List[SimulatorParameter] = Field(default_factory=list)
    demo_asset: Optional[str] = Field(None, description="URL to animation or asset")

class TimelineNode(BaseModel):
    year: str
    title: str
    description: str
    image: Optional[HttpUrl] = None

class About(BaseModel):
    bio: str
    journey: List[TimelineNode] = Field(default_factory=list)
    images: List[HttpUrl] = Field(default_factory=list)

class Skill(BaseModel):
    category: str
    chips: List[str] = Field(default_factory=list)
    icon: Optional[str] = Field(None, description="lucide icon name")
    color: Optional[str] = None

class Resume(BaseModel):
    url: HttpUrl

class Contact(BaseModel):
    email: str
    socials: List[str] = Field(default_factory=list)
    metadata: Optional[dict] = Field(default_factory=dict)
