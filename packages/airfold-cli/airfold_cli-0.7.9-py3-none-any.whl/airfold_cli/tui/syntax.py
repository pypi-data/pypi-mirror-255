from typing import Union

from rich.style import Style
from rich.syntax import (
    DEFAULT_THEME,
    RICH_SYNTAX_THEMES,
    ANSISyntaxTheme,
    PygmentsSyntaxTheme,
    SyntaxTheme,
)


class PygmentsSyntaxThemeTransparentBackground(PygmentsSyntaxTheme):
    def __init__(self, theme: str) -> None:
        super().__init__(theme=theme)
        self._background_color = None
        self._background_style = Style.null()


def get_syntax_theme(name: Union[str, SyntaxTheme] = DEFAULT_THEME) -> SyntaxTheme:
    """Get a syntax theme instance."""
    if isinstance(name, SyntaxTheme):
        return name
    theme: SyntaxTheme
    if name in RICH_SYNTAX_THEMES:
        theme = ANSISyntaxTheme(RICH_SYNTAX_THEMES[name])
    else:
        theme = PygmentsSyntaxThemeTransparentBackground(name)
    return theme
