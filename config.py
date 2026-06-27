# config.py — Application-level constants and configuration.
# All magic strings, model names, and shared settings live here.

from typing import Final

# ---------------------------------------------------------------------------
# App Identity
# ---------------------------------------------------------------------------
APP_NAME: Final[str] = "VisioForge"
APP_TAGLINE: Final[str] = "From words to worlds — one prompt at a time."
APP_DESCRIPTION: Final[str] = (
    "A professional AI image studio powered by state-of-the-art diffusion models. "
    "Describe your vision, choose your aesthetic, and generate stunning images in seconds."
)

# ---------------------------------------------------------------------------
# Model Configuration
# ---------------------------------------------------------------------------
PRIMARY_MODEL: Final[str] = "black-forest-labs/FLUX.1-schnell"
FALLBACK_MODEL: Final[str] = "stabilityai/stable-diffusion-xl-base-1.0"

# ---------------------------------------------------------------------------
# Image Size Options
# ---------------------------------------------------------------------------
IMAGE_SIZES: Final[dict[str, tuple[int, int]]] = {
    "Square (1024 × 1024)": (1024, 1024),
    "Portrait (768 × 1024)": (768, 1024),
    "Landscape (1024 × 768)": (1024, 768),
}
DEFAULT_SIZE: Final[str] = "Square (1024 × 1024)"

# ---------------------------------------------------------------------------
# Style Definitions
# ---------------------------------------------------------------------------
STYLES: Final[list[str]] = [
    "Photorealistic",
    "Cyberpunk",
    "Anime",
    "Watercolor",
    "Oil Painting",
    "Fantasy",
    "Pixel Art",
    "Minimalist Line Art",
]
DEFAULT_STYLE: Final[str] = "Photorealistic"

# ---------------------------------------------------------------------------
# Session State Keys
# ---------------------------------------------------------------------------
SESSION_HISTORY_KEY: Final[str] = "generation_history"
SESSION_LAST_IMAGE_KEY: Final[str] = "last_image"
SESSION_LAST_META_KEY: Final[str] = "last_metadata"

# ---------------------------------------------------------------------------
# UI Constants
# ---------------------------------------------------------------------------
MAX_HISTORY_ITEMS: Final[int] = 20
PROMPT_MAX_CHARS: Final[int] = 500
GALLERY_COLUMNS: Final[int] = 3

# ---------------------------------------------------------------------------
# Random Prompt Seeds
# ---------------------------------------------------------------------------
RANDOM_PROMPTS: Final[list[str]] = [
    "A futuristic Indian city at night, glowing skyline over the Ganges",
    "An ancient temple swallowed by a jungle, golden hour light filtering through the canopy",
    "A lone astronaut standing on a rust-red Martian plain, Earth visible on the horizon",
    "A vast underwater palace inhabited by bioluminescent creatures",
    "A snow-covered mountain village at dusk, warm lights in every window",
    "A massive storm over an alien ocean, twin moons rising",
    "A hyper-dense Tokyo street intersection at 3am, rain-soaked pavement",
    "A medieval fortress carved entirely into the face of a glacier",
    "A floating island chain above a sea of clouds, connected by rope bridges",
    "An abandoned space station drifting through a nebula",
    "A bustling Victorian-era marketplace inside a colossal glass greenhouse",
    "A silent forest at dawn where every tree emits a faint silver glow",
    "A colossal sandstorm approaching an isolated desert outpost",
    "A deep-sea trench where alien flora sway in the dark currents",
    "A city built vertically into the walls of a mile-deep canyon",
]
