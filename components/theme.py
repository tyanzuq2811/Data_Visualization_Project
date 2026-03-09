"""
Shared theme configuration for all pages.
Provides dark/light color palettes for Plotly charts — NEON BLUE edition.
"""

# ---- Neon Blue palette shared constants ----
_NEON_CYAN = "#00d4ff"
_NEON_BLUE = "#0088ff"

DARK_THEME = {
    # Plotly layout
    "paper_bg":   "#0f1729",
    "plot_bg":    "rgba(0,0,0,0)",
    "font_color": "#e0f2ff",
    "grid_color": "rgba(0, 212, 255, 0.10)",
    # Accent colors (neon)
    "primary":  _NEON_CYAN,
    "danger":   "#ff3366",
    "success":  "#00ff88",
    "warning":  "#ffaa00",
    # Chart-specific helpers
    "neon":        _NEON_CYAN,
    "neon_glow":   "rgba(0, 212, 255, 0.35)",
    "neon_soft":   "rgba(0, 212, 255, 0.12)",
    "neon_border": "rgba(0, 212, 255, 0.25)",
    "bar_colors":  ["#00d4ff", "#00ff88", "#ff3366", "#ffaa00",
                     "#a855f7", "#06b6d4", "#f472b6", "#facc15"],
    "seq_pair":    [_NEON_CYAN, "#ff3366"],  # two-tone: positive / negative
}

LIGHT_THEME = {
    "paper_bg":   "#ffffff",
    "plot_bg":    "rgba(0,0,0,0)",
    "font_color": "#0a1628",
    "grid_color": "rgba(0, 136, 255, 0.10)",
    "primary":  _NEON_BLUE,
    "danger":   "#e11d48",
    "success":  "#059669",
    "warning":  "#d97706",
    "neon":        _NEON_BLUE,
    "neon_glow":   "rgba(0, 136, 255, 0.20)",
    "neon_soft":   "rgba(0, 136, 255, 0.08)",
    "neon_border": "rgba(0, 136, 255, 0.20)",
    "bar_colors":  ["#0088ff", "#059669", "#e11d48", "#d97706",
                     "#7c3aed", "#0891b2", "#db2777", "#ca8a04"],
    "seq_pair":    [_NEON_BLUE, "#e11d48"],
}


def get_theme(theme_value):
    """Return the color dict for the given theme ('dark' or 'light')."""
    if theme_value == "light":
        return LIGHT_THEME
    return DARK_THEME
