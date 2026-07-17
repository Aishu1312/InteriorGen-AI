"""
prompt_builder.py
------------------
Converts structured Design Generator selections (room type, theme,
furniture style, lighting, materials, etc.) plus optional free-text
description into a single optimized, photorealistic prompt suitable
for both an LLM "refine this brief" pass and downstream image
generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


QUALITY_BOOSTERS = [
    "ultra realistic",
    "photorealistic",
    "architectural visualization",
    "8K resolution",
    "cinematic lighting",
    "professional interior photography",
    "highly detailed textures",
    "sharp focus",
]


@dataclass
class DesignOptions:
    room_type: str = "Living Room"
    color_theme: str = "Modern"
    furniture_style: str = "Modern"
    lighting: str = "Warm"
    large_windows: bool = True
    ceiling: str = "Modern"
    wall_material: str = "Paint"
    floor: str = "Wood"
    plants: str = "Indoor"
    decorations: list[str] = field(default_factory=list)
    budget: str = "Premium"
    custom_description: str = ""


def _material_phrase(options: DesignOptions) -> str:
    parts = [
        f"{options.floor.lower()} flooring",
        f"{options.wall_material.lower()} walls",
        f"{options.ceiling.lower()} style ceiling",
    ]
    return ", ".join(parts)


def build_image_prompt(options: DesignOptions) -> str:
    """Assemble the final optimized prompt sent to the image generation service."""
    segments: list[str] = []

    segments.append(
        f"Create an ultra realistic interior design of a {options.budget.lower()} "
        f"{options.color_theme.lower()} {options.room_type.lower()}"
    )

    if options.custom_description.strip():
        segments.append(f"incorporating: {options.custom_description.strip()}")

    segments.append(_material_phrase(options))
    segments.append(f"{options.furniture_style.lower()} furniture")

    if options.large_windows:
        segments.append("large floor-to-ceiling windows with natural view")

    lighting_map = {
        "Warm": "warm ambient lighting",
        "Cool": "cool toned lighting",
        "Natural": "soft natural daylight",
        "Golden": "golden hour lighting",
        "LED": "modern LED accent lighting",
    }
    segments.append(lighting_map.get(options.lighting, "warm ambient lighting"))

    if options.plants and options.plants != "None":
        segments.append(f"{options.plants.lower()} plants for greenery")

    if options.decorations:
        segments.append("featuring " + ", ".join(d.lower() for d in options.decorations))

    prompt_body = ", ".join(segments)
    boosters = ", ".join(QUALITY_BOOSTERS)
    return f"{prompt_body}, {boosters}."


def build_llm_refinement_instructions(options: DesignOptions, base_prompt: str) -> str:
    """
    Instructions given to the Groq LLM to refine/expand the structured
    prompt into a vivid, well-composed paragraph before it is sent to the
    image generation backend.
    """
    return (
        "You are a senior interior designer and prompt engineer for a "
        "photorealistic architectural visualization AI. Rewrite the "
        "following design brief into a single, vivid, tightly-written "
        "paragraph (max 120 words) that an image generation model can use "
        "to produce a stunning, photorealistic result. Preserve every "
        "material, furniture, and lighting detail mentioned. Do not add "
        "commentary, headings, or explanations — output only the final "
        "prompt paragraph.\n\n"
        f"Design brief:\n{base_prompt}"
    )


ROOM_TYPES = [
    "Living Room", "Bedroom", "Kitchen", "Bathroom", "Dining Room", "Office",
    "Balcony", "Kids Room", "Gaming Room", "Studio Apartment", "Hall", "Villa",
    "Farmhouse", "Cafe", "Restaurant", "Hotel Lobby", "Office Cabin",
    "Conference Room", "Luxury Penthouse",
]

COLOR_THEMES = [
    "Light", "Dark", "Wood", "Minimal", "Luxury", "Royal", "Modern",
    "Industrial", "Vintage", "Scandinavian", "Japanese", "Boho", "Mediterranean",
    "Traditional",
]

FURNITURE_STYLES = ["Modern", "Classic", "Luxury", "Minimal", "Wooden", "Industrial", "Rustic"]
LIGHTING_OPTIONS = ["Warm", "Cool", "Natural", "Golden", "LED"]
CEILING_OPTIONS = ["POP", "Wood", "Modern", "Concrete"]
WALL_MATERIALS = ["Paint", "Wood", "Marble", "Stone", "Wallpaper"]
FLOOR_OPTIONS = ["Marble", "Wood", "Tiles", "Granite", "Concrete"]
PLANT_OPTIONS = ["Indoor", "Outdoor", "None"]
DECORATION_OPTIONS = [
    "Curtains", "Paintings", "Mirror", "Bookshelf", "TV Unit", "Fireplace",
    "Carpet", "Indoor Garden", "Aquarium",
]
BUDGET_OPTIONS = ["Low", "Medium", "Premium", "Luxury", "Ultra Luxury"]
