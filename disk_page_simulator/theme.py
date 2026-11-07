"""Colours (light and dark), fonts, sizes and widget styles shared by the whole app."""

import sys
import tkinter.font as tkfont
from types import SimpleNamespace

import customtkinter as ctk


#  CustomTkinter widgets (CTkButton, CTkEntry, ...) take every colour as a pair:
#  (colour in light mode, colour in dark mode), so they switch theme by
#  themselves. The graph and the tables are drawn on plain tkinter Canvases,
#  so those are simply redrawn with the right colours when the theme changes.
if sys.platform.startswith("win"):
    MONO_FAMILY = "Consolas"
elif sys.platform == "darwin":
    MONO_FAMILY = "Menlo"
else:
    MONO_FAMILY = "DejaVu Sans Mono"


LIGHT = {
    "bg": "#eef2f7", "card": "#ffffff", "field": "#f8fafc", "border": "#d9dee8",
    "border_strong": "#c3cbd8", "soft": "#f1f4f9", "text": "#1f2937", "muted": "#6b7280",
    "grid": "#e3e7ee", "accent": "#2563eb", "accent_hover": "#1d4ed8", "accent_deep": "#1e3a8a",
    "accent_text": "#1e40af", "accent_soft": "#e8efff", "segment": "#94a3b8",
    "segment_hover": "#7c8ba1", "scroll": "#c5ccd8", "scroll_hover": "#a9b3c3",
    "start": "#f59e0b", "start_text": "#b45309", "edge": "#9ca3af", "good": "#16a34a",
    "fault_bg": "#fde2e2", "fault_fg": "#b91c1c", "hit_bg": "#dcfce7", "hit_fg": "#15803d",
}


DARK = {
    "bg": "#16181c", "card": "#202329", "field": "#2a2e35", "border": "#33373f",
    "border_strong": "#474c56", "soft": "#2a2e35", "text": "#e5e7eb", "muted": "#9ca3af",
    "grid": "#2f333b", "accent": "#3b82f6", "accent_hover": "#2563eb", "accent_deep": "#1d4ed8",
    "accent_text": "#93c5fd", "accent_soft": "#1e2b44", "segment": "#3b414b",
    "segment_hover": "#4a515d", "scroll": "#454a54", "scroll_hover": "#5a606b",
    "start": "#f59e0b", "start_text": "#fbbf24", "edge": "#6b7280", "good": "#22c55e",
    "fault_bg": "#43212a", "fault_fg": "#fca5a5", "hit_bg": "#173523", "hit_fg": "#86efac",
}


SCALE = 1.0                  # becomes 1.25, 1.5 ... on high-DPI Windows screens


FONT = SimpleNamespace()     # fonts for CustomTkinter widgets (scaled automatically)


CFONT = SimpleNamespace()    # fonts for drawing on canvases (scaled by us)


MAX_FRAMES = 30


DIRECTION_LABELS = {"up": "→  Toward higher", "down": "←  Toward 0"}


def C(name):
    """Colour pair (light, dark) for a CustomTkinter widget."""
    return (LIGHT[name], DARK[name])


def P():
    """Colours of the current theme, for drawing on canvases."""
    return DARK if ctk.get_appearance_mode() == "Dark" else LIGHT


def px(value):
    """Scale a size in pixels for high-DPI screens (for canvas drawings)."""
    return int(round(value * SCALE))


def setup_fonts(root):
    """Create the shared fonts once the main window exists."""
    global SCALE
    try:
        SCALE = float(ctk.ScalingTracker.get_widget_scaling(root))
    except Exception:            # if this CustomTkinter version differs, just don't scale
        SCALE = 1.0
    FONT.title = ctk.CTkFont(size=20, weight="bold")
    FONT.header = ctk.CTkFont(size=18, weight="bold")
    FONT.big = ctk.CTkFont(size=28, weight="bold")
    FONT.bold = ctk.CTkFont(size=14, weight="bold")
    FONT.ui = ctk.CTkFont(size=14)
    FONT.small = ctk.CTkFont(size=12)
    FONT.mono = ctk.CTkFont(family=MONO_FAMILY, size=13)
    family = FONT.ui.cget("family")
    # a negative size means pixels; we multiply by SCALE ourselves for canvases
    CFONT.ui = tkfont.Font(root, family=family, size=-px(13))
    CFONT.bold = tkfont.Font(root, family=family, size=-px(13), weight="bold")
    CFONT.small = tkfont.Font(root, family=family, size=-px(12))
    CFONT.label = tkfont.Font(root, family=family, size=-px(12), weight="bold")
    CFONT.tiny = tkfont.Font(root, family=family, size=-px(11))


# ----- widget styles (functions, because the fonts exist only after start-up) -----
def entry_style():
    return dict(height=34, corner_radius=8, border_width=2, fg_color=C("field"),
                border_color=C("border_strong"), text_color=C("text"),
                placeholder_text_color=C("muted"), font=FONT.ui)


def option_style():
    return dict(height=34, corner_radius=8, fg_color=C("accent"), button_color=C("accent_hover"),
                button_hover_color=C("accent_deep"), text_color=("#ffffff", "#ffffff"),
                dropdown_fg_color=C("card"), dropdown_hover_color=C("soft"),
                dropdown_text_color=C("text"), font=FONT.ui, dropdown_font=FONT.ui)


def segment_style():
    return dict(height=34, corner_radius=8, fg_color=C("segment"), selected_color=C("accent"),
                selected_hover_color=C("accent_hover"), unselected_color=C("segment"),
                unselected_hover_color=C("segment_hover"), text_color=("#ffffff", "#f3f4f6"),
                font=FONT.bold)


def plain_button_style():
    return dict(height=34, corner_radius=8, fg_color=C("soft"), hover_color=C("border"),
                text_color=C("text"), font=FONT.ui)
