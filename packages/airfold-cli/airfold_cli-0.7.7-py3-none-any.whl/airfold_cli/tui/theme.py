from rich.color import Color
from rich.style import Style
from rich.theme import Theme

MONOKAI_LIGHT_ACCENT = Color.from_rgb(62, 64, 54).triplet.hex  # type: ignore
MONOKAI_BACKGROUND = Color.from_rgb(red=39, green=40, blue=34)
DUNK_BG_HEX = "#0d0f0b"
MONOKAI_BG_HEX = MONOKAI_BACKGROUND.triplet.hex  # type: ignore

MONOKAI_THEME = Theme(
    {
        "hatched": f"{MONOKAI_BG_HEX} on {DUNK_BG_HEX}",
        "renamed": f"cyan",
        "border": MONOKAI_LIGHT_ACCENT,
        "prompt.choices": "bold blue",
        "success": "bold green",
        "error": "red",
        "warning": "yellow",
        "info": "bold blue",
        "general": Style.null(),
    }
)
