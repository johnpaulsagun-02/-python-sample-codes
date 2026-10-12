"""Kainan v2 - PySide6 food ordering sample.

New in this version
- 38 dishes with generated food "photos" (gradient + plate + emoji). To use
  real photos, put images in an `images/` folder next to this file, named
  after the dish: chicken_adobo.jpg, halo_halo.png, pork_sisig.webp ...
- Accounts: sign up, log in, stay signed in, guest mode, log out
  (passwords are salted + hashed with PBKDF2; data lives in ~/.kainan_sample)
- Profile: photo, contact details, delivery address, stats, order history, reorder
- Settings: customization (theme, accent colour, font size, cards per row,
  images, ratings), privacy (stay signed in, password before ordering, mask
  contact details, save history, clear data, export data, delete account)
  and account (change password, log out)
- Favorites (heart a dish, then open the Favorites category)

Install:  pip install PySide6
Run:      python food_ui_v2.py
"""
import hashlib
import hmac
import json
import os
import re
import secrets
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "Kainan"
APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("KAINAN_DATA_DIR", Path.home() / ".kainan_sample"))
CURRENCY = "₱"
CARD_W, CARD_H = 214, 300
GRID_GAP = 14


# --------------------------------------------------------------------------
# Data: foods
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Food:
    name: str
    category: str
    price: int
    emoji: str
    rating: float
    veg: bool
    desc: str
    c1: str
    c2: str

    @property
    def slug(self):
        return re.sub(r"[^a-z0-9]+", "_", self.name.lower()).strip("_")


FOODS = [
    # ---- Starters
    Food("Lumpiang Shanghai", "Starters", 90, "🥟", 4.6, False,
         "Crispy pork spring rolls served with sweet chili dip.", "#e8a33d", "#b4561b"),
    Food("Fresh Lumpia", "Starters", 85, "🌯", 4.2, True,
         "Soft crepe wrapped around vegetables with peanut-garlic sauce.", "#9ccf72", "#3f7d3a"),
    Food("Tokwa't Baboy", "Starters", 110, "🧈", 4.1, False,
         "Fried tofu and boiled pork in a soy-vinegar dressing.", "#d9a066", "#8a4e24"),
    Food("Kinilaw na Tanigue", "Starters", 160, "🐟", 4.5, False,
         "Fresh mackerel cured in vinegar and calamansi with ginger, onion and chili.", "#5fb4c9", "#226c86"),
    Food("Calamares", "Starters", 150, "🦑", 4.4, False,
         "Golden fried squid rings with spiced vinegar.", "#f0b95a", "#c46a2b"),
    Food("Camaron Rebusado", "Starters", 170, "🍤", 4.6, False,
         "Crispy battered shrimp with a sweet and sour dip.", "#f08a5d", "#b83d2e"),
    # ---- Mains
    Food("Chicken Adobo", "Mains", 180, "🍗", 4.8, False,
         "Chicken braised in soy sauce, vinegar, garlic and peppercorn.", "#b5651d", "#4a2511"),
    Food("Sinigang na Baboy", "Mains", 220, "🍲", 4.7, False,
         "Sour tamarind soup with pork, kangkong, radish and tomatoes.", "#d9c35a", "#7d7a1e"),
    Food("Sinigang na Hipon", "Mains", 260, "🦐", 4.7, False,
         "Tamarind soup with fresh shrimp and vegetables.", "#e6b85c", "#8b6a1e"),
    Food("Pinakbet", "Mains", 130, "🥬", 4.3, True,
         "Northern Luzon stew of squash, okra, eggplant and bitter melon.", "#7cc06a", "#2f6b3a"),
    Food("Dinengdeng", "Mains", 120, "🥗", 4.2, True,
         "Ilocano vegetable stew with moringa leaves and string beans.", "#86c36f", "#2f6d3a"),
    Food("Lechon Kawali", "Mains", 250, "🐖", 4.9, False,
         "Deep-fried crispy pork belly with liver sauce.", "#e0a24a", "#8f3b17"),
    Food("Kare-Kare", "Mains", 280, "🥘", 4.8, False,
         "Oxtail and vegetables in rich peanut sauce, served with bagoong.", "#d28c3c", "#7a4012"),
    Food("Pork Sisig", "Mains", 210, "🍖", 4.8, False,
         "Chopped sizzling pork with onion, chili and calamansi.", "#d96b3b", "#7a2c14"),
    Food("Bicol Express", "Mains", 190, "🌶️", 4.5, False,
         "Pork simmered in coconut milk with long green chilies.", "#e0553a", "#8c1f1a"),
    Food("Bistek Tagalog", "Mains", 240, "🥩", 4.6, False,
         "Beef strips in soy-calamansi sauce topped with onion rings.", "#a05a3a", "#3d1d12"),
    Food("Inihaw na Liempo", "Mains", 200, "🥓", 4.7, False,
         "Charcoal-grilled marinated pork belly.", "#cf7a45", "#6e2e16"),
    # ---- Noodles & Rice
    Food("Pancit Canton", "Noodles & Rice", 140, "🍜", 4.4, False,
         "Stir-fried egg noodles with vegetables, chicken and shrimp.", "#e9b44c", "#a8601f"),
    Food("Pancit Bihon", "Noodles & Rice", 135, "🍝", 4.3, False,
         "Thin rice noodles sauteed with pork, cabbage and carrots.", "#f0c96a", "#b57a2a"),
    Food("Pancit Palabok", "Noodles & Rice", 150, "🍝", 4.5, False,
         "Rice noodles in shrimp sauce with egg, chicharon and tinapa flakes.", "#f2a25a", "#b8501f"),
    Food("La Paz Batchoy", "Noodles & Rice", 170, "🍜", 4.6, False,
         "Iloilo noodle soup with pork, liver and crushed chicharon.", "#c98a4a", "#6b3b1b"),
    Food("Arroz Caldo", "Noodles & Rice", 110, "🍚", 4.5, False,
         "Ginger rice porridge with chicken, topped with egg and toasted garlic.", "#e6d08a", "#9a7a2a"),
    Food("Sinangag at Itlog", "Noodles & Rice", 95, "🍳", 4.4, True,
         "Garlic fried rice with a sunny-side-up egg.", "#f3d768", "#c58a1f"),
    # ---- Desserts
    Food("Halo-Halo", "Desserts", 120, "🍧", 4.9, True,
         "Shaved ice with sweet beans, fruits, leche flan and ube ice cream.", "#c58ae8", "#6a3fa8"),
    Food("Leche Flan", "Desserts", 80, "🍮", 4.7, True,
         "Silky caramel custard made with egg yolks and condensed milk.", "#f0b45a", "#b3661e"),
    Food("Turon", "Desserts", 50, "🍌", 4.5, True,
         "Banana and jackfruit in lumpia wrapper, fried with caramelized sugar.", "#f2c14e", "#b9741a"),
    Food("Bibingka", "Desserts", 100, "🥞", 4.6, True,
         "Rice cake baked in banana leaves, topped with salted egg and cheese.", "#e8c58a", "#a2692c"),
    Food("Puto Bumbong", "Desserts", 90, "🍡", 4.4, True,
         "Purple steamed rice cake with butter, coconut and muscovado.", "#b57be0", "#5f3a9a"),
    Food("Ube Halaya", "Desserts", 85, "🍠", 4.6, True,
         "Smooth, sweet purple yam jam.", "#a56be0", "#512f99"),
    Food("Strawberry Shortcake", "Desserts", 130, "🍰", 4.8, True,
         "Fluffy cake layered with cream and fresh strawberries.", "#f58aa6", "#c2395f"),
    Food("Buko Pandan", "Desserts", 95, "🥥", 4.5, True,
         "Young coconut, pandan jelly and sweet cream.", "#8fd19e", "#2e8a53"),
    # ---- Drinks
    Food("Mango Shake", "Drinks", 95, "🥭", 4.8, True,
         "Ripe Philippine mangoes blended with milk and ice.", "#f7c148", "#e07b1a"),
    Food("Calamansi Juice", "Drinks", 60, "🍋", 4.4, True,
         "Fresh calamansi, lightly sweetened and served over ice.", "#c9e06a", "#6d9a1f"),
    Food("Iced Coffee", "Drinks", 85, "☕", 4.3, True,
         "Strong arabica brewed cold and served with milk.", "#a9805a", "#4a3020"),
    Food("Sago't Gulaman", "Drinks", 55, "🧋", 4.2, True,
         "Brown sugar syrup with tapioca pearls and gelatin.", "#c28a55", "#6a3d1d"),
    Food("Buko Juice", "Drinks", 70, "🥥", 4.5, True,
         "Fresh coconut water with tender coconut strips.", "#bfe3d0", "#4f9c82"),
    Food("Strawberry Taho", "Drinks", 75, "🍓", 4.6, True,
         "Silky tofu with strawberry syrup and tapioca pearls.", "#f58aa0", "#b8324f"),
    Food("Salabat", "Drinks", 50, "🍵", 4.1, True,
         "Hot ginger tea sweetened with honey.", "#e8c96a", "#a77a1e"),
    Food("Melon Juice", "Drinks", 65, "🍈", 4.2, True,
         "Chilled cantaloupe juice with a little sugar.", "#b8e08a", "#5fa03a"),
]
FOOD_BY_NAME = {f.name: f for f in FOODS}

CATEGORIES = ["All", "Favorites", "Starters", "Mains", "Noodles & Rice", "Desserts", "Drinks"]
CAT_ICONS = {
    "All": "🍴", "Favorites": "♥", "Starters": "🥟", "Mains": "🍛",
    "Noodles & Rice": "🍜", "Desserts": "🍨", "Drinks": "🥤",
}


# --------------------------------------------------------------------------
# Settings & themes
# --------------------------------------------------------------------------
DEFAULT_SETTINGS = {
    "theme": "Dark",
    "accent": "#ff8c1a",
    "font_size": 10,
    "columns": 0,            # 0 = automatic
    "show_images": True,
    "show_ratings": True,
    "mask_contact": False,
    "save_history": True,
    "confirm_orders": False,
}
PROFILE_FIELDS = ("full_name", "email", "phone", "address", "avatar")

ACCENTS = {
    "Orange": "#ff8c1a", "Tomato": "#e8523f", "Mango": "#f5b82e", "Leaf": "#4cb36a",
    "Ocean": "#3b8ee8", "Ube": "#8e5be0", "Pink": "#e75a9b",
}

PALETTES = {
    "Dark": {
        "bg": "#1e1b18", "surface": "#272320", "surface2": "#35302b",
        "border": "#3d362f", "text": "#f2e8dc", "muted": "#a89a8a", "hover": "#453e37",
    },
    "Light": {
        "bg": "#f7f2ec", "surface": "#ffffff", "surface2": "#efe7dd",
        "border": "#e0d6ca", "text": "#2b2520", "muted": "#7a6e62", "hover": "#e6dccf",
    },
}

STYLE_TEMPLATE = """
QWidget { background: transparent; color: @text@; }
QMainWindow, QDialog, QMessageBox, QWidget#root, QWidget#page { background: @bg@; }
QToolTip { background: @surface2@; color: @text@; border: 1px solid @border@; }

QLabel#title { font-size: 22px; font-weight: bold; color: @accent@; }
QLabel#h2 { font-size: 15px; font-weight: bold; }
QLabel#muted { color: @muted@; }
QLabel#price { color: @accent@; font-weight: bold; font-size: 15px; }
QLabel#total { font-size: 20px; font-weight: bold; color: @accent@; }
QLabel#stat { font-size: 22px; font-weight: bold; color: @accent@; }
QLabel#error { color: #e5484d; }
QLabel#banner { background: @surface2@; border-radius: 8px; padding: 10px; }
QLabel#imgfallback { background: @surface2@; border-radius: 10px; font-size: 52px; }

QListWidget#sidebar {
    background: @surface@; border: none; border-radius: 10px;
    font-size: 14px; padding: 6px; outline: none;
}
QListWidget#sidebar::item { padding: 9px 12px; border-radius: 8px; }
QListWidget#sidebar::item:selected { background: @accent@; color: @on_accent@; }
QListWidget#sidebar::item:hover:!selected { background: @surface2@; }

QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {
    background: @surface@; border: 1px solid @border@; border-radius: 8px;
    padding: 6px 10px; selection-background-color: @accent@; selection-color: @on_accent@;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus { border-color: @accent@; }
QLineEdit:disabled, QPlainTextEdit:disabled, QComboBox:disabled { color: @muted@; }
QComboBox QAbstractItemView {
    background: @surface@; border: 1px solid @border@;
    selection-background-color: @accent@; selection-color: @on_accent@;
}
QComboBox::drop-down { border: none; width: 26px; background: transparent; }
QComboBox::down-arrow { image: url("@arrow_down@"); width: 12px; height: 8px; margin-right: 8px; }
QSpinBox::up-button, QSpinBox::down-button {
    subcontrol-origin: border; width: 22px; border: none; background: transparent;
}
QSpinBox::up-button { subcontrol-position: top right; }
QSpinBox::down-button { subcontrol-position: bottom right; }
QSpinBox::up-arrow { image: url("@arrow_up@"); width: 10px; height: 7px; }
QSpinBox::down-arrow { image: url("@arrow_down@"); width: 10px; height: 7px; }
QCheckBox { spacing: 8px; }
QCheckBox:disabled { color: @muted@; }
QCheckBox::indicator {
    width: 18px; height: 18px; border-radius: 5px;
    border: 1px solid @muted@; background: @surface@;
}
QCheckBox::indicator:hover { border-color: @accent@; }
QCheckBox::indicator:checked { background: @accent@; border-color: @accent@; image: url("@check@"); }
QCheckBox::indicator:disabled { border-color: @border@; background: @surface2@; }

QPushButton {
    background: @surface2@; border: none; border-radius: 8px; padding: 8px 14px;
}
QPushButton:hover { background: @hover@; }
QPushButton#primary { background: @accent@; color: @on_accent@; font-weight: bold; }
QPushButton#primary:hover { background: @accent_hover@; }
QPushButton#danger { background: #c0392b; color: #ffffff; }
QPushButton#danger:hover { background: #d9503f; }
QPushButton:disabled { background: @surface@; color: @muted@; }
QToolButton#heart { border: none; font-size: 20px; color: @muted@; padding: 0 4px; }
QToolButton#heart[fav="true"] { color: @accent@; }

QFrame#card { background: @surface@; border: 1px solid @border@; border-radius: 14px; }
QFrame#card:hover { border-color: @accent@; }
QFrame#panel { background: @surface@; border-radius: 14px; }

QTableWidget { background: transparent; border: none; gridline-color: transparent; }
QTableWidget::item:selected { background: @hover@; color: @text@; }
QHeaderView::section { background: transparent; color: @muted@; border: none; padding: 4px; }

QTabWidget::pane { border: 1px solid @border@; border-radius: 10px; top: -1px; background: @surface@; }
QTabBar::tab { color: @muted@; padding: 8px 18px; margin-right: 4px; border-radius: 8px; }
QTabBar::tab:selected { background: @accent@; color: @on_accent@; font-weight: bold; }
QTabBar::tab:hover:!selected { background: @surface2@; }
QGroupBox {
    border: 1px solid @border@; border-radius: 10px; margin-top: 14px; padding: 14px 10px 10px 10px;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: @muted@; }

QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: transparent; width: 10px; }
QScrollBar::handle:vertical { background: @hover@; border-radius: 5px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


def luminance(color):
    return (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255


def write_icons(arrow_color, check_color):
    """Write the small SVG icons used by combo boxes, spin boxes and checkboxes."""
    folder = DATA_DIR / "icons"
    folder.mkdir(parents=True, exist_ok=True)
    head = "<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>"
    tail = ("<path d='{d}' fill='none' stroke='{c}' stroke-width='1.8' "
            "stroke-linecap='round' stroke-linejoin='round'/></svg>")
    icons = {
        "arrow_down": (12, 8, "M1 1.5 6 6.5 11 1.5", arrow_color),
        "arrow_up": (12, 8, "M1 6.5 6 1.5 11 6.5", arrow_color),
        "check": (12, 12, "M2 6.5 5 9.5 10 3", check_color),
    }
    paths = {}
    for name, (w, h, d, color) in icons.items():
        path = folder / f"{name}_{color.lstrip('#')}.svg"
        if not path.exists():
            path.write_text(head.format(w=w, h=h) + tail.format(d=d, c=color), "utf-8")
        paths[name] = path.as_posix()
    return paths


def build_stylesheet(settings):
    palette = dict(PALETTES.get(settings.get("theme"), PALETTES["Dark"]))
    accent = QColor(settings.get("accent", DEFAULT_SETTINGS["accent"]))
    if not accent.isValid():
        accent = QColor(DEFAULT_SETTINGS["accent"])
    palette["accent"] = accent.name()
    palette["accent_hover"] = accent.lighter(115).name()
    palette["on_accent"] = "#1e1b18" if luminance(accent) > 0.55 else "#ffffff"
    palette.update(write_icons(palette["muted"], palette["on_accent"]))
    css = STYLE_TEMPLATE
    for key, value in palette.items():
        css = css.replace(f"@{key}@", value)
    return css


def apply_app_theme(app, settings):
    app.setStyleSheet(build_stylesheet(settings))
    font = app.font()
    font.setPointSize(int(settings.get("font_size", 10)))
    app.setFont(font)


# --------------------------------------------------------------------------
# Image helpers
# --------------------------------------------------------------------------
_pixmap_cache = {}


def find_custom_image(food):
    for folder in (APP_DIR / "images", DATA_DIR / "images"):
        for ext in ("jpg", "jpeg", "png", "webp"):
            candidate = folder / f"{food.slug}.{ext}"
            if candidate.exists():
                return candidate
    return None


def make_food_pixmap(food, w, h, radius=12):
    key = (food.slug, w, h, radius)
    if key in _pixmap_cache:
        return _pixmap_cache[key]

    pm = QPixmap(w * 2, h * 2)
    pm.setDevicePixelRatio(2)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    clip = QPainterPath()
    clip.addRoundedRect(0, 0, w, h, radius, radius)
    p.setClipPath(clip)

    custom = find_custom_image(food)
    photo = QPixmap(str(custom)) if custom else QPixmap()
    if not photo.isNull():
        scaled = photo.scaled(
            w * 2, h * 2,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        source = QRectF((scaled.width() - w * 2) / 2, (scaled.height() - h * 2) / 2, w * 2, h * 2)
        p.drawPixmap(QRectF(0, 0, w, h), scaled, source)
    else:
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0, QColor(food.c1))
        grad.setColorAt(1, QColor(food.c2))
        p.fillRect(QRectF(0, 0, w, h), grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 30))
        p.drawEllipse(QPointF(w * 0.88, h * 0.1), h * 0.5, h * 0.5)
        p.drawEllipse(QPointF(w * 0.08, h * 1.0), h * 0.45, h * 0.45)
        center = QPointF(w / 2, h / 2)
        r = min(w, h) * 0.42
        p.setBrush(QColor(0, 0, 0, 35))
        p.drawEllipse(QPointF(center.x(), center.y() + r * 0.1), r * 1.05, r * 0.98)
        p.setBrush(QColor(255, 255, 255, 235))
        p.drawEllipse(center, r, r * 0.95)
        p.setBrush(QColor(255, 255, 255, 255))
        p.drawEllipse(center, r * 0.78, r * 0.72)
        font = QFont()
        font.setPixelSize(int(min(w, h) * 0.46))
        p.setFont(font)
        p.setPen(QColor(0, 0, 0))
        p.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, food.emoji)
    p.end()
    _pixmap_cache[key] = pm
    return pm


def initials(name):
    parts = [x for x in name.split() if x]
    return "".join(x[0] for x in parts[:2]).upper() or "?"


def make_avatar(name, path, size, accent):
    pm = QPixmap(size * 2, size * 2)
    pm.setDevicePixelRatio(2)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    clip = QPainterPath()
    clip.addEllipse(0, 0, size, size)
    p.setClipPath(clip)
    photo = QPixmap(path) if path and Path(path).exists() else QPixmap()
    if not photo.isNull():
        scaled = photo.scaled(
            size * 2, size * 2,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        source = QRectF((scaled.width() - size * 2) / 2, (scaled.height() - size * 2) / 2,
                        size * 2, size * 2)
        p.drawPixmap(QRectF(0, 0, size, size), scaled, source)
    else:
        color = QColor(accent)
        p.fillRect(QRectF(0, 0, size, size), color)
        font = QFont()
        font.setPixelSize(int(size * 0.4))
        font.setBold(True)
        p.setFont(font)
        p.setPen(QColor("#1e1b18") if luminance(color) > 0.55 else QColor("#ffffff"))
        p.drawText(QRectF(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, initials(name))
    p.end()
    return pm


def mask_email(email):
    if "@" not in email:
        return "***" if email else ""
    local, domain = email.split("@", 1)
    return f"{local[:1]}***@{domain}"


def mask_phone(phone):
    return f"***{phone[-3:]}" if len(phone) > 3 else ("***" if phone else "")


# --------------------------------------------------------------------------
# Storage (accounts, profile, settings, favorites, orders)
# --------------------------------------------------------------------------
class Store:
    def __init__(self):
        self.dir = DATA_DIR
        self.dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.dir / "users.json"
        self.session_file = self.dir / "session.json"
        self.users = self._load(self.users_file, {})
        for record in self.users.values():
            self.normalize(record)

    @staticmethod
    def _load(path, default):
        try:
            return json.loads(path.read_text("utf-8"))
        except (OSError, ValueError):
            return default

    def save(self):
        tmp = self.users_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.users, indent=2, ensure_ascii=False), "utf-8")
        tmp.replace(self.users_file)

    @staticmethod
    def normalize(record):
        profile = record.setdefault("profile", {})
        for field in PROFILE_FIELDS:
            profile.setdefault(field, "")
        settings = record.setdefault("settings", {})
        for key, value in DEFAULT_SETTINGS.items():
            settings.setdefault(key, value)
        record.setdefault("favorites", [])
        record.setdefault("orders", [])
        return record

    def new_guest(self):
        return self.normalize({"username": "guest", "profile": {"full_name": "Guest"}})

    @staticmethod
    def hash_password(password, salt_hex):
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 200_000
        ).hex()

    def register(self, username, password, full_name, email):
        """Returns an error message, or None on success."""
        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,24}", username):
            return "Username must be 3-24 characters: letters, numbers, _ . -"
        if len(password) < 6:
            return "Password must be at least 6 characters."
        if not full_name.strip():
            return "Please enter your name."
        key = username.lower()
        if key in self.users:
            return "That username is already taken."
        salt = secrets.token_hex(16)
        record = {
            "username": username,
            "salt": salt,
            "hash": self.hash_password(password, salt),
            "created": datetime.now().strftime("%Y-%m-%d"),
            "profile": {"full_name": full_name.strip(), "email": email.strip()},
        }
        self.users[key] = self.normalize(record)
        self.save()
        return None

    def verify(self, username, password):
        record = self.users.get(username.lower())
        if not record:
            return False
        digest = self.hash_password(password, record["salt"])
        return hmac.compare_digest(digest, record["hash"])

    def set_password(self, key, password):
        record = self.users[key]
        record["salt"] = secrets.token_hex(16)
        record["hash"] = self.hash_password(password, record["salt"])
        self.save()

    def remembered_user(self):
        name = self._load(self.session_file, {}).get("user")
        return name if name in self.users else None

    def remember(self, key):
        self.session_file.write_text(json.dumps({"user": key}), "utf-8")

    def forget_session(self):
        try:
            self.session_file.unlink()
        except OSError:
            pass


# --------------------------------------------------------------------------
# Login / sign-up dialog
# --------------------------------------------------------------------------
class LoginDialog(QDialog):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.username = None   # None => guest
        self.setWindowTitle(f"{APP_NAME} - Welcome")
        self.setMinimumWidth(380)

        brand = QLabel("🍽  Kainan")
        brand.setObjectName("title")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub = QLabel("Filipino favorites, delivered.")
        sub.setObjectName("muted")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._login_tab(), "Log in")
        self.tabs.addTab(self._signup_tab(), "Sign up")

        guest = QPushButton("Continue as guest")
        guest.clicked.connect(self._guest)
        note = QLabel("Guest data (favorites, orders, settings) isn't saved.")
        note.setObjectName("muted")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(8)
        layout.addWidget(brand)
        layout.addWidget(sub)
        layout.addSpacing(6)
        layout.addWidget(self.tabs)
        layout.addWidget(guest)
        layout.addWidget(note)

    def _login_tab(self):
        w = QWidget()
        self.l_user = QLineEdit()
        self.l_user.setPlaceholderText("Username")
        self.l_pass = QLineEdit()
        self.l_pass.setPlaceholderText("Password")
        self.l_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.l_stay = QCheckBox("Keep me signed in on this device")
        self.l_error = QLabel("")
        self.l_error.setObjectName("error")
        btn = QPushButton("Log in")
        btn.setObjectName("primary")
        btn.clicked.connect(self._do_login)
        self.l_user.returnPressed.connect(self.l_pass.setFocus)
        self.l_pass.returnPressed.connect(self._do_login)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(14, 14, 14, 14)
        for widget in (self.l_user, self.l_pass, self.l_stay, self.l_error, btn):
            lay.addWidget(widget)
        return w

    def _signup_tab(self):
        w = QWidget()
        self.s_name = QLineEdit()
        self.s_name.setPlaceholderText("Full name")
        self.s_user = QLineEdit()
        self.s_user.setPlaceholderText("Username")
        self.s_email = QLineEdit()
        self.s_email.setPlaceholderText("Email (optional)")
        self.s_pass = QLineEdit()
        self.s_pass.setPlaceholderText("Password (min. 6 characters)")
        self.s_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.s_pass2 = QLineEdit()
        self.s_pass2.setPlaceholderText("Confirm password")
        self.s_pass2.setEchoMode(QLineEdit.EchoMode.Password)
        self.s_error = QLabel("")
        self.s_error.setObjectName("error")
        self.s_error.setWordWrap(True)
        btn = QPushButton("Create account")
        btn.setObjectName("primary")
        btn.clicked.connect(self._do_signup)
        self.s_pass2.returnPressed.connect(self._do_signup)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(14, 14, 14, 14)
        for widget in (self.s_name, self.s_user, self.s_email, self.s_pass,
                       self.s_pass2, self.s_error, btn):
            lay.addWidget(widget)
        return w

    def _do_login(self):
        name, pw = self.l_user.text().strip(), self.l_pass.text()
        if not self.store.verify(name, pw):
            self.l_error.setText("Wrong username or password.")
            return
        self._finish(name.lower(), self.l_stay.isChecked())

    def _do_signup(self):
        if self.s_pass.text() != self.s_pass2.text():
            self.s_error.setText("Passwords don't match.")
            return
        error = self.store.register(
            self.s_user.text().strip(), self.s_pass.text(),
            self.s_name.text(), self.s_email.text(),
        )
        if error:
            self.s_error.setText(error)
            return
        self._finish(self.s_user.text().strip().lower(), False)

    def _guest(self):
        self.username = None
        self.accept()

    def _finish(self, key, stay):
        self.username = key
        if stay:
            self.store.remember(key)
        else:
            self.store.forget_session()
        self.accept()


# --------------------------------------------------------------------------
# Food card + details dialog
# --------------------------------------------------------------------------
class FoodCard(QFrame):
    add_clicked = Signal(object)
    details_clicked = Signal(object)
    fav_toggled = Signal(object)

    def __init__(self, food, is_fav, show_image, show_rating):
        super().__init__()
        self.food = food
        self.setObjectName("card")
        self.setFixedSize(CARD_W, CARD_H)
        iw, ih = CARD_W - 24, 118

        image = QLabel()
        image.setFixedSize(iw, ih)
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if show_image:
            image.setPixmap(make_food_pixmap(food, iw, ih))
        else:
            image.setObjectName("imgfallback")
            image.setText(food.emoji)

        title = QLabel(food.name)
        title.setObjectName("h2")
        title.setWordWrap(True)
        title.setMinimumHeight(38)
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        bits = []
        if show_rating:
            bits.append(f"★ {food.rating}")
        bits.append(food.category)
        if food.veg:
            bits.append("🌱 Veg")
        meta = QLabel("  ·  ".join(bits))
        meta.setObjectName("muted")
        meta.setWordWrap(True)

        price = QLabel(f"{CURRENCY}{food.price:,.2f}")
        price.setObjectName("price")

        self.heart = QToolButton()
        self.heart.setObjectName("heart")
        self.heart.setCursor(Qt.CursorShape.PointingHandCursor)
        self.heart.setToolTip("Add to / remove from favorites")
        self.set_fav(is_fav)
        self.heart.clicked.connect(lambda: self.fav_toggled.emit(self.food))

        price_row = QHBoxLayout()
        price_row.addWidget(price)
        price_row.addStretch()
        price_row.addWidget(self.heart)

        details = QPushButton("Details")
        add = QPushButton("Add")
        add.setObjectName("primary")
        details.clicked.connect(lambda: self.details_clicked.emit(self.food))
        add.clicked.connect(lambda: self.add_clicked.emit(self.food))
        buttons = QHBoxLayout()
        buttons.addWidget(details)
        buttons.addWidget(add)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(6)
        lay.addWidget(image)
        lay.addWidget(title)
        lay.addWidget(meta)
        lay.addLayout(price_row)
        lay.addStretch()
        lay.addLayout(buttons)

    def set_fav(self, is_fav):
        self.heart.setText("♥" if is_fav else "♡")
        self.heart.setProperty("fav", bool(is_fav))
        self.heart.style().unpolish(self.heart)
        self.heart.style().polish(self.heart)


class DetailsDialog(QDialog):
    def __init__(self, food, is_fav, show_image, on_add, on_fav, parent=None):
        super().__init__(parent)
        self.setWindowTitle(food.name)
        self.setMinimumWidth(400)

        image = QLabel()
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if show_image:
            image.setPixmap(make_food_pixmap(food, 360, 190, 14))
        else:
            image.setText(food.emoji)
            image.setStyleSheet("font-size: 72px;")

        title = QLabel(food.name)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info = QLabel(f"{food.category}  •  ★ {food.rating}  •  "
                      f"{'Vegetarian' if food.veg else 'Contains meat/seafood'}")
        info.setObjectName("muted")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body = QLabel(food.desc)
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        price = QLabel(f"{CURRENCY}{food.price:,.2f}")
        price.setObjectName("total")
        price.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._fav = is_fav
        fav_btn = QPushButton("♥ Favorited" if is_fav else "♡ Favorite")

        def toggle():
            self._fav = not self._fav
            fav_btn.setText("♥ Favorited" if self._fav else "♡ Favorite")
            on_fav(food)

        fav_btn.clicked.connect(toggle)
        add_btn = QPushButton("Add to order")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(lambda: (on_add(food), self.accept()))
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        row = QHBoxLayout()
        row.addWidget(close_btn)
        row.addWidget(fav_btn)
        row.addWidget(add_btn)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(10)
        for w in (image, title, info, body, price):
            lay.addWidget(w)
        lay.addLayout(row)


# --------------------------------------------------------------------------
# Profile page
# --------------------------------------------------------------------------
class ProfilePage(QWidget):
    def __init__(self, win):
        super().__init__()
        self.setObjectName("page")
        self.win = win

        # Left: profile card
        left = QFrame()
        left.setObjectName("panel")
        left.setFixedWidth(360)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(18, 18, 18, 18)
        ll.setSpacing(8)

        self.avatar = QLabel()
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_lbl = QLabel()
        self.name_lbl.setObjectName("title")
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub_lbl = QLabel()
        self.sub_lbl.setObjectName("muted")
        self.sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contact_lbl = QLabel()
        self.contact_lbl.setObjectName("muted")
        self.contact_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        photo_row = QHBoxLayout()
        self.photo_btn = QPushButton("Change photo")
        self.photo_rm_btn = QPushButton("Remove")
        self.photo_btn.clicked.connect(self.change_photo)
        self.photo_rm_btn.clicked.connect(self.remove_photo)
        photo_row.addWidget(self.photo_btn)
        photo_row.addWidget(self.photo_rm_btn)

        self.f_name = QLineEdit()
        self.f_email = QLineEdit()
        self.f_phone = QLineEdit()
        self.f_address = QPlainTextEdit()
        self.f_address.setFixedHeight(70)
        form = QFormLayout()
        form.setSpacing(8)
        form.addRow("Name", self.f_name)
        form.addRow("Email", self.f_email)
        form.addRow("Phone", self.f_phone)
        form.addRow("Address", self.f_address)

        self.save_btn = QPushButton("Save changes")
        self.save_btn.setObjectName("primary")
        self.save_btn.clicked.connect(self.save)

        self.guest_banner = QLabel(
            "You're browsing as a guest. Log in or sign up to save a profile, "
            "favorites and order history.")
        self.guest_banner.setObjectName("banner")
        self.guest_banner.setWordWrap(True)
        self.guest_btn = QPushButton("Log in / Sign up")
        self.guest_btn.setObjectName("primary")
        self.guest_btn.clicked.connect(self.win.logout)

        for w in (self.avatar, self.name_lbl, self.sub_lbl, self.contact_lbl):
            ll.addWidget(w)
        ll.addLayout(photo_row)
        ll.addSpacing(6)
        ll.addLayout(form)
        ll.addWidget(self.save_btn)
        ll.addWidget(self.guest_banner)
        ll.addWidget(self.guest_btn)
        ll.addStretch()

        # Right: stats + history
        right = QFrame()
        right.setObjectName("panel")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(18, 18, 18, 18)

        stats = QHBoxLayout()
        self.stat_orders = self._stat("Orders")
        self.stat_spent = self._stat("Total spent")
        self.stat_favs = self._stat("Favorites")
        for box in (self.stat_orders, self.stat_spent, self.stat_favs):
            stats.addLayout(box[0])
        rl.addLayout(stats)
        rl.addSpacing(8)

        heading = QLabel("Order history")
        heading.setObjectName("h2")
        rl.addWidget(heading)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Order", "Date", "Items", "Total"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        rl.addWidget(self.table, 1)

        self.empty_lbl = QLabel("No orders yet. Your past orders will show up here.")
        self.empty_lbl.setObjectName("muted")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(self.empty_lbl)

        self.reorder_btn = QPushButton("Reorder selected")
        self.reorder_btn.setObjectName("primary")
        self.reorder_btn.clicked.connect(self.reorder)
        rl.addWidget(self.reorder_btn)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)
        outer.addWidget(left)
        outer.addWidget(right, 1)

    @staticmethod
    def _stat(label):
        box = QVBoxLayout()
        value = QLabel("0")
        value.setObjectName("stat")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption = QLabel(label)
        caption.setObjectName("muted")
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(value)
        box.addWidget(caption)
        return box, value

    def refresh(self):
        user, s = self.win.user, self.win.settings
        profile = user["profile"]
        is_account = self.win.username is not None

        self.avatar.setPixmap(make_avatar(profile["full_name"], profile["avatar"], 110, s["accent"]))
        self.name_lbl.setText(profile["full_name"] or "Guest")
        if is_account:
            self.sub_lbl.setText(f"@{user['username']}  •  member since {user.get('created', '-')}")
        else:
            self.sub_lbl.setText("Guest mode")

        email, phone = profile["email"], profile["phone"]
        if s["mask_contact"]:
            email, phone = mask_email(email), mask_phone(phone)
        self.contact_lbl.setText("  •  ".join(x for x in (email, phone) if x))

        self.f_name.setText(profile["full_name"])
        self.f_email.setText(profile["email"])
        self.f_phone.setText(profile["phone"])
        self.f_address.setPlainText(profile["address"])

        for w in (self.f_name, self.f_email, self.f_phone, self.f_address,
                  self.save_btn, self.photo_btn, self.photo_rm_btn):
            w.setEnabled(is_account)
        self.guest_banner.setVisible(not is_account)
        self.guest_btn.setVisible(not is_account)

        orders = user["orders"]
        spent = sum(o["total"] for o in orders)
        self.stat_orders[1].setText(str(len(orders)))
        self.stat_spent[1].setText(f"{CURRENCY}{spent:,.0f}")
        self.stat_favs[1].setText(str(len(user["favorites"])))

        self.table.setRowCount(len(orders))
        for row, order in enumerate(reversed(orders)):
            items = ", ".join(f"{i['qty']}× {i['name']}" for i in order["items"])
            cells = [order["id"], order["time"], items, f"{CURRENCY}{order['total']:,.2f}"]
            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, order["id"])
                if col == 3:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, col, item)
        has_orders = bool(orders)
        self.table.setVisible(has_orders)
        self.empty_lbl.setVisible(not has_orders)
        self.reorder_btn.setEnabled(has_orders)

    def save(self):
        name = self.f_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Profile", "Name can't be empty.")
            return
        profile = self.win.user["profile"]
        profile["full_name"] = name
        profile["email"] = self.f_email.text().strip()
        profile["phone"] = self.f_phone.text().strip()
        profile["address"] = self.f_address.toPlainText().strip()
        self.win.persist()
        self.win.refresh_user_chip()
        self.win.refresh_cart()
        self.refresh()
        QMessageBox.information(self, "Profile", "Profile saved.")

    def change_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose a profile photo", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if not path:
            return
        folder = self.win.store.dir / "avatars"
        folder.mkdir(exist_ok=True)
        dest = folder / f"{self.win.username}{Path(path).suffix.lower()}"
        shutil.copy(path, dest)
        self.win.user["profile"]["avatar"] = str(dest)
        self.win.persist()
        self.win.refresh_user_chip()
        self.refresh()

    def remove_photo(self):
        self.win.user["profile"]["avatar"] = ""
        self.win.persist()
        self.win.refresh_user_chip()
        self.refresh()

    def reorder(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Reorder", "Select an order first.")
            return
        order_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        order = next((o for o in self.win.user["orders"] if o["id"] == order_id), None)
        if not order:
            return
        for item in order["items"]:
            food = FOOD_BY_NAME.get(item["name"])
            if food:
                self.win.add_to_cart(food, item["qty"])
        self.win.go_to("All")


# --------------------------------------------------------------------------
# Settings page
# --------------------------------------------------------------------------
class SettingsPage(QWidget):
    def __init__(self, win):
        super().__init__()
        self.setObjectName("page")
        self.win = win
        self._loading = False

        title = QLabel("⚙  Settings")
        title.setObjectName("title")
        self.tabs = QTabWidget()
        self.tabs.addTab(self._customization_tab(), "🎨  Customization")
        self.tabs.addTab(self._privacy_tab(), "🔒  Privacy")
        self.tabs.addTab(self._account_tab(), "👤  Account")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(title)
        lay.addWidget(self.tabs, 1)

    # ----- tabs
    def _customization_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(24, 24, 24, 24)
        form.setSpacing(14)

        self.theme_box = QComboBox()
        self.theme_box.addItems(list(PALETTES))
        self.theme_box.activated.connect(lambda: self._set("theme", self.theme_box.currentText(), True))

        self.accent_box = QComboBox()
        self.accent_box.addItems(list(ACCENTS) + ["Custom…"])
        self.accent_box.activated.connect(self._on_accent)

        self.font_spin = QSpinBox()
        self.font_spin.setRange(9, 16)
        self.font_spin.setSuffix(" pt")
        self.font_spin.valueChanged.connect(lambda v: self._set("font_size", v, True))

        self.cols_box = QComboBox()
        self.cols_box.addItems(["Automatic", "2", "3", "4", "5"])
        self.cols_box.activated.connect(self._on_cols)

        self.images_chk = QCheckBox("Show food images")
        self.images_chk.clicked.connect(lambda c: self._set("show_images", c))
        self.ratings_chk = QCheckBox("Show ratings on cards")
        self.ratings_chk.clicked.connect(lambda c: self._set("show_ratings", c))

        reset = QPushButton("Reset appearance to defaults")
        reset.clicked.connect(self._reset_appearance)

        form.addRow("Theme", self.theme_box)
        form.addRow("Accent colour", self.accent_box)
        form.addRow("Font size", self.font_spin)
        form.addRow("Cards per row", self.cols_box)
        form.addRow("", self.images_chk)
        form.addRow("", self.ratings_chk)
        form.addRow("", reset)
        return w

    def _privacy_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 16, 24, 16)

        signin = QGroupBox("Sign-in && security")
        sl = QVBoxLayout(signin)
        self.stay_chk = QCheckBox("Keep me signed in on this device")
        self.stay_chk.clicked.connect(self._on_stay)
        self.confirm_chk = QCheckBox("Ask for my password before placing an order")
        self.confirm_chk.clicked.connect(lambda c: self._set("confirm_orders", c))
        sl.addWidget(self.stay_chk)
        sl.addWidget(self.confirm_chk)

        display = QGroupBox("On screen")
        dl = QVBoxLayout(display)
        self.mask_chk = QCheckBox("Mask my email and phone in my profile and receipts")
        self.mask_chk.clicked.connect(lambda c: self._set("mask_contact", c))
        dl.addWidget(self.mask_chk)

        data = QGroupBox("Your data")
        dal = QVBoxLayout(data)
        self.history_chk = QCheckBox("Save my order history")
        self.history_chk.clicked.connect(lambda c: self._set("save_history", c))
        dal.addWidget(self.history_chk)
        self.clear_hist_btn = QPushButton("Clear order history")
        self.clear_hist_btn.clicked.connect(self._clear_history)
        self.clear_fav_btn = QPushButton("Clear favorites")
        self.clear_fav_btn.clicked.connect(self._clear_favorites)
        self.export_btn = QPushButton("Export my data…")
        self.export_btn.clicked.connect(self._export)
        self.delete_btn = QPushButton("Delete my account")
        self.delete_btn.setObjectName("danger")
        self.delete_btn.clicked.connect(self._delete_account)
        row = QHBoxLayout()
        for b in (self.clear_hist_btn, self.clear_fav_btn, self.export_btn):
            row.addWidget(b)
        dal.addLayout(row)
        dal.addWidget(self.delete_btn)

        self.privacy_note = QLabel("Guest mode: nothing is saved, so most privacy options don't apply.")
        self.privacy_note.setObjectName("banner")
        self.privacy_note.setWordWrap(True)

        lay.addWidget(self.privacy_note)
        lay.addWidget(signin)
        lay.addWidget(display)
        lay.addWidget(data)
        lay.addStretch()
        return w

    def _account_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 16, 24, 16)

        self.acc_info = QLabel()
        self.acc_info.setObjectName("h2")

        pw_box = QGroupBox("Change password")
        form = QFormLayout(pw_box)
        self.pw_old = QLineEdit()
        self.pw_new = QLineEdit()
        self.pw_new2 = QLineEdit()
        for e in (self.pw_old, self.pw_new, self.pw_new2):
            e.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Current password", self.pw_old)
        form.addRow("New password", self.pw_new)
        form.addRow("Confirm new", self.pw_new2)
        self.pw_btn = QPushButton("Update password")
        self.pw_btn.setObjectName("primary")
        self.pw_btn.clicked.connect(self._change_password)
        form.addRow("", self.pw_btn)
        self.pw_box = pw_box

        self.logout_btn = QPushButton("Log out")
        self.logout_btn.clicked.connect(self.win.logout)

        lay.addWidget(self.acc_info)
        lay.addWidget(pw_box)
        lay.addWidget(self.logout_btn)
        lay.addStretch()
        return w

    # ----- state
    def load(self):
        s = self.win.settings
        is_account = self.win.username is not None
        self._loading = True
        self.theme_box.setCurrentText(s["theme"])
        accent_name = next((n for n, v in ACCENTS.items() if v.lower() == s["accent"].lower()), "Custom…")
        self.accent_box.setCurrentText(accent_name)
        self.font_spin.setValue(int(s["font_size"]))
        self.cols_box.setCurrentIndex(0 if s["columns"] == 0 else max(0, s["columns"] - 1))
        self.images_chk.setChecked(s["show_images"])
        self.ratings_chk.setChecked(s["show_ratings"])
        self.mask_chk.setChecked(s["mask_contact"])
        self.history_chk.setChecked(s["save_history"])
        self.confirm_chk.setChecked(s["confirm_orders"])
        self.stay_chk.setChecked(is_account and self.win.store.remembered_user() == self.win.username)
        self._loading = False

        for w in (self.stay_chk, self.confirm_chk, self.history_chk, self.clear_hist_btn,
                  self.clear_fav_btn, self.export_btn, self.delete_btn, self.pw_box):
            w.setEnabled(is_account)
        self.privacy_note.setVisible(not is_account)
        if is_account:
            self.acc_info.setText(f"Signed in as @{self.win.user['username']}")
            self.logout_btn.setText("Log out")
        else:
            self.acc_info.setText("You're using Kainan as a guest.")
            self.logout_btn.setText("Log in / Sign up")

    def _set(self, key, value, restyle=False):
        if self._loading:
            return
        self.win.settings[key] = value
        self.win.persist()
        self.win.on_settings_changed(restyle)

    # ----- handlers
    def _on_accent(self):
        name = self.accent_box.currentText()
        if name == "Custom…":
            color = QColorDialog.getColor(QColor(self.win.settings["accent"]), self, "Pick an accent colour")
            if not color.isValid():
                self.load()
                return
            self._set("accent", color.name(), True)
        else:
            self._set("accent", ACCENTS[name], True)

    def _on_cols(self):
        idx = self.cols_box.currentIndex()
        self._set("columns", 0 if idx == 0 else idx + 1)

    def _reset_appearance(self):
        for key in ("theme", "accent", "font_size", "columns", "show_images", "show_ratings"):
            self.win.settings[key] = DEFAULT_SETTINGS[key]
        self.win.persist()
        self.win.on_settings_changed(True)
        self.load()

    def _on_stay(self, checked):
        if self._loading or self.win.username is None:
            return
        if checked:
            self.win.store.remember(self.win.username)
        else:
            self.win.store.forget_session()

    def _clear_history(self):
        if QMessageBox.question(self, "Clear order history", "Delete all saved orders?") \
                == QMessageBox.StandardButton.Yes:
            self.win.user["orders"] = []
            self.win.persist()

    def _clear_favorites(self):
        if QMessageBox.question(self, "Clear favorites", "Remove all favorites?") \
                == QMessageBox.StandardButton.Yes:
            self.win.user["favorites"] = []
            self.win.persist()
            self.win.refresh_menu()

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export my data", "kainan_my_data.json", "JSON (*.json)")
        if not path:
            return
        u = self.win.user
        data = {k: u[k] for k in ("username", "created", "profile", "settings", "favorites", "orders") if k in u}
        Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), "utf-8")
        QMessageBox.information(self, "Export", f"Saved to:\n{path}")

    def _ask_password(self, title):
        pw, ok = QInputDialog.getText(self, title, "Enter your password:", QLineEdit.EchoMode.Password)
        return pw if ok else None

    def _delete_account(self):
        if QMessageBox.question(
                self, "Delete account",
                "This permanently deletes your account, favorites and order history.\nContinue?") \
                != QMessageBox.StandardButton.Yes:
            return
        pw = self._ask_password("Confirm deletion")
        if pw is None:
            return
        if not self.win.store.verify(self.win.username, pw):
            QMessageBox.warning(self, "Delete account", "Wrong password.")
            return
        avatar = self.win.user["profile"].get("avatar")
        if avatar:
            try:
                Path(avatar).unlink()
            except OSError:
                pass
        del self.win.store.users[self.win.username]
        self.win.store.save()
        self.win.logout()

    def _change_password(self):
        if not self.win.store.verify(self.win.username, self.pw_old.text()):
            QMessageBox.warning(self, "Password", "Current password is wrong.")
            return
        if len(self.pw_new.text()) < 6:
            QMessageBox.warning(self, "Password", "New password must be at least 6 characters.")
            return
        if self.pw_new.text() != self.pw_new2.text():
            QMessageBox.warning(self, "Password", "New passwords don't match.")
            return
        self.win.store.set_password(self.win.username, self.pw_new.text())
        for e in (self.pw_old, self.pw_new, self.pw_new2):
            e.clear()
        QMessageBox.information(self, "Password", "Password updated.")


# --------------------------------------------------------------------------
# Main window
# --------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, store, username):
        super().__init__()
        self.store = store
        self.username = username            # None => guest
        self.user = store.users[username] if username else store.new_guest()
        self.logout_requested = False
        self.cart = {}                       # name -> [Food, qty]
        self.cards = []
        self.category = "All"

        self.setWindowTitle(f"{APP_NAME} - Food Menu")
        self.resize(1320, 780)
        self._build_ui()

        self.relayout_timer = QTimer(self)
        self.relayout_timer.setSingleShot(True)
        self.relayout_timer.timeout.connect(self.relayout_grid)

        apply_app_theme(QApplication.instance(), self.settings)
        self.refresh_user_chip()
        self.refresh_menu()
        self.refresh_cart()

    @property
    def settings(self):
        return self.user["settings"]

    def persist(self):
        if self.username:
            self.store.save()

    def fmt(self, value):
        return f"{CURRENCY}{value:,.2f}"

    # ----- UI construction
    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(16)

        # Sidebar
        side = QVBoxLayout()
        brand = QLabel("🍽  Kainan")
        brand.setObjectName("title")
        chip = QHBoxLayout()
        self.chip_avatar = QLabel()
        chip_text = QVBoxLayout()
        self.chip_name = QLabel()
        self.chip_name.setObjectName("h2")
        self.chip_sub = QLabel()
        self.chip_sub.setObjectName("muted")
        chip_text.addWidget(self.chip_name)
        chip_text.addWidget(self.chip_sub)
        chip.addWidget(self.chip_avatar)
        chip.addLayout(chip_text)
        chip.addStretch()

        self.nav = QListWidget()
        self.nav.setObjectName("sidebar")
        self.nav.setFixedWidth(200)
        for key in CATEGORIES:
            self._add_nav(f"{CAT_ICONS[key]}  {key}", key)
        divider = QListWidgetItem("")
        divider.setFlags(Qt.ItemFlag.NoItemFlags)
        divider.setSizeHint(QSize(0, 16))
        self.nav.addItem(divider)
        self._add_nav("👤  Profile", "profile")
        self._add_nav("⚙  Settings", "settings")
        self.nav.currentItemChanged.connect(self.on_nav)

        self.logout_btn = QPushButton("↪  Log out")
        self.logout_btn.clicked.connect(self.logout)

        side.addWidget(brand)
        side.addSpacing(4)
        side.addLayout(chip)
        side.addSpacing(8)
        side.addWidget(self.nav, 1)
        side.addWidget(self.logout_btn)
        outer.addLayout(side)

        # Pages
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_menu_page())
        self.profile_page = ProfilePage(self)
        self.settings_page = SettingsPage(self)
        self.stack.addWidget(self.profile_page)
        self.stack.addWidget(self.settings_page)
        outer.addWidget(self.stack, 1)

        # Cart panel
        outer.addWidget(self._build_cart_panel())

        self.nav.setCurrentRow(0)

    def _add_nav(self, text, key):
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, key)
        self.nav.addItem(item)

    def _build_menu_page(self):
        page = QWidget()
        page.setObjectName("page")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)

        top = QHBoxLayout()
        self.page_title = QLabel("All dishes")
        self.page_title.setObjectName("title")
        top.addWidget(self.page_title)
        top.addStretch()
        lay.addLayout(top)

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search dishes...")
        self.search.textChanged.connect(self.refresh_menu)
        self.veg_only = QCheckBox("Vegetarian only")
        self.veg_only.toggled.connect(self.refresh_menu)
        self.sort_box = QComboBox()
        self.sort_box.addItems(["Name (A-Z)", "Price: low to high", "Price: high to low", "Top rated"])
        self.sort_box.currentIndexChanged.connect(self.refresh_menu)
        filters.addWidget(self.search, 1)
        filters.addWidget(self.veg_only)
        filters.addWidget(self.sort_box)
        lay.addLayout(filters)

        self.result_label = QLabel()
        self.result_label.setObjectName("muted")
        lay.addWidget(self.result_label)

        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setSpacing(GRID_GAP)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.grid_host)
        lay.addWidget(self.scroll, 1)

        self.empty_label = QLabel()
        self.empty_label.setObjectName("muted")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.empty_label)
        return page

    def _build_cart_panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedWidth(320)
        self.cart_panel = panel
        p = QVBoxLayout(panel)
        p.setContentsMargins(14, 14, 14, 14)
        heading = QLabel("🧾  Your Order")
        heading.setObjectName("title")
        p.addWidget(heading)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Item", "Qty", "Subtotal"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        p.addWidget(self.table, 1)

        row = QHBoxLayout()
        self.minus_btn = QPushButton("−")
        self.plus_btn = QPushButton("+")
        self.remove_btn = QPushButton("Remove")
        self.minus_btn.clicked.connect(lambda: self.change_qty(-1))
        self.plus_btn.clicked.connect(lambda: self.change_qty(+1))
        self.remove_btn.clicked.connect(self.remove_selected)
        row.addWidget(self.minus_btn)
        row.addWidget(self.plus_btn)
        row.addWidget(self.remove_btn, 1)
        p.addLayout(row)

        self.items_label = QLabel()
        self.items_label.setObjectName("muted")
        self.deliver_label = QLabel()
        self.deliver_label.setObjectName("muted")
        self.deliver_label.setWordWrap(True)
        self.total_label = QLabel()
        self.total_label.setObjectName("total")
        p.addWidget(self.items_label)
        p.addWidget(self.deliver_label)
        p.addWidget(self.total_label)

        self.place_btn = QPushButton("Place Order")
        self.place_btn.setObjectName("primary")
        self.place_btn.clicked.connect(self.place_order)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_cart)
        p.addWidget(self.place_btn)
        p.addWidget(self.clear_btn)
        return panel

    # ----- navigation
    def on_nav(self, current, _previous):
        if current is None:
            return
        key = current.data(Qt.ItemDataRole.UserRole)
        if key in CATEGORIES:
            self.category = key
            self.stack.setCurrentIndex(0)
            self.cart_panel.show()
            self.refresh_menu()
        elif key == "profile":
            self.profile_page.refresh()
            self.stack.setCurrentIndex(1)
            self.cart_panel.hide()
        elif key == "settings":
            self.settings_page.load()
            self.stack.setCurrentIndex(2)
            self.cart_panel.hide()

    def go_to(self, key):
        for row in range(self.nav.count()):
            if self.nav.item(row).data(Qt.ItemDataRole.UserRole) == key:
                self.nav.setCurrentRow(row)
                return

    def logout(self):
        self.store.forget_session()
        self.logout_requested = True
        self.close()

    def refresh_user_chip(self):
        profile = self.user["profile"]
        name = profile["full_name"] or "Guest"
        self.chip_avatar.setPixmap(make_avatar(name, profile["avatar"], 44, self.settings["accent"]))
        self.chip_name.setText(name)
        self.chip_sub.setText(f"@{self.user['username']}" if self.username else "Guest mode")
        self.logout_btn.setText("↪  Log out" if self.username else "↪  Log in / Sign up")

    def on_settings_changed(self, restyle):
        if restyle:
            apply_app_theme(QApplication.instance(), self.settings)
            self.refresh_user_chip()
        self.refresh_menu()
        self.refresh_cart()

    # ----- menu
    def filtered_foods(self):
        query = self.search.text().strip().lower()
        favs = set(self.user["favorites"])
        foods = [
            f for f in FOODS
            if (self.category == "All" or (self.category == "Favorites" and f.name in favs)
                or f.category == self.category)
            and (not query or query in f.name.lower() or query in f.desc.lower())
            and (not self.veg_only.isChecked() or f.veg)
        ]
        sort = self.sort_box.currentIndex()
        if sort == 0:
            foods.sort(key=lambda f: f.name)
        elif sort == 1:
            foods.sort(key=lambda f: f.price)
        elif sort == 2:
            foods.sort(key=lambda f: -f.price)
        else:
            foods.sort(key=lambda f: -f.rating)
        return foods

    def column_count(self):
        cols = self.settings["columns"]
        if cols > 0:
            return cols
        available = self.scroll.viewport().width()
        return max(1, (available + GRID_GAP) // (CARD_W + GRID_GAP))

    def _clear_cards(self):
        while self.grid.count():
            self.grid.takeAt(0)
        for card in self.cards:
            card.setParent(None)
            card.deleteLater()
        self.cards = []

    def refresh_menu(self, *_):
        if not hasattr(self, "scroll"):
            return
        scroll_pos = self.scroll.verticalScrollBar().value()
        self._clear_cards()

        favs = set(self.user["favorites"])
        foods = self.filtered_foods()
        s = self.settings
        for food in foods:
            card = FoodCard(food, food.name in favs, s["show_images"], s["show_ratings"])
            card.add_clicked.connect(self.add_to_cart)
            card.details_clicked.connect(self.show_details)
            card.fav_toggled.connect(self.toggle_favorite)
            self.cards.append(card)
        self.relayout_grid()

        title = {"All": "All dishes", "Favorites": "Your favorites"}.get(self.category, self.category)
        self.page_title.setText(title)
        self.result_label.setText(f"{len(foods)} dish{'es' if len(foods) != 1 else ''}")
        if not foods:
            self.empty_label.setText(
                "No favorites yet - tap ♡ on a dish to save it here."
                if self.category == "Favorites" and not favs and not self.search.text()
                else "No dishes match your filters.")
        self.empty_label.setVisible(not foods)
        QTimer.singleShot(0, lambda: self.scroll.verticalScrollBar().setValue(scroll_pos))

    def relayout_grid(self):
        cols = self.column_count()
        while self.grid.count():
            self.grid.takeAt(0)
        for i, card in enumerate(self.cards):
            self.grid.addWidget(card, i // cols, i % cols,
                                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            card.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "relayout_timer") and self.settings["columns"] == 0:
            self.relayout_timer.start(60)

    def show_details(self, food):
        DetailsDialog(
            food, food.name in self.user["favorites"], self.settings["show_images"],
            self.add_to_cart, self.toggle_favorite, self,
        ).exec()
        self.refresh_menu()

    def toggle_favorite(self, food):
        favs = self.user["favorites"]
        if food.name in favs:
            favs.remove(food.name)
        else:
            favs.append(food.name)
        self.persist()
        if self.category == "Favorites":
            self.refresh_menu()
        else:
            for card in self.cards:
                if card.food.name == food.name:
                    card.set_fav(food.name in favs)

    # ----- cart
    def add_to_cart(self, food, qty=1):
        if food.name in self.cart:
            self.cart[food.name][1] += qty
        else:
            self.cart[food.name] = [food, qty]
        self.refresh_cart(select=food.name)

    def selected_name(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def change_qty(self, delta):
        name = self.selected_name()
        if not name:
            return
        self.cart[name][1] += delta
        if self.cart[name][1] <= 0:
            del self.cart[name]
            name = None
        self.refresh_cart(select=name)

    def remove_selected(self):
        name = self.selected_name()
        if name:
            del self.cart[name]
            self.refresh_cart()

    def clear_cart(self):
        self.cart.clear()
        self.refresh_cart()

    def cart_total(self):
        return sum(f.price * q for f, q in self.cart.values())

    def refresh_cart(self, select=None):
        if not hasattr(self, "table"):
            return
        self.table.setRowCount(len(self.cart))
        select_row = -1
        for row, (name, (food, qty)) in enumerate(self.cart.items()):
            name_item = QTableWidgetItem(f"{food.emoji} {name}")
            name_item.setData(Qt.ItemDataRole.UserRole, name)
            qty_item = QTableWidgetItem(str(qty))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            sub_item = QTableWidgetItem(self.fmt(food.price * qty))
            sub_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, qty_item)
            self.table.setItem(row, 2, sub_item)
            if name == select:
                select_row = row
        if select_row >= 0:
            self.table.selectRow(select_row)

        count = sum(q for _f, q in self.cart.values())
        self.items_label.setText(f"{count} item{'s' if count != 1 else ''}")
        address = self.user["profile"]["address"]
        self.deliver_label.setText(
            f"📍 Deliver to: {address}" if address else "📍 Pick-up (no address saved in profile)")
        self.total_label.setText(f"Total: {self.fmt(self.cart_total())}")
        has_items = bool(self.cart)
        for btn in (self.minus_btn, self.plus_btn, self.remove_btn, self.place_btn, self.clear_btn):
            btn.setEnabled(has_items)

    def place_order(self):
        if not self.cart:
            return
        if self.username and self.settings["confirm_orders"]:
            pw, ok = QInputDialog.getText(
                self, "Confirm order", "Enter your password to place this order:",
                QLineEdit.EchoMode.Password)
            if not ok:
                return
            if not self.store.verify(self.username, pw):
                QMessageBox.warning(self, "Confirm order", "Wrong password.")
                return

        total = self.cart_total()
        items = [{"name": f.name, "qty": q, "price": f.price} for f, q in self.cart.values()]
        order_id = f"#{len(self.user['orders']) + 1:04d}"
        saved = bool(self.username and self.settings["save_history"])
        if saved:
            self.user["orders"].append({
                "id": order_id,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "items": items,
                "total": total,
            })
            self.persist()

        profile = self.user["profile"]
        email = mask_email(profile["email"]) if self.settings["mask_contact"] else profile["email"]
        lines = "\n".join(f"{i['qty']} × {i['name']}" for i in items)
        where = profile["address"] or "Pick-up"
        receipt = f"Thank you, {profile['full_name'] or 'guest'}!\n\n{lines}\n\n" \
                  f"Total: {self.fmt(total)}\nDelivery: {where}"
        if email:
            receipt += f"\nReceipt sent to: {email}"
        if not saved:
            receipt += "\n\n(This order was not saved to your history.)"
        QMessageBox.information(self, f"Order placed {order_id if saved else ''}".strip(), receipt)
        self.clear_cart()


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    store = Store()

    while True:
        apply_app_theme(app, DEFAULT_SETTINGS)
        remembered = store.remembered_user()
        if remembered:
            username = remembered
        else:
            dialog = LoginDialog(store)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                break
            username = dialog.username
        window = MainWindow(store, username)
        window.show()
        app.exec()
        if not window.logout_requested:
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())