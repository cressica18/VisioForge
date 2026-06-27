# prompt_templates.py — Style definitions and prompt construction logic.
# No UI or API logic belongs here. Only prompt engineering.

from dataclasses import dataclass, field
from typing import Final


# ---------------------------------------------------------------------------
# Style Data Model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StyleTemplate:
    """Immutable definition of a visual style used for prompt conditioning."""
    name: str
    descriptor: str
    quality_boosters: list[str] = field(default_factory=list)
    negative_hints: list[str] = field(default_factory=list)
    preview_keywords: list[str] = field(default_factory=list)
    description: str = ""


# ---------------------------------------------------------------------------
# Style Registry
# ---------------------------------------------------------------------------

STYLE_REGISTRY: Final[dict[str, StyleTemplate]] = {
    "Photorealistic": StyleTemplate(
        name="Photorealistic",
        descriptor=(
            "ultra-photorealistic, RAW photo, DSLR quality, natural lighting, "
            "cinematic composition, depth of field"
        ),
        quality_boosters=[
            "8K resolution", "highly detailed", "sharp focus",
            "professional photography", "award-winning photograph",
        ],
        negative_hints=[
            "cartoon", "painting", "illustration", "sketch", "anime",
            "3d render", "blurry", "low quality",
        ],
        preview_keywords=["photorealistic", "DSLR", "cinematic", "natural lighting"],
        description="Ultra-realistic imagery indistinguishable from a professional photograph.",
    ),

    "Cyberpunk": StyleTemplate(
        name="Cyberpunk",
        descriptor=(
            "cyberpunk aesthetic, neon lights, rain-soaked streets, "
            "holographic signs, dystopian future, retrofuturism, "
            "blue and magenta neon glow, dark atmosphere"
        ),
        quality_boosters=[
            "cinematic lighting", "highly detailed", "sharp focus",
            "professional digital art", "4K", "atmospheric haze",
        ],
        negative_hints=[
            "daytime", "bright sunshine", "cheerful", "pastel colors",
            "low quality", "blurry",
        ],
        preview_keywords=["neon lights", "dystopian", "holographic", "rain"],
        description="Neon-drenched dystopian futures inspired by classic cyberpunk aesthetics.",
    ),

    "Anime": StyleTemplate(
        name="Anime",
        descriptor=(
            "anime style, Studio Ghibli inspired, soft cel shading, "
            "vivid colors, expressive linework, Japanese animation aesthetic"
        ),
        quality_boosters=[
            "highly detailed", "clean linework", "vibrant colors",
            "professional anime art", "sharp focus",
        ],
        negative_hints=[
            "photorealistic", "3d render", "western cartoon", "sketch",
            "low quality", "blurry",
        ],
        preview_keywords=["cel shading", "vivid", "Ghibli", "Japanese animation"],
        description="Expressive Japanese animation aesthetic with rich colors and fluid compositions.",
    ),

    "Watercolor": StyleTemplate(
        name="Watercolor",
        descriptor=(
            "watercolor painting, soft washes of color, wet-on-wet technique, "
            "translucent layers, paper texture, delicate brushwork, "
            "impressionistic, flowing pigments"
        ),
        quality_boosters=[
            "professional watercolor art", "highly detailed",
            "fine art quality", "museum quality",
        ],
        negative_hints=[
            "photorealistic", "sharp edges", "digital art", "3d render",
            "low quality",
        ],
        preview_keywords=["soft washes", "translucent", "paper texture", "impressionistic"],
        description="Delicate, luminous paintings with soft washes, flowing pigments, and paper texture.",
    ),

    "Oil Painting": StyleTemplate(
        name="Oil Painting",
        descriptor=(
            "oil painting on canvas, rich impasto texture, deep shadows, "
            "dramatic chiaroscuro lighting, old masters technique, "
            "Rembrandt-style, warm tones, visible brushstrokes"
        ),
        quality_boosters=[
            "museum quality", "masterpiece", "highly detailed",
            "fine art", "gallery piece",
        ],
        negative_hints=[
            "photorealistic", "digital art", "anime", "sketch",
            "watercolor", "low quality",
        ],
        preview_keywords=["impasto", "chiaroscuro", "old masters", "canvas texture"],
        description="Rich, textured paintings evoking the depth and warmth of classical oil-on-canvas works.",
    ),

    "Fantasy": StyleTemplate(
        name="Fantasy",
        descriptor=(
            "epic fantasy art, magical atmosphere, mystical lighting, "
            "otherworldly environment, dramatic scale, ethereal glow, "
            "concept art for a fantasy film, mythological grandeur"
        ),
        quality_boosters=[
            "concept art quality", "highly detailed", "cinematic",
            "professional digital painting", "epic composition",
        ],
        negative_hints=[
            "mundane", "photorealistic", "modern setting",
            "low quality", "blurry",
        ],
        preview_keywords=["mystical", "ethereal glow", "epic scale", "magical"],
        description="Grand, mythological scenes filled with magic, dramatic lighting, and otherworldly scale.",
    ),

    "Pixel Art": StyleTemplate(
        name="Pixel Art",
        descriptor=(
            "pixel art style, 16-bit aesthetic, retro game art, "
            "clean pixel grid, limited color palette, "
            "isometric or side-scrolling perspective, crisp pixels"
        ),
        quality_boosters=[
            "high resolution pixel art", "clean pixels",
            "professional game art", "no anti-aliasing",
        ],
        negative_hints=[
            "photorealistic", "blurry", "anti-aliased", "3d render",
            "soft edges", "low quality",
        ],
        preview_keywords=["16-bit", "retro", "pixel grid", "limited palette"],
        description="Nostalgic retro-game aesthetics with crisp pixel grids and carefully chosen palettes.",
    ),

    "Minimalist Line Art": StyleTemplate(
        name="Minimalist Line Art",
        descriptor=(
            "minimalist line art, clean geometric forms, monochromatic, "
            "negative space, Bauhaus-inspired, precise linework, "
            "graphic design aesthetic, flat composition"
        ),
        quality_boosters=[
            "professional graphic design", "clean composition",
            "high contrast", "precise lines",
        ],
        negative_hints=[
            "photorealistic", "color", "busy composition", "texture",
            "3d render", "low quality",
        ],
        preview_keywords=["geometric", "negative space", "Bauhaus", "monochromatic"],
        description="Precise, elegant compositions using clean lines, geometry, and deliberate negative space.",
    ),
}


# ---------------------------------------------------------------------------
# Prompt Construction
# ---------------------------------------------------------------------------

def build_styled_prompt(user_prompt: str, style_name: str) -> str:
    """
    Construct the final prompt to be sent to the image generation API.

    Combines the user's raw subject prompt with style descriptors and
    quality boosters defined in the style registry.

    Args:
        user_prompt: The raw descriptive prompt entered by the user.
        style_name:  The name of the selected style (must be in STYLE_REGISTRY).

    Returns:
        A fully constructed prompt string ready for API submission.
    """
    template = STYLE_REGISTRY.get(style_name)
    if template is None:
        # Graceful fallback: return the prompt unmodified
        return user_prompt.strip()

    parts = [
        user_prompt.strip(),
        template.descriptor,
        ", ".join(template.quality_boosters),
    ]
    return ", ".join(filter(None, parts))


def get_style_negative_hints(style_name: str) -> str:
    """
    Return the default negative prompt suggestions for a given style.

    These are offered as defaults in the UI but may be overridden by the user.

    Args:
        style_name: Name of the style to look up.

    Returns:
        A comma-separated string of negative prompt keywords.
    """
    template = STYLE_REGISTRY.get(style_name)
    if template is None:
        return ""
    return ", ".join(template.negative_hints)


def get_style_info(style_name: str) -> dict[str, str | list[str]]:
    """
    Return display metadata for a style — used in the UI preview.

    Args:
        style_name: Name of the style to retrieve.

    Returns:
        Dictionary with 'description' and 'keywords' keys.
    """
    template = STYLE_REGISTRY.get(style_name)
    if template is None:
        return {"description": "", "keywords": []}
    return {
        "description": template.description,
        "keywords": template.preview_keywords,
    }


def list_styles() -> list[str]:
    """Return all registered style names in their defined order."""
    return list(STYLE_REGISTRY.keys())
