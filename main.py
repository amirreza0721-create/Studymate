# -*- coding: utf-8 -*-
"""
StudyMate 3.3 Final — Professional Study Assistant
Single-file, production-ready, crash-proof.
"""

import os
import sys
import math
import json
import sqlite3
import wave
import struct
from datetime import datetime, date, timedelta

# ══════════════════════════════════════════════════════════════
# SAFE IMPORTS
# ══════════════════════════════════════════════════════════════
try:
    import arabic_reshaper
    from bidi.algorithm import get_display as _bidi_get_display
    _HAS_RESHAPER = True
except Exception:
    _HAS_RESHAPER = False

    def _bidi_get_display(s):
        return str(s)


def get_display(s):
    return str(s) if not _HAS_RESHAPER else _bidi_get_display(s)


try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.core.window import Window
    from kivy.core.audio import SoundLoader
    from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, Ellipse
    from kivy.metrics import dp
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.anchorlayout import AnchorLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.spinner import Spinner
    from kivy.uix.textinput import TextInput
    from kivy.uix.popup import Popup
    from kivy.uix.widget import Widget
except ImportError:
    print("[StudyMate] Kivy is required. Install: pip install kivy")
    sys.exit(1)

try:
    from plyer import notification as plyer_notif
except Exception:
    plyer_notif = None

# ══════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════
DB_FILE = "studymate.db"
ASSETS = "assets"
BEEP_FILE = os.path.join(ASSETS, "beep.wav")

XP_PER_LEVEL = 500
MAX_LEVEL = 100

POMODORO_WORK = 25 * 60
POMODORO_SHORT = 5 * 60
POMODORO_LONG = 15 * 60
POMODORO_CYCLES = 4


def _find_font():
    for c in ("fonts/Vazir.ttf", "fonts/Vazirmatn.ttf", "fonts/Sahel.ttf",
              "fonts/BYekan.ttf", "Vazir.ttf", "Vazirmatn.ttf"):
        if os.path.exists(c):
            return c
    return "Roboto"


FONT = _find_font()

# ══════════════════════════════════════════════════════════════
# THEMES
# ══════════════════════════════════════════════════════════════
THEMES = {
    "dark": {
        "name": "dark", "label": "شب بنفش",
        "bg": (0.045, 0.035, 0.10, 1),
        "card": (0.105, 0.090, 0.205, 1),
        "card2": (0.145, 0.120, 0.265, 1),
        "border": (0.22, 0.19, 0.40, 1),
        "primary": (0.60, 0.36, 0.98, 1),
        "primary_d": (0.42, 0.22, 0.78, 1),
        "secondary": (0.28, 0.80, 0.95, 1),
        "accent": (1.00, 0.42, 0.68, 1),
        "success": (0.18, 0.85, 0.55, 1),
        "danger": (0.95, 0.30, 0.42, 1),
        "warning": (1.00, 0.72, 0.30, 1),
        "fire": (1.00, 0.45, 0.20, 1),
        "text": (0.97, 0.96, 1.00, 1),
        "muted": (0.66, 0.66, 0.82, 1),
        "timer": (0.78, 0.62, 1.00, 1),
        "on_prim": (1, 1, 1, 1),
    },
    "light": {
        "name": "light", "label": "روز روشن",
        "bg": (0.965, 0.955, 1.00, 1),
        "card": (1.00, 1.00, 1.00, 1),
        "card2": (0.945, 0.935, 0.985, 1),
        "border": (0.86, 0.83, 0.94, 1),
        "primary": (0.48, 0.24, 0.90, 1),
        "primary_d": (0.36, 0.16, 0.74, 1),
        "secondary": (0.10, 0.60, 0.82, 1),
        "accent": (0.92, 0.22, 0.55, 1),
        "success": (0.10, 0.72, 0.42, 1),
        "danger": (0.88, 0.22, 0.32, 1),
        "warning": (0.95, 0.62, 0.15, 1),
        "fire": (0.95, 0.35, 0.10, 1),
        "text": (0.10, 0.08, 0.22, 1),
        "muted": (0.42, 0.40, 0.55, 1),
        "timer": (0.42, 0.18, 0.82, 1),
        "on_prim": (1, 1, 1, 1),
    },
    "ocean": {
        "name": "ocean", "label": "اقیانوس",
        "bg": (0.02, 0.06, 0.12, 1),
        "card": (0.06, 0.14, 0.24, 1),
        "card2": (0.09, 0.20, 0.32, 1),
        "border": (0.14, 0.28, 0.42, 1),
        "primary": (0.20, 0.75, 0.90, 1),
        "primary_d": (0.10, 0.55, 0.75, 1),
        "secondary": (0.40, 0.90, 0.75, 1),
        "accent": (1.00, 0.60, 0.40, 1),
        "success": (0.25, 0.85, 0.55, 1),
        "danger": (0.95, 0.35, 0.42, 1),
        "warning": (1.00, 0.78, 0.35, 1),
        "fire": (1.00, 0.55, 0.25, 1),
        "text": (0.92, 0.97, 1.00, 1),
        "muted": (0.55, 0.70, 0.82, 1),
        "timer": (0.40, 0.85, 1.00, 1),
        "on_prim": (1, 1, 1, 1),
    },
    "forest": {
        "name": "forest", "label": "جنگل",
        "bg": (0.04, 0.09, 0.06, 1),
        "card": (0.10, 0.20, 0.14, 1),
        "card2": (0.14, 0.28, 0.20, 1),
        "border": (0.20, 0.36, 0.26, 1),
        "primary": (0.30, 0.85, 0.50, 1),
        "primary_d": (0.15, 0.65, 0.38, 1),
        "secondary": (0.85, 0.85, 0.30, 1),
        "accent": (1.00, 0.55, 0.35, 1),
        "success": (0.30, 0.90, 0.55, 1),
        "danger": (0.95, 0.32, 0.38, 1),
        "warning": (1.00, 0.78, 0.35, 1),
        "fire": (1.00, 0.55, 0.20, 1),
        "text": (0.94, 1.00, 0.95, 1),
        "muted": (0.62, 0.78, 0.66, 1),
        "timer": (0.55, 1.00, 0.70, 1),
        "on_prim": (1, 1, 1, 1),
    },
}

THEME = dict(THEMES["dark"])


def set_theme(key):
    if key in THEMES:
        THEME.clear()
        THEME.update(THEMES[key])
    try:
        Window.clearcolor = THEME["bg"]
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def fa(text):
    if not _HAS_RESHAPER:
        return str(text)
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return str(text)


def fmt_min(seconds):
    m = int(seconds // 60)
    h = m // 60
    return f"{h}س {m % 60}د" if h > 0 else f"{m}د"


def fmt_long(seconds):
    m = int(seconds // 60)
    h = m // 60
    return f"{h} ساعت و {m % 60} دقیقه" if h > 0 else f"{m} دقیقه"


def fmt_clock(sec):
    sec = max(0, int(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


def today_str():
    return date.today().isoformat()


def greeting():
    h = datetime.now().hour
    if 5 <= h < 12:
        return "صبح بخیر ☀️"
    if 12 <= h < 17:
        return "ظهر بخیر 🌤"
    if 17 <= h < 21:
        return "عصر بخیر 🌆"
    return "شب بخیر 🌙"


def xp_to_level(xp):
    lvl = min(MAX_LEVEL, 1 + int(xp // XP_PER_LEVEL))
    in_lvl = xp % XP_PER_LEVEL
    return lvl, in_lvl, in_lvl / XP_PER_LEVEL


def make_beep():
    if os.path.exists(BEEP_FILE):
        return BEEP_FILE
    try:
        os.makedirs(ASSETS, exist_ok=True)
        fr, dur, freq = 44100, 0.35, 880
        with wave.open(BEEP_FILE, "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(fr)
            frames = []
            n = int(dur * fr)
            for i in range(n):
                t = i / n
                env = min(1.0, t * 12, (1 - t) * 12)
                v = int(32767 * 0.45 * env * math.sin(2 * math.pi * freq * i / fr))
                frames.append(struct.pack("<h", v))
            w.writeframes(b"".join(frames))
        return BEEP_FILE
    except Exception:
        return None


def compute_streak(dates_set):
    if not dates_set:
        return 0
    d = date.today()
    if d.isoformat() not in dates_set:
        d -= timedelta(days=1)
        if d.isoformat() not in dates_set:
            return 0
    s = 0
    while d.isoformat() in dates_set:
        s += 1
        d -= timedelta(days=1)
    return s


def r4(px):
    r = dp(px) if isinstance(px, (int, float)) else px
    return [r, r, r, r]

# ══════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════
class DB:
    def __init__(self, path=DB_FILE):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#7C5CFF',
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                seconds INTEGER,
                date TEXT,
                time TEXT,
                note TEXT,
                mood INTEGER DEFAULT 0,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                front TEXT,
                back TEXT,
                ease REAL DEFAULT 2.5,
                interval INTEGER DEFAULT 0,
                repetitions INTEGER DEFAULT 0,
                next_review TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                subject TEXT,
                due TEXT,
                done INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 1,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                body TEXT,
                subject TEXT,
                created_at TEXT,
                updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS achievements (
                key TEXT PRIMARY KEY,
                earned_at TEXT
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        self.conn.commit()

    # ---- Settings ----
    def get_setting(self, key, default=None):
        try:
            r = self.conn.execute(
                "SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            if r is None:
                return default
            try:
                return json.loads(r["value"])
            except Exception:
                return r["value"]
        except Exception:
            return default

    def set_setting(self, key, value):
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)",
                (key, json.dumps(value, ensure_ascii=False)))
            self.conn.commit()
        except Exception:
            pass

    # ---- Subjects ----
    def subjects(self):
        try:
            return [dict(r) for r in self.conn.execute(
                "SELECT * FROM subjects ORDER BY id").fetchall()]
        except Exception:
            return []

    def add_subject(self, name):
        try:
            self.conn.execute(
                "INSERT INTO subjects (name, created_at) VALUES (?,?)",
                (name, datetime.now().isoformat()))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception:
            return False

    def delete_subject(self, name):
        try:
            self.conn.execute("DELETE FROM subjects WHERE name=?", (name,))
            self.conn.commit()
        except Exception:
            pass

    # ---- Sessions ----
    def add_session(self, subject, seconds, note="", mood=0):
        try:
            now = datetime.now()
            self.conn.execute(
                """INSERT INTO sessions (subject, seconds, date, time, note, mood, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (subject, int(seconds), now.date().isoformat(),
                 now.strftime("%H:%M"), note, mood, now.isoformat()))
            self.conn.commit()
        except Exception:
            pass

    def total_seconds(self):
        try:
            return self.conn.execute(
                "SELECT COALESCE(SUM(seconds),0) s FROM sessions").fetchone()["s"]
        except Exception:
            return 0

    def total_sessions(self):
        try:
            return self.conn.execute(
                "SELECT COUNT(*) n FROM sessions").fetchone()["n"]
        except Exception:
            return 0

    def today_seconds(self):
        try:
            return self.conn.execute(
                "SELECT COALESCE(SUM(seconds),0) s FROM sessions WHERE date=?",
                (today_str(),)).fetchone()["s"]
        except Exception:
            return 0

    def today_sessions(self):
        try:
            return self.conn.execute(
                "SELECT COUNT(*) n FROM sessions WHERE date=?",
                (today_str(),)).fetchone()["n"]
        except Exception:
            return 0

    def seconds_on(self, d):
        try:
            return self.conn.execute(
                "SELECT COALESCE(SUM(seconds),0) s FROM sessions WHERE date=?",
                (d.isoformat(),)).fetchone()["s"]
        except Exception:
            return 0

    def subject_stats(self):
        try:
            return [dict(r) for r in self.conn.execute(
                """SELECT subject, SUM(seconds) s, COUNT(*) n
                   FROM sessions GROUP BY subject ORDER BY s DESC""").fetchall()]
        except Exception:
            return []

    def session_dates(self):
        try:
            return {r["date"] for r in self.conn.execute(
                "SELECT DISTINCT date FROM sessions").fetchall()}
        except Exception:
            return set()

    # ---- Flashcards ----
    def flashcards(self, subject=None):
        try:
            if subject:
                return [dict(r) for r in self.conn.execute(
                    "SELECT * FROM flashcards WHERE subject=? ORDER BY id DESC",
                    (subject,)).fetchall()]
            return [dict(r) for r in self.conn.execute(
                "SELECT * FROM flashcards ORDER BY id DESC").fetchall()]
        except Exception:
            return []

    def due_flashcards(self, subject=None):
        try:
            today = today_str()
            if subject:
                return [dict(r) for r in self.conn.execute(
                    """SELECT * FROM flashcards WHERE subject=?
                       AND (next_review IS NULL OR next_review<=?) ORDER BY id""",
                    (subject, today)).fetchall()]
            return [dict(r) for r in self.conn.execute(
                """SELECT * FROM flashcards
                   WHERE (next_review IS NULL OR next_review<=?) ORDER BY id""",
                (today,)).fetchall()]
        except Exception:
            return []

    def get_flashcard(self, fc_id):
        try:
            r = self.conn.execute(
                "SELECT * FROM flashcards WHERE id=?", (fc_id,)).fetchone()
            return dict(r) if r else None
        except Exception:
            return None

    def add_flashcard(self, subject, front, back):
        try:
            self.conn.execute(
                """INSERT INTO flashcards (subject, front, back, next_review, created_at)
                   VALUES (?,?,?,?,?)""",
                (subject, front, back, today_str(), datetime.now().isoformat()))
            self.conn.commit()
        except Exception:
            pass

    def update_flashcard(self, fc_id, ease, interval, reps, next_review):
        try:
            self.conn.execute(
                """UPDATE flashcards SET ease=?, interval=?, repetitions=?, next_review=?
                   WHERE id=?""",
                (ease, interval, reps, next_review, fc_id))
            self.conn.commit()
        except Exception:
            pass

    def delete_flashcard(self, fc_id):
        try:
            self.conn.execute("DELETE FROM flashcards WHERE id=?", (fc_id,))
            self.conn.commit()
        except Exception:
            pass

    def flashcards_count(self):
        try:
            return self.conn.execute(
                "SELECT COUNT(*) n FROM flashcards").fetchone()["n"]
        except Exception:
            return 0

    # ---- Tasks ----
    def tasks(self):
        try:
            return [dict(r) for r in self.conn.execute(
                "SELECT * FROM tasks ORDER BY done, priority DESC, id DESC").fetchall()]
        except Exception:
            return []

    def tasks_done_count(self):
        try:
            return self.conn.execute(
                "SELECT COUNT(*) n FROM tasks WHERE done=1").fetchone()["n"]
        except Exception:
            return 0

    def add_task(self, title):
        try:
            self.conn.execute(
                "INSERT INTO tasks (title, created_at) VALUES (?,?)",
                (title, datetime.now().isoformat()))
            self.conn.commit()
        except Exception:
            pass

    def toggle_task(self, task_id, done):
        try:
            self.conn.execute(
                "UPDATE tasks SET done=? WHERE id=?",
                (1 if done else 0, task_id))
            self.conn.commit()
        except Exception:
            pass

    def delete_task(self, task_id):
        try:
            self.conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            self.conn.commit()
        except Exception:
            pass

    def open_tasks_count(self):
        try:
            return self.conn.execute(
                "SELECT COUNT(*) n FROM tasks WHERE done=0").fetchone()["n"]
        except Exception:
            return 0

    # ---- Notes ----
    def notes(self):
        try:
            return [dict(r) for r in self.conn.execute(
                "SELECT * FROM notes ORDER BY updated_at DESC").fetchall()]
        except Exception:
            return []

    def add_note(self, title, body):
        try:
            now = datetime.now().isoformat()
            self.conn.execute(
                """INSERT INTO notes (title, body, created_at, updated_at)
                   VALUES (?,?,?,?)""", (title, body, now, now))
            self.conn.commit()
        except Exception:
            pass

    def delete_note(self, note_id):
        try:
            self.conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
            self.conn.commit()
        except Exception:
            pass

    # ---- Achievements ----
    def earned_achievements(self):
        try:
            return {r["key"] for r in self.conn.execute(
                "SELECT key FROM achievements").fetchall()}
        except Exception:
            return set()

    def earn_achievement(self, key):
        try:
            self.conn.execute(
                "INSERT INTO achievements (key, earned_at) VALUES (?,?)",
                (key, datetime.now().isoformat()))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception:
            return False

    # ---- Backup / Reset ----
    def export_json(self):
        try:
            data = {
                "subjects": self.subjects(),
                "sessions": [dict(r) for r in self.conn.execute(
                    "SELECT * FROM sessions").fetchall()],
                "flashcards": self.flashcards(),
                "tasks": self.tasks(),
                "notes": self.notes(),
                "achievements": list(self.earned_achievements()),
            }
            return json.dumps(data, ensure_ascii=False, indent=2, default=str)
        except Exception:
            return "{}"

    def reset_all(self):
        try:
            for t in ["sessions", "flashcards", "tasks",
                      "notes", "achievements", "subjects"]:
                self.conn.execute(f"DELETE FROM {t}")
            self.conn.commit()
        except Exception:
            pass

# ══════════════════════════════════════════════════════════════
# ACHIEVEMENTS
# ══════════════════════════════════════════════════════════════
ACHIEVEMENTS = [
    ("first_step", "🌱", "اولین قدم", "اولین جلسه مطالعه"),
    ("ten_sessions", "📚", "کوشا", "۱۰ جلسه مطالعه"),
    ("fifty_sessions", "🏅", "فعال", "۵۰ جلسه مطالعه"),
    ("hundred_sessions", "💯", "صدتایی", "۱۰۰ جلسه مطالعه"),
    ("hour_1", "⏰", "یک ساعتی", "۶۰ دقیقه مطالعه"),
    ("hour_10", "🕐", "ده ساعتی", "۶۰۰ دقیقه مطالعه"),
    ("hour_50", "⏳", "پنجاه ساعتی", "۳۰۰۰ دقیقه مطالعه"),
    ("streak_3", "🔥", "سه روز پیاپی", "۳ روز پشت سر هم"),
    ("streak_7", "🚀", "یک هفته پیاپی", "۷ روز پشت سر هم"),
    ("streak_30", "👑", "افسانه", "۳۰ روز پشت سر هم"),
    ("level_5", "⭐", "لِوِل ۵", "به سطح ۵ رسیدی"),
    ("level_10", "🌈", "لِوِل ۱۰", "به سطح ۱۰ رسیدی"),
    ("level_25", "🎯", "لِوِل ۲۵", "به سطح ۲۵ رسیدی"),
    ("early_bird", "🌅", "سحرخیز", "قبل از ۷ صبح مطالعه"),
    ("night_owl", "🦉", "شب‌زنده‌دار", "بعد از ۲۳ مطالعه"),
    ("flashcard_10", "🃏", "کارت‌باز", "۱۰ فلش‌کارت ساختی"),
    ("task_master", "✅", "وظیفه‌شناس", "۱۰ تسک انجام دادی"),
    ("note_keeper", "📝", "یادداشت‌بردار", "۵ یادداشت نوشتی"),
    ("subject_5", "📖", "چند‌کاره", "۵ درس داشتی"),
]
ACH_MAP = {k: (i, t, d) for k, i, t, d in ACHIEVEMENTS}

# ══════════════════════════════════════════════════════════════
# WIDGETS
# ══════════════════════════════════════════════════════════════
class Card(BoxLayout):
    def __init__(self, bg_color=None, border_color=None,
                 radius=20, border_width=1, **kwargs):
        super().__init__(**kwargs)
        self._bw = border_width
        bg = bg_color or THEME["card"]
        brd = border_color or THEME["border"]
        with self.canvas.before:
            Color(*brd)
            self._border = RoundedRectangle(pos=self.pos, size=self.size,
                                            radius=r4(radius))
            Color(*bg)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=r4(radius))
        self.bind(pos=self._update, size=self._update)
        self._update()

    def _update(self, *a):
        self._border.pos = self.pos
        self._border.size = self.size
        off = self._bw
        w = max(0, self.width - 2 * off)
        h = max(0, self.height - 2 * off)
        self._rect.pos = (self.x + off, self.y + off)
        self._rect.size = (w, h)


class RoundedButton(Button):
    def __init__(self, button_color=None, radius=18, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.button_color = button_color or THEME["primary"]
        with self.canvas.before:
            self._color = Color(*self.button_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=r4(radius))
        self.bind(pos=self._update, size=self._update, disabled=self._on_dis)

    def _update(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _on_dis(self, *a):
        self._color.rgba = ((0.30, 0.30, 0.40, 1)
                            if self.disabled else self.button_color)

    def set_color(self, c):
        self.button_color = c
        if not self.disabled:
            self._color.rgba = c


# ⚠️ مهم: اسم این کلاس عوض شد تا با ProgressBar داخلی Kivy تداخل نکنه
class SMProgressBar(Widget):
    def __init__(self, progress=0.0, color=None, bg=None, radius=10, **kwargs):
        super().__init__(**kwargs)
        self._progress = max(0.0, min(1.0, float(progress)))
        self.fill_color = color or THEME["primary"]
        self.bg_color = bg or THEME["card2"]
        self._radius = radius
        with self.canvas:
            self._bg_color = Color(*self.bg_color)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size,
                                        radius=r4(radius))
            self._fill_color = Color(*self.fill_color)
            self._fill = RoundedRectangle(pos=self.pos, size=(0, self.height),
                                          radius=r4(radius))
        self.bind(pos=self._update, size=self._update)
        self._update()

    def set_progress(self, p, color=None):
        self._progress = max(0.0, min(1.0, float(p)))
        if color:
            self.fill_color = color
            self._fill_color.rgba = color
        self._update()

    def _update(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        w = self.width * self._progress
        r = min(dp(self._radius), w / 2) if w > 0 else 0
        self._fill.pos = self.pos
        self._fill.size = (max(0, w), self.height)
        self._fill.radius = [r, r, r, r]


class Heatmap(Widget):
    def __init__(self, get_value=None, weeks=12, cell=None, gap=None, **kwargs):
        super().__init__(**kwargs)
        self.get_value = get_value or (lambda d: 0)
        self.weeks = weeks
        self.cell = cell if cell is not None else dp(13)
        self.gap = gap if gap is not None else dp(3)
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *a):
        self.canvas.clear()
        if self.width < 10 or self.height < 10:
            return
        tw = self.weeks * self.cell + (self.weeks - 1) * self.gap
        th = 7 * self.cell + 6 * self.gap
        ox = self.x + (self.width - tw) / 2
        oy = self.y + (self.height - th) / 2
        today = date.today()
        start = today - timedelta(days=self.weeks * 7 - 1)
        with self.canvas:
            for w in range(self.weeks):
                for d in range(7):
                    day = start + timedelta(days=w * 7 + d)
                    if day > today:
                        continue
                    minutes = self.get_value(day)
                    if minutes <= 0:
                        col = ((0.14, 0.12, 0.24, 1)
                               if THEME["name"] == "dark"
                               else (0.92, 0.91, 0.96, 1))
                    else:
                        inten = min(1.0, minutes / 60.0)
                        b = THEME["primary"]
                        f = 0.35 + 0.65 * inten
                        col = (b[0] * f, b[1] * f, b[2] * f, 1)
                    Color(*col)
                    x = ox + w * (self.cell + self.gap)
                    y = oy + (6 - d) * (self.cell + self.gap)
                    RoundedRectangle(pos=(x, y), size=(self.cell, self.cell),
                                     radius=r4(3))


class BarChart(Widget):
    def __init__(self, get_value=None, days=7, **kwargs):
        super().__init__(**kwargs)
        self.get_value = get_value or (lambda d: 0)
        self.days = days
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *a):
        self.canvas.clear()
        if self.width < 20 or self.height < 20:
            return
        today = date.today()
        days = [today - timedelta(days=self.days - 1 - i) for i in range(self.days)]
        vals = [self.get_value(d) for d in days]
        mx = max(vals + [1])
        pl, pr, pt, pb = dp(6), dp(6), dp(8), dp(28)
        w = self.width - pl - pr
        h = self.height - pt - pb
        if w <= 0 or h <= 0:
            return
        bw = w / self.days * 0.6
        step = w / self.days
        with self.canvas:
            Color(*THEME["border"])
            Rectangle(pos=(self.x + pl, self.y + pb), size=(w, dp(1)))
            for i, v in enumerate(vals):
                frac = v / mx if mx else 0
                bh = max(dp(3), h * frac)
                x = self.x + pl + i * step + (step - bw) / 2
                y = self.y + pb + 2
                col = (THEME["accent"] if i == self.days - 1
                       else (THEME["primary"] if v > 0 else THEME["card2"]))
                Color(*col)
                RoundedRectangle(pos=(x, y), size=(bw, bh), radius=r4(4))

# ══════════════════════════════════════════════════════════════
# SCREENS
# ══════════════════════════════════════════════════════════════
class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=dp(40), spacing=dp(12))
        layout.add_widget(Widget())
        holder = AnchorLayout(anchor_x="center", anchor_y="center",
                              size_hint_y=None, height=dp(160))
        logo = Card(size_hint=(None, None), size=(dp(140), dp(140)),
                    bg_color=THEME["primary"], border_color=THEME["primary"],
                    radius=70, border_width=0)
        logo.add_widget(Label(text="S", font_name=FONT, font_size=dp(78),
                              bold=True, color=THEME["on_prim"]))
        holder.add_widget(logo)
        layout.add_widget(holder)
        layout.add_widget(Label(text="StudyMate", font_name=FONT,
                                font_size=dp(38), bold=True,
                                color=THEME["text"], size_hint_y=None, height=dp(50)))
        layout.add_widget(Label(text=fa("دستیار حرفه‌ای مطالعه"), font_name=FONT,
                                font_size=dp(16), color=THEME["muted"],
                                size_hint_y=None, height=dp(30)))
        layout.add_widget(Widget())
        self.add_widget(layout)
        self._ev = None

    def on_enter(self):
        if self._ev:
            try:
                self._ev.cancel()
            except Exception:
                pass
        self._ev = Clock.schedule_once(self._go, 1.4)

    def on_leave(self):
        if self._ev:
            try:
                self._ev.cancel()
            except Exception:
                pass
            self._ev = None

    def _go(self, dt):
        if self.manager is None:
            return
        try:
            app = App.get_running_app()
            if app and app.db.get_setting("onboarded", False):
                self.manager.current = "home"
            else:
                self.manager.current = "onboarding"
        except Exception:
            pass


class OnboardingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 0
        self.slides = [
            ("🎯", "به StudyMate خوش آمدی", "همراه تو برای مطالعه‌ی هوشمندتر و منظم‌تر"),
            ("⏱", "تایمر پومودورو", "۲۵ دقیقه تمرکز، ۵ دقیقه استراحت"),
            ("🃏", "فلش‌کارت با تکرار فاصله‌دار", "مرور درست در زمان درست"),
            ("📊", "آمار و پیشرفت", "نمودار، Heatmap، استریک، سطح و نشان‌ها"),
        ]
        main = BoxLayout(orientation="vertical", padding=dp(30), spacing=dp(16))
        self.icon = Label(text="", font_name=FONT, font_size=dp(90),
                          size_hint_y=None, height=dp(140))
        self.title_lbl = Label(text="", font_name=FONT, font_size=dp(24),
                               bold=True, color=THEME["text"],
                               size_hint_y=None, height=dp(50), halign="center")
        self.title_lbl.bind(size=lambda l, s: setattr(l, "text_size", s))
        self.desc = Label(text="", font_name=FONT, font_size=dp(15),
                          color=THEME["muted"], halign="center")
        self.desc.bind(size=lambda l, s: setattr(l, "text_size", s))

        self.dots = BoxLayout(orientation="horizontal", spacing=dp(6),
                              size_hint_y=None, height=dp(20))
        self.dot_colors = []
        for _ in self.slides:
            holder = AnchorLayout(anchor_x="center", anchor_y="center")
            d = Widget(size_hint=(None, None), size=(dp(10), dp(10)))
            with d.canvas:
                c = Color(*THEME["card2"])
                e = Ellipse(pos=d.pos, size=d.size)
            d.bind(pos=lambda *a, e=e, dd=d: setattr(e, "pos", dd.pos),
                   size=lambda *a, e=e, dd=d: setattr(e, "size", dd.size))
            self.dot_colors.append(c)
            holder.add_widget(d)
            self.dots.add_widget(holder)

        next_btn = RoundedButton(text=fa("بعدی"), font_name=FONT,
                                 font_size=dp(18), bold=True,
                                 size_hint_y=None, height=dp(60),
                                 button_color=THEME["primary"])
        next_btn.bind(on_release=self.next_step)
        skip = Button(text=fa("رد کردن"), font_name=FONT, font_size=dp(14),
                      size_hint_y=None, height=dp(40),
                      background_normal="", background_color=(0, 0, 0, 0),
                      color=THEME["muted"])
        skip.bind(on_release=self.finish)
        main.add_widget(Widget())
        main.add_widget(self.icon)
        main.add_widget(self.title_lbl)
        main.add_widget(self.desc)
        main.add_widget(Widget())
        main.add_widget(self.dots)
        main.add_widget(next_btn)
        main.add_widget(skip)
        self.add_widget(main)

    def on_enter(self):
        self.update_slide()

    def update_slide(self):
        icon, title, desc = self.slides[self.step]
        self.icon.text = icon
        self.title_lbl.text = fa(title)
        self.desc.text = fa(desc)
        for i, c in enumerate(self.dot_colors):
            c.rgba = THEME["primary"] if i == self.step else THEME["card2"]

    def next_step(self, *a):
        self.step += 1
        if self.step >= len(self.slides):
            self.finish()
        else:
            self.update_slide()

    def finish(self, *a):
        if self.manager is None:
            return
        try:
            App.get_running_app().db.set_setting("onboarded", True)
            self.manager.current = "home"
        except Exception:
            pass


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView()
        main = BoxLayout(orientation="vertical", padding=dp(16),
                         spacing=dp(12), size_hint_y=None)
        main.bind(minimum_height=main.setter("height"))
        scroll.add_widget(main)

        self.greeting = Label(text="", font_name=FONT, font_size=dp(22),
                              bold=True, color=THEME["text"], halign="right",
                              size_hint_y=None, height=dp(32))
        self.greeting.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))

        hero = Card(orientation="horizontal", padding=dp(14), spacing=dp(10),
                    size_hint_y=None, height=dp(126),
                    bg_color=THEME["primary_d"], border_color=THEME["primary"])
        lvl_box = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_x=0.55)
        self.level_lbl = Label(text="", font_name=FONT, font_size=dp(20),
                               bold=True, color=(1, 1, 1, 1),
                               halign="right", size_hint_y=None, height=dp(30))
        self.level_lbl.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        self.xp_lbl = Label(text="", font_name=FONT, font_size=dp(12),
                            color=(1, 1, 1, 0.85), halign="right",
                            size_hint_y=None, height=dp(20))
        self.xp_lbl.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))

        # ✅ SMProgressBar جایگزین شد
        self.xp_bar = SMProgressBar(progress=0.0, color=THEME["warning"],
                                    bg=(1, 1, 1, 0.20), radius=6,
                                    size_hint_y=None, height=dp(10))
        lvl_box.add_widget(self.level_lbl)
        lvl_box.add_widget(self.xp_lbl)
        lvl_box.add_widget(self.xp_bar)

        streak_box = BoxLayout(orientation="vertical", size_hint_x=0.45)
        streak_box.add_widget(Label(text="🔥", font_name=FONT, font_size=dp(38),
                                    color=THEME["fire"], size_hint_y=None, height=dp(50)))
        self.streak_lbl = Label(text="", font_name=FONT, font_size=dp(13),
                                bold=True, color=(1, 1, 1, 1))
        streak_box.add_widget(self.streak_lbl)
        hero.add_widget(lvl_box)
        hero.add_widget(streak_box)

        today_card = Card(orientation="vertical", padding=dp(16),
                          spacing=dp(8), size_hint_y=None, height=dp(140))
        row1 = BoxLayout(size_hint_y=None, height=dp(24))
        l1 = Label(text=fa("امروز"), font_name=FONT, font_size=dp(14),
                   color=THEME["muted"], halign="right")
        l1.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        self.today_goal = Label(text="", font_name=FONT, font_size=dp(12),
                                color=THEME["primary"], halign="left")
        self.today_goal.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        row1.add_widget(l1)
        row1.add_widget(self.today_goal)
        self.today_time = Label(text="", font_name=FONT, font_size=dp(28),
                                bold=True, color=THEME["text"], halign="right",
                                size_hint_y=None, height=dp(40))
        self.today_time.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))

        # ✅ SMProgressBar جایگزین شد
        self.today_bar = SMProgressBar(progress=0.0, color=THEME["primary"],
                                       bg=THEME["card2"], radius=8,
                                       size_hint_y=None, height=dp(10))
        self.today_meta = Label(text="", font_name=FONT, font_size=dp(12),
                                color=THEME["muted"], halign="right",
                                size_hint_y=None, height=dp(20))
        self.today_meta.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        today_card.add_widget(row1)
        today_card.add_widget(self.today_time)
        today_card.add_widget(self.today_bar)
        today_card.add_widget(self.today_meta)

        # ✅ کد مرده حذف شد
        quick = BoxLayout(orientation="horizontal", spacing=dp(8),
                          size_hint_y=None, height=dp(84))

        def mini(icon, color):
            c = Card(orientation="vertical", padding=dp(8), spacing=dp(2),
                     bg_color=color, border_color=color)
            c.add_widget(Label(text=icon, font_name=FONT, font_size=dp(22),
                               size_hint_y=None, height=dp(30)))
            v = Label(text="", font_name=FONT, font_size=dp(11), color=THEME["text"])
            c.add_widget(v)
            return c, v

        c1, self.due_lbl = mini("🃏", THEME["card"])
        c2, self.task_lbl = mini("✅", THEME["card"])
        c3, self.sess_lbl = mini("📚", THEME["card"])
        quick.add_widget(c1)
        quick.add_widget(c2)
        quick.add_widget(c3)

        start_btn = RoundedButton(text=fa("▶ شروع مطالعه"), font_name=FONT,
                                  font_size=dp(20), bold=True,
                                  size_hint_y=None, height=dp(72),
                                  button_color=THEME["primary"], radius=22)
        start_btn.bind(on_release=lambda *a: self._go("timer"))

        def nav_row(b1, b2):
            r = BoxLayout(orientation="horizontal", spacing=dp(10),
                          size_hint_y=None, height=dp(80))
            r.add_widget(b1)
            r.add_widget(b2)
            return r

        def mkbtn(text, color, target):
            b = RoundedButton(text=fa(text), font_name=FONT, font_size=dp(14),
                              button_color=color, radius=20)
            b.bind(on_release=lambda *a: self._go(target))
            return b

        subj_btn = mkbtn("📚 درس‌ها", THEME["secondary"], "subjects")
        card_btn = mkbtn("🃏 فلش‌کارت", THEME["accent"], "flashcards")
        task_btn = mkbtn("✅ وظایف", THEME["success"], "tasks")
        note_btn = mkbtn("📝 یادداشت", THEME["warning"], "notes")
        stats_btn = mkbtn("📊 آمار", THEME["card2"], "stats")
        ach_btn = mkbtn("🏆 نشان‌ها", THEME["card2"], "achievements")

        set_btn = RoundedButton(text=fa("⚙ تنظیمات"), font_name=FONT,
                                font_size=dp(14), size_hint_y=None, height=dp(52),
                                button_color=THEME["card2"], radius=16)
        set_btn.bind(on_release=lambda *a: self._go("settings"))

        main.add_widget(self.greeting)
        main.add_widget(hero)
        main.add_widget(today_card)
        main.add_widget(quick)
        main.add_widget(start_btn)
        main.add_widget(nav_row(subj_btn, card_btn))
        main.add_widget(nav_row(task_btn, note_btn))
        main.add_widget(nav_row(stats_btn, ach_btn))
        main.add_widget(set_btn)
        self.add_widget(scroll)

    def _go(self, name):
        if self.manager is not None:
            self.manager.current = name

    def on_pre_enter(self):
        try:
            db = App.get_running_app().db
        except Exception:
            return
        self.greeting.text = fa(greeting())
        xp = int(db.total_seconds() // 60)
        lvl, in_lvl, prog = xp_to_level(xp)
        self.level_lbl.text = fa(f"لِوِل {lvl}")
        self.xp_lbl.text = fa(f"{in_lvl} / {XP_PER_LEVEL} XP")
        self.xp_bar.set_progress(prog)
        streak = compute_streak(db.session_dates())
        self.streak_lbl.text = fa(f"{streak} روز پیاپی" if streak else "شروع کن!")
        today_sec = db.today_seconds()
        try:
            goal_min = int(db.get_setting("daily_goal", 60))
        except Exception:
            goal_min = 60
        p = min(1.0, today_sec / max(1, goal_min * 60))
        self.today_time.text = fa(fmt_long(today_sec))
        col = (THEME["success"] if p >= 1
               else THEME["primary"] if p >= 0.5
               else THEME["accent"])
        self.today_bar.set_progress(p, col)
        self.today_goal.text = fa(f"هدف {goal_min}د • {int(p * 100)}%")
        self.today_meta.text = fa(
            f"{db.today_sessions()} جلسه • مجموع {fmt_min(db.total_seconds())}")
        self.due_lbl.text = fa(f"{len(db.due_flashcards())} مرور")
        self.task_lbl.text = fa(f"{db.open_tasks_count()} وظیفه")
        self.sess_lbl.text = fa(f"{db.total_sessions()} جلسه")


class TimerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = "work"
        self.cycle = 0
        self.duration = POMODORO_WORK
        self.remaining = self.duration
        self.elapsed = 0
        self.running = False
        self.event = None
        self.selected_subject = None
        self._restored = False

        scroll = ScrollView()
        main = BoxLayout(orientation="vertical", padding=dp(18),
                         spacing=dp(12), size_hint_y=None)
        main.bind(minimum_height=main.setter("height"))
        scroll.add_widget(main)

        title = Label(text=fa("تایمر پومودورو"), font_name=FONT,
                      font_size=dp(24), bold=True, color=THEME["text"],
                      halign="right", size_hint_y=None, height=dp(40))
        title.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))

        modes_row = BoxLayout(orientation="horizontal", spacing=dp(6),
                              size_hint_y=None, height=dp(44))
        self.mode_btns = {}
        for key, label in [("work", "کار"), ("short", "استراحت"), ("long", "استراحت بلند")]:
            b = RoundedButton(text=fa(label), font_name=FONT, font_size=dp(13),
                              button_color=THEME["card2"], radius=12)
            b.bind(on_release=lambda *a, k=key: self.set_mode(k))
            self.mode_btns[key] = b
            modes_row.add_widget(b)
        self.mode_btns["work"].set_color(THEME["primary"])

        subj_label = Label(text=fa("درس"), font_name=FONT, font_size=dp(13),
                           color=THEME["muted"], halign="right",
                           size_hint_y=None, height=dp(22))
        subj_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        self.subject_spinner = Spinner(text=fa("بدون درس"),
                                       values=[fa("بدون درس")],
                                       font_name=FONT, font_size=dp(15),
                                       size_hint_y=None, height=dp(50),
                                       background_normal="",
                                       background_color=THEME["secondary"],
                                       color=THEME["on_prim"])

        timer_card = Card(orientation="vertical", padding=dp(20), spacing=dp(8),
                          size_hint_y=None, height=dp(240))
        self.timer_label = Label(text="25:00", font_name=FONT, font_size=dp(78),
                                 bold=True, color=THEME["timer"], halign="center")
        self.timer_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        self.status = Label(text=fa("آماده شروع"), font_name=FONT, font_size=dp(14),
                            color=THEME["muted"], halign="center",
                            size_hint_y=None, height=dp(24))
        self.status.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        self.cycle_lbl = Label(text="", font_name=FONT, font_size=dp(12),
                               color=THEME["muted"], halign="center",
                               size_hint_y=None, height=dp(20))
        self.cycle_lbl.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        timer_card.add_widget(self.timer_label)
        timer_card.add_widget(self.status)
        timer_card.add_widget(self.cycle_lbl)

        self.start_btn = RoundedButton(text=fa("شروع"), font_name=FONT,
                                       font_size=dp(19), bold=True,
                                       size_hint_y=None, height=dp(64),
                                       button_color=THEME["primary"], radius=22)
        self.start_btn.bind(on_release=self.toggle)

        row = BoxLayout(orientation="horizontal", spacing=dp(10),
                        size_hint_y=None, height=dp(52))
        reset_btn = RoundedButton(text=fa("ریست"), font_name=FONT,
                                  font_size=dp(15), button_color=THEME["card2"],
                                  radius=14)
        reset_btn.bind(on_release=self.reset)
        skip_btn = RoundedButton(text=fa("رد کردن"), font_name=FONT,
                                 font_size=dp(15), button_color=THEME["card2"],
                                 radius=14)
        skip_btn.bind(on_release=self.skip)
        back_btn = RoundedButton(text=fa("بازگشت"), font_name=FONT,
                                 font_size=dp(15), button_color=THEME["card2"],
                                 radius=14)
        back_btn.bind(on_release=self.go_back)
        row.add_widget(reset_btn)
        row.add_widget(skip_btn)
        row.add_widget(back_btn)

        main.add_widget(title)
        main.add_widget(modes_row)
        main.add_widget(subj_label)
        main.add_widget(self.subject_spinner)
        main.add_widget(timer_card)
        main.add_widget(self.start_btn)
        main.add_widget(row)
        self.add_widget(scroll)

    def on_pre_enter(self):
        try:
            app = App.get_running_app()
            no_sub = fa("بدون درس")
            values = [no_sub] + [fa(s["name"]) for s in app.db.subjects()]
            self.subject_spinner.values = values
            if self.subject_spinner.text not in values:
                self.subject_spinner.text = no_sub
            if not self._restored:
                self._restore()
            self.update_cycle_lbl()
        except Exception:
            pass

    def on_leave(self):
        """تایمر رو متوقف می‌کنه تا موقع رفتن به صفحه‌ی دیگه تیک نزنه."""
        if self.running:
            self.pause()

    def _restore(self):
        self._restored = True
        try:
            app = App.get_running_app()
            saved = app.db.get_setting("active_timer")
            if not saved:
                return
            self.mode = saved.get("mode", "work")
            self.cycle = int(saved.get("cycle", 0))
            self.duration = int(saved.get("duration", self.duration))
            self.remaining = int(saved.get("remaining", self.duration))
            self.elapsed = int(saved.get("elapsed", 0))
            self.selected_subject = saved.get("subject")
            if self.selected_subject:
                for s in app.db.subjects():
                    if s["name"] == self.selected_subject:
                        self.subject_spinner.text = fa(s["name"])
                        break
            app.db.set_setting("active_timer", None)
            self._update_display()
        except Exception:
            pass

    def update_cycle_lbl(self):
        self.cycle_lbl.text = fa(f"دور {self.cycle + 1} از {POMODORO_CYCLES}")

    def set_mode(self, mode):
        if self.running:
            return
        self.mode = mode
        for k, b in self.mode_btns.items():
            if k == mode:
                col = {"work": THEME["primary"],
                       "short": THEME["success"],
                       "long": THEME["secondary"]}[k]
                b.set_color(col)
            else:
                b.set_color(THEME["card2"])
        dur = {"work": POMODORO_WORK,
               "short": POMODORO_SHORT,
               "long": POMODORO_LONG}[mode]
        self.duration = dur
        self.remaining = dur
        self.elapsed = 0
        self._update_display()
        self.status.text = fa({"work": "آماده تمرکز",
                                "short": "آماده استراحت",
                                "long": "آماده استراحت بلند"}[mode])

    def _update_display(self):
        self.timer_label.text = fmt_clock(self.remaining)

    def toggle(self, *a):
        if self.running:
            self.pause()
        else:
            self.start()

    def start(self, *a):
        if self.remaining <= 0:
            self.remaining = self.duration
        try:
            app = App.get_running_app()
        except Exception:
            return
        subj_text = self.subject_spinner.text
        no_sub = fa("بدون درس")
        if subj_text == no_sub:
            self.selected_subject = "بدون درس"
        else:
            self.selected_subject = "بدون درس"
            for s in app.db.subjects():
                if fa(s["name"]) == subj_text:
                    self.selected_subject = s["name"]
                    break
        self.running = True
        if self.event is None:
            self.event = Clock.schedule_interval(self.tick, 1)
        self.start_btn.text = fa("توقف")
        self.start_btn.set_color(THEME["danger"])
        if self.mode == "work":
            self.status.text = fa(f"در حال تمرکز: {self.selected_subject or ''}")
            self.status.color = THEME["primary"]
        else:
            self.status.text = fa("در حال استراحت")
            self.status.color = THEME["success"]
        self.subject_spinner.disabled = True

    def pause(self):
        self.running = False
        if self.event:
            try:
                self.event.cancel()
            except Exception:
                pass
            self.event = None
        self.start_btn.text = fa("ادامه")
        self.start_btn.set_color(THEME["primary"])
        self.status.text = fa("متوقف شد")
        self.status.color = THEME["muted"]
        self.subject_spinner.disabled = False

    def tick(self, dt):
        if not self.running:
            return
        if self.remaining > 0:
            self.remaining -= 1
            if self.mode == "work":
                self.elapsed += 1
            self._update_display()
        if self.remaining == 0:
            self.finish()

    def finish(self):
        self.running = False
        if self.event:
            try:
                self.event.cancel()
            except Exception:
                pass
            self.event = None
        self.timer_label.text = "00:00"
        try:
            app = App.get_running_app()
        except Exception:
            return
        if app.db.get_setting("sound", True):
            app.play_beep()
            app.notify(fa("پایان " + ("تمرکز" if self.mode == "work" else "استراحت")),
                       fa("یک جلسه تمام شد!"))
        if self.mode == "work":
            self._record_work()
            self.cycle += 1
            self.update_cycle_lbl()
            nxt = "long" if self.cycle % POMODORO_CYCLES == 0 else "short"
            self.show_end_popup(nxt)
        else:
            self.show_rest_done()
        self.start_btn.text = fa("شروع")
        self.start_btn.set_color(THEME["primary"])
        self.subject_spinner.disabled = False

    def _record_work(self):
        try:
            app = App.get_running_app()
            if self.elapsed > 0:
                app.db.add_session(self.selected_subject or "بدون درس",
                                   self.elapsed, "", 0)
                Clock.schedule_once(lambda dt: app.check_achievements(), 0.8)
        except Exception:
            pass

    def show_end_popup(self, next_mode):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(20))
        content.add_widget(Label(text=fa("🎉 جلسه تمرکز تمام شد!"), font_name=FONT,
                                 font_size=dp(20), bold=True, color=THEME["success"],
                                 size_hint_y=None, height=dp(36)))
        content.add_widget(Label(text=fa(f"زمان: {fmt_long(self.elapsed)}"),
                                 font_name=FONT, font_size=dp(15),
                                 color=THEME["text"], size_hint_y=None, height=dp(28)))
        content.add_widget(Label(text=fa(f"🌟 {self.elapsed // 60} XP"),
                                 font_name=FONT, font_size=dp(16), bold=True,
                                 color=THEME["warning"], size_hint_y=None, height=dp(28)))
        note_lbl = Label(text=fa("یادداشت (اختیاری)"), font_name=FONT,
                         font_size=dp(13), color=THEME["muted"], halign="right",
                         size_hint_y=None, height=dp(22))
        note_lbl.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        note_input = TextInput(hint_text=fa("چی خوندی؟"), font_name=FONT,
                               font_size=dp(14), multiline=False, halign="right",
                               padding=[dp(10), dp(16), dp(10), dp(16)],
                               size_hint_y=None, height=dp(48),
                               background_color=THEME["card2"],
                               foreground_color=THEME["text"],
                               cursor_color=THEME["primary"],
                               hint_text_color=THEME["muted"])
        content.add_widget(note_lbl)
        content.add_widget(note_input)
        row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(54))
        start_rest = RoundedButton(text=fa("شروع استراحت"), font_name=FONT,
                                   font_size=dp(15), bold=True,
                                   button_color=THEME["success"])
        later = RoundedButton(text=fa("بعداً"), font_name=FONT, font_size=dp(15),
                              button_color=THEME["card2"])
        row.add_widget(start_rest)
        row.add_widget(later)
        content.add_widget(row)
        popup = Popup(title=fa("پایان تمرکز"), title_font=FONT, title_size=dp(15),
                      title_color=THEME["text"], content=content,
                      size_hint=(0.9, 0.75), background_color=THEME["card"],
                      background="", separator_color=THEME["primary"],
                      auto_dismiss=False)

        def do_start_rest(*a):
            try:
                app = App.get_running_app()
                if note_input.text.strip():
                    app.db.add_session(self.selected_subject or "بدون درس",
                                       0, note_input.text.strip(), 0)
            except Exception:
                pass
            popup.dismiss()
            self.set_mode(next_mode)
            Clock.schedule_once(lambda dt: self.start(), 0.3)

        def do_later(*a):
            popup.dismiss()
            self.set_mode(next_mode)

        start_rest.bind(on_release=do_start_rest)
        later.bind(on_release=do_later)
        popup.open()
        self.elapsed = 0

    def show_rest_done(self):
        content = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(20))
        content.add_widget(Label(text=fa("✨ استراحت تمام شد"), font_name=FONT,
                                 font_size=dp(20), bold=True,
                                 color=THEME["secondary"],
                                 size_hint_y=None, height=dp(40)))
        content.add_widget(Label(text=fa("آماده‌ای برای دور بعدی؟"), font_name=FONT,
                                 font_size=dp(15), color=THEME["text"],
                                 size_hint_y=None, height=dp(30)))
        ok = RoundedButton(text=fa("شروع تمرکز"), font_name=FONT, font_size=dp(16),
                           bold=True, size_hint_y=None, height=dp(54),
                           button_color=THEME["primary"])
        content.add_widget(ok)
        popup = Popup(title=fa("استراحت"), title_font=FONT, title_size=dp(15),
                      title_color=THEME["text"], content=content,
                      size_hint=(0.85, 0.45), background_color=THEME["card"],
                      background="", separator_color=THEME["secondary"])

        def go(*a):
            popup.dismiss()
            self.set_mode("work")

        ok.bind(on_release=go)
        popup.open()
        self.set_mode("work")

    def reset(self, *a):
        self.pause()
        self.remaining = self.duration
        self.elapsed = 0
        self._update_display()
        self.status.text = fa("آماده شروع")

    def skip(self, *a):
        self.pause()
        self.remaining = 0
        self.finish()

    def go_back(self, *a):
        self.pause()
        if self.manager is not None:
            self.manager.current = "home"


class SubjectsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        title = Label(text=fa("درس‌های من"), font_name=FONT, font_size=dp(24),
                      bold=True, color=THEME["text"], halign="right",
                      size_hint_y=None, height=dp(44))
        title.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        add_btn = RoundedButton(text=fa("+ افزودن درس جدید"), font_name=FONT,
                                font_size=dp(15), bold=True,
                                size_hint_y=None, height=dp(54),
                                button_color=THEME["primary"])
        add_btn.bind(on_release=self.add)
        scroll = ScrollView()
        self.list_box = BoxLayout(orientation="vertical", spacing=dp(10),
                                  size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        back = RoundedButton(text=fa("بازگشت"), font_name=FONT, font_size=dp(15),
                             size_hint_y=None, height=dp(50),
                             button_color=THEME["card2"])
        back.bind(on_release=lambda *a: self._go_home())
        main.add_widget(title)
        main.add_widget(add_btn)
        main.add_widget(scroll)
        main.add_widget(back)
        self.add_widget(main)

    def _go_home(self):
        if self.manager is not None:
            self.manager.current = "home"

    def on_pre_enter(self):
        self.refresh()

    def refresh(self):
        self.list_box.clear_widgets()
        try:
            app = App.get_running_app()
            subs = app.db.subjects()
        except Exception:
            return
        if not subs:
            c = Card(orientation="vertical", padding=dp(20), spacing=dp(6),
                     size_hint_y=None, height=dp(110))
            c.add_widget(Label(text=fa("هنوز درسی اضافه نکرده‌ای"), font_name=FONT,
                               font_size=dp(15), color=THEME["text"]))
            c.add_widget(Label(text=fa("از دکمه بالا شروع کن ✨"), font_name=FONT,
                               font_size=dp(13), color=THEME["muted"]))
            self.list_box.add_widget(c)
            return
        stats = {x["subject"]: x for x in app.db.subject_stats()}
        for s in subs:
            self._row(s, stats.get(s["name"]))

    def _row(self, s, info):
        c = Card(orientation="horizontal", padding=dp(14), spacing=dp(10),
                 size_hint_y=None, height=dp(66))
        dot = Widget(size_hint_x=None, width=dp(12))
        with dot.canvas:
            Color(*THEME["primary"])
            dot._r = RoundedRectangle(pos=dot.pos, size=dot.size, radius=r4(6))
        dot.bind(pos=lambda *a: setattr(dot._r, "pos", dot.pos),
                 size=lambda *a: setattr(dot._r, "size", dot.size))
        lbl = Label(text=fa(s["name"]), font_name=FONT, font_size=dp(16),
                    bold=True, color=THEME["text"], halign="right")
        lbl.bind(size=lambda l, sv: setattr(l, "text_size", (sv[0], None)))
        info_lbl = Label(text=fa(fmt_min(info["s"]) if info else "—"),
                         font_name=FONT, font_size=dp(12), color=THEME["muted"],
                         size_hint_x=None, width=dp(70))
        del_btn = RoundedButton(text=fa("حذف"), font_name=FONT, font_size=dp(13),
                                size_hint_x=None, width=dp(60),
                                button_color=THEME["danger"], radius=12)
        del_btn.bind(on_release=lambda *a: self.delete(s["name"]))
        c.add_widget(dot)
        c.add_widget(lbl)
        c.add_widget(info_lbl)
        c.add_widget(del_btn)
        self.list_box.add_widget(c)

    def add(self, *a):
        box = Card(orientation="horizontal", padding=dp(10), spacing=dp(8),
                   size_hint_y=None, height=dp(70))
        ti = TextInput(hint_text=fa("نام درس"), font_name=FONT, font_size=dp(15),
                       multiline=False, halign="right", size_hint_x=0.68,
                       padding=[dp(12), dp(18), dp(12), dp(18)],
                       background_color=THEME["card2"],
                       foreground_color=THEME["text"],
                       cursor_color=THEME["primary"],
                       hint_text_color=THEME["muted"])
        save = RoundedButton(text=fa("ذخیره"), font_name=FONT, font_size=dp(14),
                             size_hint_x=0.32, button_color=THEME["success"],
                             radius=14)
        box.add_widget(ti)
        box.add_widget(save)
        self.list_box.add_widget(box, index=0)
        save.bind(on_release=lambda *a: self.save(ti))
        ti.focus = True

    def save(self, ti):
        name = ti.text.strip()
        if name:
            try:
                App.get_running_app().db.add_subject(name)
            except Exception:
                pass
            self.refresh()

    def delete(self, name):
        try:
            App.get_running_app().db.delete_subject(name)
        except Exception:
            pass
        self.refresh()


class FlashcardsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        title = Label(text=fa("فلش‌کارت‌ها"), font_name=FONT, font_size=dp(24),
                      bold=True, color=THEME["text"], halign="right",
                      size_hint_y=None, height=dp(44))
        title.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        row = BoxLayout(orientation="horizontal", spacing=dp(8),
                        size_hint_y=None, height=dp(52))
        self.subj_filter = Spinner(text=fa("همه دروس"), values=[fa("همه دروس")],
                                   font_name=FONT, font_size=dp(14),
                                   background_normal="",
                                   background_color=THEME["secondary"],
                                   color=THEME["on_prim"])
        self.subj_filter.bind(text=lambda *a: self.refresh())
        study_btn = RoundedButton(text=fa("▶ شروع مرور"), font_name=FONT,
                                  font_size=dp(14), bold=True,
                                  button_color=THEME["primary"], radius=14)
        study_btn.bind(on_release=self.study)
        row.add_widget(self.subj_filter)
        row.add_widget(study_btn)
        add_btn = RoundedButton(text=fa("+ فلش‌کارت جدید"), font_name=FONT,
                                font_size=dp(15), bold=True,
                                size_hint_y=None, height=dp(52),
                                button_color=THEME["accent"])
        add_btn.bind(on_release=self.add)
        scroll = ScrollView()
        self.list_box = BoxLayout(orientation="vertical", spacing=dp(8),
                                  size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        back = RoundedButton(text=fa("بازگشت"), font_name=FONT, font_size=dp(15),
                             size_hint_y=None, height=dp(50),
                             button_color=THEME["card2"])
        back.bind(on_release=lambda *a: self._go_home())
        main.add_widget(title)
        main.add_widget(row)
        main.add_widget(add_btn)
        main.add_widget(scroll)
        main.add_widget(back)
        self.add_widget(main)

    def _go_home(self):
        if self.manager is not None:
            self.manager.current = "home"

    def on_pre_enter(self):
        try:
            app = App.get_running_app()
            vals = [fa("همه دروس")] + [fa(s["name"]) for s in app.db.subjects()]
            self.subj_filter.values = vals
            if self.subj_filter.text not in vals:
                self.subj_filter.text = fa("همه دروس")
            self.refresh()
        except Exception:
            pass

    def _selected_subject(self):
        t = self.subj_filter.text
        if t == fa("همه دروس"):
            return None
        try:
            for s in App.get_running_app().db.subjects():
                if fa(s["name"]) == t:
                    return s["name"]
        except Exception:
            pass
        return None

    def refresh(self):
        self.list_box.clear_widgets()
        try:
            cards = App.get_running_app().db.flashcards(self._selected_subject())
        except Exception:
            return
        if not cards:
            c = Card(orientation="vertical", padding=dp(20), spacing=dp(6),
                     size_hint_y=None, height=dp(100))
            c.add_widget(Label(text=fa("فلش‌کارتی نداری"), font_name=FONT,
                               font_size=dp(14), color=THEME["text"]))
            c.add_widget(Label(text=fa("یه کارت جدید بساز ✨"), font_name=FONT,
                               font_size=dp(12), color=THEME["muted"]))
            self.list_box.add_widget(c)
            return
        for fc in cards:
            c = Card(orientation="vertical", padding=dp(12), spacing=dp(4),
                     size_hint_y=None, height=dp(84))
            top = BoxLayout(size_hint_y=None, height=dp(26))
            front = Label(text=fa(fc["front"][:40]), font_name=FONT,
                          font_size=dp(15), bold=True, color=THEME["text"],
                          halign="right")
            front.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
            del_btn = RoundedButton(text="✕", font_name=FONT, font_size=dp(12),
                                    size_hint_x=None, width=dp(34),
                                    button_color=THEME["danger"], radius=10)
            del_btn.bind(on_release=lambda *a, i=fc["id"]: self.delete(i))
            top.add_widget(front)
            top.add_widget(del_btn)
            back_lbl = Label(text=fa(fc["back"][:60]), font_name=FONT,
                             font_size=dp(13), color=THEME["muted"], halign="right")
            back_lbl.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
            subj_lbl = Label(text=fa(fc["subject"] or "—"), font_name=FONT,
                             font_size=dp(11), color=THEME["primary"],
                             halign="right", size_hint_y=None, height=dp(18))
            subj_lbl.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
            c.add_widget(top)
            c.add_widget(back_lbl)
            c.add_widget(subj_lbl)
            self.list_box.add_widget(c)

    def add(self, *a):
        try:
            app = App.get_running_app()
            subs = app.db.subjects()
        except Exception:
            return
        if not subs:
            try:
                App.get_running_app().toast("اول یه درس بساز")
            except Exception:
                pass
            return
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(16))
        content.add_widget(Label(text=fa("درس"), font_name=FONT, font_size=dp(13),
                                 color=THEME["muted"], halign="right",
                                 size_hint_y=None, height=dp(22)))
        subj_sp = Spinner(text=fa(subs[0]["name"]),
                          values=[fa(s["name"]) for s in subs],
                          font_name=FONT, font_size=dp(14),
                          size_hint_y=None, height=dp(48),
                          background_normal="",
                          background_color=THEME["secondary"],
                          color=THEME["on_prim"])
        content.add_widget(subj_sp)
        content.add_widget(Label(text=fa("روی کارت (سوال)"), font_name=FONT,
                                 font_size=dp(13), color=THEME["muted"],
                                 halign="right", size_hint_y=None, height=dp(22)))
        front = TextInput(font_name=FONT, font_size=dp(15), multiline=True,
                          halign="right", size_hint_y=None, height=dp(80),
                          padding=[dp(10), dp(10), dp(10), dp(10)],
                          background_color=THEME["card2"],
                          foreground_color=THEME["text"],
                          cursor_color=THEME["primary"])
        content.add_widget(front)
        content.add_widget(Label(text=fa("پشت کارت (پاسخ)"), font_name=FONT,
                                 font_size=dp(13), color=THEME["muted"],
                                 halign="right", size_hint_y=None, height=dp(22)))
        back = TextInput(font_name=FONT, font_size=dp(15), multiline=True,
                         halign="right", size_hint_y=None, height=dp(80),
                         padding=[dp(10), dp(10), dp(10), dp(10)],
                         background_color=THEME["card2"],
                         foreground_color=THEME["text"],
                         cursor_color=THEME["primary"])
        content.add_widget(back)
        save = RoundedButton(text=fa("ذخیره"), font_name=FONT, font_size=dp(15),
                             bold=True, size_hint_y=None, height=dp(52),
                             button_color=THEME["success"])
        content.add_widget(save)
        popup = Popup(title=fa("فلش‌کارت جدید"), title_font=FONT,
                      title_size=dp(15), title_color=THEME["text"],
                      content=content, size_hint=(0.9, 0.9),
                      background_color=THEME["card"], background="",
                      separator_color=THEME["primary"])

        def do_save(*a):
            f = front.text.strip()
            b = back.text.strip()
            if not f or not b:
                return
            subj_name = subs[0]["name"]
            for s in subs:
                if fa(s["name"]) == subj_sp.text:
                    subj_name = s["name"]
                    break
            try:
                app.db.add_flashcard(subj_name, f, b)
                app.check_achievements()
            except Exception:
                pass
            popup.dismiss()
            self.refresh()

        save.bind(on_release=do_save)
        popup.open()

    def delete(self, fc_id):
        try:
            App.get_running_app().db.delete_flashcard(fc_id)
        except Exception:
            pass
        self.refresh()

    def study(self, *a):
        try:
            app = App.get_running_app()
            due = app.db.due_flashcards(self._selected_subject())
        except Exception:
            return
        if not due:
            try:
                app.toast("چیزی برای مرور نیست ✨")
            except Exception:
                pass
            return
        if self.manager is None:
            return
        try:
            screen = self.manager.get_screen("fc_study")
            screen.set_deck(due)
            self.manager.current = "fc_study"
        except Exception:
            pass


class FlashcardStudyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.deck = []
        self.idx = 0
        self.flipped = False
        main = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36))
        self.progress_lbl = Label(text="", font_name=FONT, font_size=dp(14),
                                  color=THEME["muted"], halign="right")
        self.progress_lbl.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        close_btn = RoundedButton(text=fa("بستن"), font_name=FONT, font_size=dp(12),
                                  size_hint_x=None, width=dp(60),
                                  button_color=THEME["card2"], radius=12)
        close_btn.bind(on_release=lambda *a: self._close())
        top.add_widget(self.progress_lbl)
        top.add_widget(close_btn)
        self.card = Card(orientation="vertical", padding=dp(20), spacing=dp(10))
        self.front_lbl = Label(text="", font_name=FONT, font_size=dp(20),
                               color=THEME["text"], halign="center", valign="middle")
        self.front_lbl.bind(size=lambda l, s: setattr(l, "text_size", s))
        self.card.add_widget(self.front_lbl)
        self.flip_btn = RoundedButton(text=fa("نمایش پاسخ"), font_name=FONT,
                                      font_size=dp(16), bold=True,
                                      size_hint_y=None, height=dp(56),
                                      button_color=THEME["primary"], radius=18)
        self.flip_btn.bind(on_release=self.flip)
        self.rating_box = BoxLayout(orientation="horizontal", spacing=dp(6),
                                    size_hint_y=None, height=dp(56))
        for label, color, q in [("دوباره", THEME["danger"], 0),
                                 ("سخت", THEME["warning"], 3),
                                 ("خوب", THEME["primary"], 4),
                                 ("آسان", THEME["success"], 5)]:
            b = RoundedButton(text=fa(label), font_name=FONT, font_size=dp(13),
                              button_color=color, radius=14)
            b.bind(on_release=lambda *a, quality=q: self.rate(quality))
            self.rating_box.add_widget(b)
        self.rating_box.opacity = 0
        self.rating_box.disabled = True
        main.add_widget(top)
        main.add_widget(self.card)
        main.add_widget(self.flip_btn)
        main.add_widget(self.rating_box)
        self.add_widget(main)

    def _close(self):
        if self.manager is not None:
            self.manager.current = "flashcards"

    def set_deck(self, deck):
        self.deck = list(deck)
        self.idx = 0
        self.flipped = False
        self.show()

    def show(self):
        if self.idx >= len(self.deck):
            self.finish()
            return
        card = self.deck[self.idx]
        self.front_lbl.text = fa(card["front"])
        self.flipped = False
        self.flip_btn.text = fa("نمایش پاسخ")
        self.flip_btn.set_color(THEME["primary"])
        self.rating_box.opacity = 0
        self.rating_box.disabled = True
        self.progress_lbl.text = fa(f"{self.idx + 1} / {len(self.deck)}")

    def flip(self, *a):
        if self.flipped:
            return
        self.front_lbl.text = fa(self.deck[self.idx]["back"])
        self.flipped = True
        self.flip_btn.text = fa("✓ چقدر راحت بود؟")
        self.flip_btn.set_color(THEME["card2"])
        self.rating_box.opacity = 1
        self.rating_box.disabled = False

    def rate(self, quality):
        if self.idx >= len(self.deck):
            return
        try:
            db = App.get_running_app().db
        except Exception:
            self.idx += 1
            self.show()
            return

        # ✅ از DB می‌خونیم تا داده‌ی کهنه استفاده نشه
        fc_id = self.deck[self.idx]["id"]
        fresh = db.get_flashcard(fc_id)
        card = fresh if fresh else self.deck[self.idx]

        ease = float(card.get("ease") or 2.5)
        reps = int(card.get("repetitions") or 0)
        interval = int(card.get("interval") or 0)

        if quality < 3:
            reps = 0
            interval = 1
        else:
            if reps == 0:
                interval = 1
            elif reps == 1:
                interval = 6
            else:
                interval = int(round(interval * ease))
            reps += 1

        ease = ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if ease < 1.3:
            ease = 1.3

        nxt = (date.today() + timedelta(days=interval)).isoformat()
        try:
            db.update_flashcard(fc_id, ease, interval, reps, nxt)
        except Exception:
            pass
        self.idx += 1
        self.show()

    def finish(self):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(20))
        content.add_widget(Label(text="🎉", font_name=FONT, font_size=dp(50),
                                 size_hint_y=None, height=dp(60)))
        content.add_widget(Label(text=fa("مرور تمام شد!"), font_name=FONT,
                                 font_size=dp(18), bold=True,
                                 color=THEME["success"],
                                 size_hint_y=None, height=dp(30)))
        ok = RoundedButton(text=fa("بازگشت"), font_name=FONT, font_size=dp(15),
                           size_hint_y=None, height=dp(52),
                           button_color=THEME["primary"])
        content.add_widget(ok)
        popup = Popup(title="", title_size=0, content=content,
                      size_hint=(0.8, 0.45), background_color=THEME["card"],
                      background="", separator_color=THEME["success"])

        def go(*a):
            popup.dismiss()
            self._close()

        ok.bind(on_release=go)
        popup.open()


class TasksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        title = Label(text=fa("وظایف من"), font_name=FONT, font_size=dp(24),
                      bold=True, color=THEME["text"], halign="right",
                      size_hint_y=None, height=dp(44))
        title.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        add_btn = RoundedButton(text=fa("+ وظیفه جدید"), font_name=FONT,
                                font_size=dp(15), bold=True,
                                size_hint_y=None, height=dp(52),
                                button_color=THEME["success"])
        add_btn.bind(on_release=self.add)
        scroll = ScrollView()
        self.list_box = BoxLayout(orientation="vertical", spacing=dp(8),
                                  size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        back = RoundedButton(text=fa("بازگشت"), font_name=FONT, font_size=dp(15),
                             size_hint_y=None, height=dp(50),
                             button_color=THEME["card2"])
        back.bind(on_release=lambda *a: self._go_home())
        main.add_widget(title)
        main.add_widget(add_btn)
        main.add_widget(scroll)
        main.add_widget(back)
        self.add_widget(main)

    def _go_home(self):
        if self.manager is not None:
            self.manager.current = "home"

    def on_pre_enter(self):
        self.refresh()

    def refresh(self):
        self.list_box.clear_widgets()
        try:
            tasks = App.get_running_app().db.tasks()
        except Exception:
            return
        if not tasks:
            c = Card(orientation="vertical", padding=dp(20), spacing=dp(6),
                     size_hint_y=None, height=dp(100))
            c.add_widget(Label(text=fa("وظیفه‌ای نداری"), font_name=FONT,
                               font_size=dp(14), color=THEME["text"]))
            c.add_widget(Label(text=fa("یه وظیفه جدید بساز ✨"), font_name=FONT,
                               font_size=dp(12), color=THEME["muted"]))
            self.list_box.add_widget(c)
            return
        for t in tasks:
            self._row(t)

    def _row(self, t):
        is_done = bool(t["done"])
        c = Card(orientation="horizontal", padding=dp(12), spacing=dp(8),
                 size_hint_y=None, height=dp(64))
        chk = RoundedButton(text="✓" if is_done else "○", font_name=FONT,
                            font_size=dp(16), size_hint_x=None, width=dp(44),
                            button_color=(THEME["success"] if is_done
                                          else THEME["card2"]), radius=12)
        chk.bind(on_release=lambda *a: self.toggle(t))
        title = Label(text=fa(t["title"]), font_name=FONT, font_size=dp(15),
                      bold=not is_done,
                      color=THEME["muted"] if is_done else THEME["text"],
                      halign="right")
        title.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        del_btn = RoundedButton(text="✕", font_name=FONT, font_size=dp(12),
                                size_hint_x=None, width=dp(36),
                                button_color=THEME["danger"], radius=10)
        del_btn.bind(on_release=lambda *a: self.delete(t["id"]))
        c.add_widget(chk)
        c.add_widget(title)
        c.add_widget(del_btn)
        self.list_box.add_widget(c)

    def add(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(16))
        content.add_widget(Label(text=fa("عنوان وظیفه"), font_name=FONT,
                                 font_size=dp(13), color=THEME["muted"],
                                 halign="right", size_hint_y=None, height=dp(22)))
        ti = TextInput(hint_text=fa("چیکار باید بکنم؟"), font_name=FONT,
                       font_size=dp(15), multiline=False, halign="right",
                       size_hint_y=None, height=dp(50),
                       padding=[dp(10), dp(16), dp(10), dp(16)],
                       background_color=THEME["card2"],
                       foreground_color=THEME["text"],
                       cursor_color=THEME["primary"])
        content.add_widget(ti)
        save = RoundedButton(text=fa("ذخیره"), font_name=FONT, font_size=dp(15),
                             size_hint_y=None, height=dp(50),
                             button_color=THEME["success"])
        content.add_widget(save)
        popup = Popup(title=fa("وظیفه جدید"), title_font=FONT, title_size=dp(15),
                      title_color=THEME["text"], content=content,
                      size_hint=(0.9, 0.55), background_color=THEME["card"],
                      background="", separator_color=THEME["success"])

        def do_save(*a):
            title = ti.text.strip()
            if title:
                try:
                    App.get_running_app().db.add_task(title)
                except Exception:
                    pass
                popup.dismiss()
                self.refresh()

        save.bind(on_release=do_save)
        popup.open()

    def toggle(self, t):
        try:
            app = App.get_running_app()
            app.db.toggle_task(t["id"], not t["done"])
            app.check_achievements()
        except Exception:
            pass
        self.refresh()

    def delete(self, tid):
        try:
            App.get_running_app().db.delete_task(tid)
        except Exception:
            pass
        self.refresh()


class NotesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        title = Label(text=fa("یادداشت‌ها"), font_name=FONT, font_size=dp(24),
                      bold=True, color=THEME["text"], halign="right",
                      size_hint_y=None, height=dp(44))
        title.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        add_btn = RoundedButton(text=fa("+ یادداشت جدید"), font_name=FONT,
                                font_size=dp(15), bold=True,
                                size_hint_y=None, height=dp(52),
                                button_color=THEME["warning"])
        add_btn.bind(on_release=self.add)
        scroll = ScrollView()
        self.list_box = BoxLayout(orientation="vertical", spacing=dp(8),
                                  size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        back = RoundedButton(text=fa("بازگشت"), font_name=FONT, font_size=dp(15),
                             size_hint_y=None, height=dp(50),
                             button_color=THEME["card2"])
        back.bind(on_release=lambda *a: self._go_home())
        main.add_widget(title)
        main.add_widget(add_btn)
        main.add_widget(scroll)
        main.add_widget(back)
        self.add_widget(main)

    def _go_home(self):
        if self.manager is not None:
            self.manager.current = "home"

    def on_pre_enter(self):
        self.refresh()

    def refresh(self):
        self.list_box.clear_widgets()
        try:
            notes = App.get_running_app().db.notes()
        except Exception:
            return
        if not notes:
            c = Card(orientation="vertical", padding=dp(20), spacing=dp(6),
                     size_hint_y=None, height=dp(100))
            c.add_widget(Label(text=fa("یادداشتی نداری"), font_name=FONT,
                               font_size=dp(14), color=THEME["text"]))
            c.add_widget(Label(text=fa("شروع کن به نوشتن ✍️"), font_name=FONT,
                               font_size=dp(12), color=THEME["muted"]))
            self.list_box.add_widget(c)
            return
        for n in notes:
            c = Card(orientation="vertical", padding=dp(12), spacing=dp(4),
                     size_hint_y=None, height=dp(90))
            top = BoxLayout(size_hint_y=None, height=dp(26))
            t = Label(text=fa(n["title"] or "بدون عنوان"), font_name=FONT,
                      font_size=dp(15), bold=True, color=THEME["text"],
                      halign="right")
            t.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
            del_btn = RoundedButton(text="✕", font_name=FONT, font_size=dp(12),
                                    size_hint_x=None, width=dp(34),
                                    button_color=THEME["danger"], radius=10)
            del_btn.bind(on_release=lambda *a, i=n["id"]: self.delete(i))
            top.add_widget(t)
            top.add_widget(del_btn)
            body = Label(text=fa((n["body"] or "")[:80]), font_name=FONT,
                         font_size=dp(12), color=THEME["muted"], halign="right")
            body.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
            c.add_widget(top)
            c.add_widget(body)
            self.list_box.add_widget(c)

    def add(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(16))
        content.add_widget(Label(text=fa("عنوان"), font_name=FONT,
                                 font_size=dp(13), color=THEME["muted"],
                                 halign="right", size_hint_y=None, height=dp(22)))
        t = TextInput(font_name=FONT, font_size=dp(15), multiline=False,
                      halign="right", size_hint_y=None, height=dp(46),
                      padding=[dp(10), dp(14), dp(10), dp(14)],
                      background_color=THEME["card2"],
                      foreground_color=THEME["text"],
                      cursor_color=THEME["primary"])
        content.add_widget(t)
        content.add_widget(Label(text=fa("متن"), font_name=FONT,
                                 font_size=dp(13), color=THEME["muted"],
                                 halign="right", size_hint_y=None, height=dp(22)))
        b = TextInput(font_name=FONT, font_size=dp(14), multiline=True,
                      halign="right", padding=[dp(10), dp(10), dp(10), dp(10)],
                      background_color=THEME["card2"],
                      foreground_color=THEME["text"],
                      cursor_color=THEME["primary"])
        content.add_widget(b)
        save = RoundedButton(text=fa("ذخیره"), font_name=FONT, font_size=dp(15),
                             size_hint_y=None, height=dp(50),
                             button_color=THEME["success"])
        content.add_widget(save)
        popup = Popup(title=fa("یادداشت جدید"), title_font=FONT,
                      title_size=dp(15), title_color=THEME["text"],
                      content=content, size_hint=(0.9, 0.9),
                      background_color=THEME["card"], background="",
                      separator_color=THEME["warning"])

        def do_save(*a):
            if t.text.strip() or b.text.strip():
                try:
                    app = App.get_running_app()
                    app.db.add_note(t.text.strip(), b.text.strip())
                    app.check_achievements()
                except Exception:
                    pass
                popup.dismiss()
                self.refresh()

        save.bind(on_release=do_save)
        popup.open()

    def delete(self, nid):
        try:
            App.get_running_app().db.delete_note(nid)
        except Exception:
            pass
        self.refresh()


class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView()
        main = BoxLayout(orientation="vertical", padding=dp(18),
                         spacing=dp(12), size_hint_y=None)
        main.bind(minimum_height=main.setter("height"))
        scroll.add_widget(main)
        title = Label(text=fa("آمار و تحلیل"), font_name=FONT, font_size=dp(24),
                      bold=True, color=THEME["text"], halign="right",
                      size_hint_y=None, height=dp(44))
        title.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        week_card = Card(orientation="vertical", padding=dp(14), spacing=dp(6),
                         size_hint_y=None, height=dp(190))
        w_lbl = Label(text=fa("۷ روز اخیر"), font_name=FONT, font_size=dp(14),
                      bold=True, color=THEME["text"], halign="right",
                      size_hint_y=None, height=dp(24))
        w_lbl.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        self.week_chart = BarChart(get_value=lambda d: 0)
        week_card.add_widget(w_lbl)
        week_card.add_widget(self.week_chart)
        month_card = Card(orientation="vertical", padding=dp(14), spacing=dp(6),
                          size_hint_y=None, height=dp(190))
        m_lbl = Label(text=fa("۳۰ روز اخیر"), font_name=FONT, font_size=dp(14),
                      bold=True, color=THEME["text"], halign="right",
                      size_hint_y=None, height=dp(24))
        m_lbl.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        self.month_chart = BarChart(get_value=lambda d: 0, days=30)
        month_card.add_widget(m_lbl)
        month_card.add_widget(self.month_chart)
        heat_card = Card(orientation="vertical", padding=dp(14), spacing=dp(6),
                         size_hint_y=None, height=dp(200))
        h_lbl = Label(text=fa("فعالیت ۱۲ هفته اخیر"), font_name=FONT,
                      font_size=dp(14), bold=True, color=THEME["text"],
                      halign="right", size_hint_y=None, height=dp(24))
        h_lbl.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        self.heatmap = Heatmap(get_value=lambda d: 0)
        heat_card.add_widget(h_lbl)
        heat_card.add_widget(self.heatmap)
        subj_title = Label(text=fa("تفکیک دروس"), font_name=FONT,
                           font_size=dp(16), bold=True, color=THEME["text"],
                           halign="right", size_hint_y=None, height=dp(34))
        subj_title.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        self.subj_list = BoxLayout(orientation="vertical", spacing=dp(8),
                                   size_hint_y=None)
        self.subj_list.bind(minimum_height=self.subj_list.setter("height"))
        back = RoundedButton(text=fa("بازگشت"), font_name=FONT, font_size=dp(15),
                             size_hint_y=None, height=dp(50),
                             button_color=THEME["card2"])
        back.bind(on_release=lambda *a: self._go_home())
        main.add_widget(title)
        main.add_widget(week_card)
        main.add_widget(month_card)
        main.add_widget(heat_card)
        main.add_widget(subj_title)
        main.add_widget(self.subj_list)
        main.add_widget(back)
        self.add_widget(scroll)

    def _go_home(self):
        if self.manager is not None:
            self.manager.current = "home"

    def on_pre_enter(self):
        self.update()

    def update(self):
        try:
            db = App.get_running_app().db
        except Exception:
            return
        self.week_chart.get_value = lambda d: db.seconds_on(d) / 60.0
        self.week_chart.redraw()
        self.month_chart.get_value = lambda d: db.seconds_on(d) / 60.0
        self.month_chart.redraw()
        self.heatmap.get_value = lambda d: db.seconds_on(d) / 60.0
        self.heatmap.redraw()
        stats = db.subject_stats()
        self.subj_list.clear_widgets()
        if not stats:
            c = Card(orientation="vertical", padding=dp(20),
                     size_hint_y=None, height=dp(80))
            c.add_widget(Label(text=fa("هنوز جلسه‌ای ثبت نشده"), font_name=FONT,
                               font_size=dp(14), color=THEME["muted"]))
            self.subj_list.add_widget(c)
            return
        for s in stats:
            c = Card(orientation="vertical", padding=dp(12), spacing=dp(4),
                     size_hint_y=None, height=dp(76))
            top = BoxLayout(size_hint_y=None, height=dp(26))
            n = Label(text=fa(s["subject"]), font_name=FONT, font_size=dp(15),
                      bold=True, color=THEME["text"], halign="right")
            n.bind(size=lambda l, sv: setattr(l, "text_size", (sv[0], None)))
            cnt = Label(text=fa(f"{s['n']} جلسه"), font_name=FONT,
                        font_size=dp(11), color=THEME["primary"], halign="left")
            cnt.bind(size=lambda l, sv: setattr(l, "text_size", (sv[0], None)))
            top.add_widget(n)
            top.add_widget(cnt)
            detail = Label(text=fa(fmt_long(s["s"])), font_name=FONT,
                           font_size=dp(12), color=THEME["muted"], halign="right")
            detail.bind(size=lambda l, sv: setattr(l, "text_size", (sv[0], None)))
            c.add_widget(top)
            c.add_widget(detail)
            self.subj_list.add_widget(c)


class AchievementsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        title = Label(text=fa("🏆 نشان‌های من"), font_name=FONT,
                      font_size=dp(24), bold=True, color=THEME["text"],
                      halign="right", size_hint_y=None, height=dp(44))
        title.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        self.counter = Label(text="", font_name=FONT, font_size=dp(14),
                             color=THEME["muted"], halign="right",
                             size_hint_y=None, height=dp(24))
        self.counter.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        scroll = ScrollView()
        self.grid = BoxLayout(orientation="vertical", spacing=dp(8),
                              size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll.add_widget(self.grid)
        back = RoundedButton(text=fa("بازگشت"), font_name=FONT, font_size=dp(15),
                             size_hint_y=None, height=dp(50),
                             button_color=THEME["card2"])
        back.bind(on_release=lambda *a: self._go_home())
        main.add_widget(title)
        main.add_widget(self.counter)
        main.add_widget(scroll)
        main.add_widget(back)
        self.add_widget(main)

    def _go_home(self):
        if self.manager is not None:
            self.manager.current = "home"

    def on_pre_enter(self):
        self.refresh()

    def refresh(self):
        self.grid.clear_widgets()
        try:
            earned = App.get_running_app().db.earned_achievements()
        except Exception:
            earned = set()
        self.counter.text = fa(f"{len(earned)} از {len(ACHIEVEMENTS)} نشان")
        for key, icon, title, desc in ACHIEVEMENTS:
            is_e = key in earned
            c = Card(orientation="horizontal", padding=dp(12), spacing=dp(10),
                     size_hint_y=None, height=dp(76),
                     bg_color=THEME["card"] if is_e else THEME["card2"],
                     border_color=THEME["warning"] if is_e else THEME["border"])
            ico = Label(text=icon, font_name=FONT, font_size=dp(32),
                        size_hint_x=None, width=dp(54),
                        color=THEME["warning"] if is_e else THEME["muted"])
            tb = BoxLayout(orientation="vertical", spacing=dp(2))
            t = Label(text=fa(title), font_name=FONT, font_size=dp(15),
                      bold=True, halign="right",
                      color=THEME["text"] if is_e else THEME["muted"])
            t.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
            d = Label(text=fa(desc), font_name=FONT, font_size=dp(12),
                      color=THEME["muted"], halign="right")
            d.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
            tb.add_widget(t)
            tb.add_widget(d)
            c.add_widget(tb)
            c.add_widget(ico)
            self.grid.add_widget(c)


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView()
        main = BoxLayout(orientation="vertical", padding=dp(18),
                         spacing=dp(10), size_hint_y=None)
        main.bind(minimum_height=main.setter("height"))
        scroll.add_widget(main)
        title = Label(text=fa("تنظیمات"), font_name=FONT, font_size=dp(24),
                      bold=True, color=THEME["text"], halign="right",
                      size_hint_y=None, height=dp(44))
        title.bind(size=lambda l, s: setattr(l, "text_size", (s[0], None)))
        main.add_widget(title)

        def section(text, color=None):
            l = Label(text=fa(text), font_name=FONT, font_size=dp(13),
                      color=color or THEME["muted"], halign="right",
                      size_hint_y=None, height=dp(24))
            l.bind(size=lambda x, s: setattr(x, "text_size", (s[0], None)))
            main.add_widget(l)

        section("تم رنگی")
        self.theme_row = BoxLayout(orientation="horizontal", spacing=dp(6),
                                   size_hint_y=None, height=dp(60))
        self.theme_btns = {}
        for key, th in THEMES.items():
            b = RoundedButton(text=fa(th["label"]), font_name=FONT,
                              font_size=dp(12), button_color=th["primary"],
                              radius=14)
            b.bind(on_release=lambda *a, k=key: self.pick_theme(k))
            self.theme_btns[key] = b
            self.theme_row.add_widget(b)
        main.add_widget(self.theme_row)

        section("صدای پایان جلسه")
        self.sound_btn = RoundedButton(text="", font_name=FONT, font_size=dp(15),
                                       bold=True, size_hint_y=None, height=dp(52),
                                       button_color=THEME["secondary"])
        self.sound_btn.bind(on_release=self.toggle_sound)
        main.add_widget(self.sound_btn)

        section("هدف مطالعه روزانه (دقیقه)")
        self.goal_input = TextInput(text="", font_name=FONT, font_size=dp(16),
                                    multiline=False, input_filter="int",
                                    halign="center", size_hint_y=None, height=dp(50),
                                    padding=[dp(10), dp(14), dp(10), dp(14)],
                                    background_color=THEME["card2"],
                                    foreground_color=THEME["text"],
                                    cursor_color=THEME["primary"])
        self.goal_input.bind(text=self.save_goal)
        main.add_widget(self.goal_input)

        section("پشتیبان‌گیری")
        backup_btn = RoundedButton(text=fa("نمایش داده‌ها (JSON)"), font_name=FONT,
                                   font_size=dp(14), size_hint_y=None, height=dp(50),
                                   button_color=THEME["primary_d"])
        backup_btn.bind(on_release=self.show_backup)
        main.add_widget(backup_btn)

        section("ناحیه خطر", THEME["danger"])
        reset_btn = RoundedButton(text=fa("پاک کردن همه اطلاعات"), font_name=FONT,
                                  font_size=dp(14), bold=True,
                                  size_hint_y=None, height=dp(52),
                                  button_color=THEME["danger"])
        reset_btn.bind(on_release=self.confirm_reset)
        main.add_widget(reset_btn)

        section("درباره")
        about_btn = RoundedButton(text=fa("درباره StudyMate"), font_name=FONT,
                                  font_size=dp(14), size_hint_y=None, height=dp(50),
                                  button_color=THEME["card2"])
        about_btn.bind(on_release=self.show_about)
        main.add_widget(about_btn)

        back = RoundedButton(text=fa("بازگشت"), font_name=FONT, font_size=dp(15),
                             size_hint_y=None, height=dp(50),
                             button_color=THEME["card2"])
        back.bind(on_release=lambda *a: self._go_home())
        main.add_widget(back)
        self.add_widget(scroll)

    def _go_home(self):
        if self.manager is not None:
            self.manager.current = "home"

    def on_pre_enter(self):
        self.refresh()

    def refresh(self):
        try:
            app = App.get_running_app()
        except Exception:
            return
        cur = app.db.get_setting("theme", "dark")
        for k, b in self.theme_btns.items():
            if k == cur:
                b.set_color(THEMES[k]["primary"])
                b.color = THEME["on_prim"]
            else:
                b.set_color(THEME["card2"])
                b.color = THEME["text"]
        is_sound = app.db.get_setting("sound", True)
        self.sound_btn.text = fa("🔊 روشن" if is_sound else "🔇 خاموش")
        self.goal_input.text = str(app.db.get_setting("daily_goal", 60))

    def pick_theme(self, key):
        try:
            app = App.get_running_app()
            app.db.set_setting("theme", key)
            set_theme(key)
            app.rebuild_ui("settings")
        except Exception:
            pass

    def toggle_sound(self, *a):
        try:
            app = App.get_running_app()
            cur = app.db.get_setting("sound", True)
            app.db.set_setting("sound", not cur)
            self.refresh()
        except Exception:
            pass

    def save_goal(self, instance, text):
        if not text:
            return
        try:
            v = int(text)
            if v >= 1:
                App.get_running_app().db.set_setting("daily_goal", v)
        except Exception:
            pass

    def show_backup(self, *a):
        try:
            data = App.get_running_app().db.export_json()
        except Exception:
            return
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        sv = ScrollView()
        txt = TextInput(text=data, font_name=FONT, font_size=dp(11),
                        multiline=True, readonly=True,
                        background_color=THEME["card2"],
                        foreground_color=THEME["text"])
        sv.add_widget(txt)
        content.add_widget(sv)
        popup = Popup(title=fa("پشتیبان"), title_font=FONT, title_size=dp(15),
                      title_color=THEME["text"], content=content,
                      size_hint=(0.95, 0.85), background_color=THEME["card"],
                      background="", separator_color=THEME["primary"])
        popup.open()

    def confirm_reset(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(20))
        content.add_widget(Label(text=fa("همه اطلاعات پاک شود؟"), font_name=FONT,
                                 font_size=dp(15), color=THEME["text"]))
        row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(54))
        yes = RoundedButton(text=fa("بله"), font_name=FONT, font_size=dp(15),
                            button_color=THEME["danger"])
        no = RoundedButton(text=fa("لغو"), font_name=FONT, font_size=dp(15),
                           button_color=THEME["card2"])
        row.add_widget(yes)
        row.add_widget(no)
        content.add_widget(row)
        popup = Popup(title=fa("تأیید"), title_font=FONT, title_size=dp(15),
                      title_color=THEME["text"], content=content,
                      size_hint=(0.85, 0.4), background_color=THEME["card"],
                      background="", separator_color=THEME["danger"])

        def do_reset(*a):
            try:
                app = App.get_running_app()
                app.db.reset_all()
                popup.dismiss()
                app.rebuild_ui("home")
            except Exception:
                pass

        yes.bind(on_release=do_reset)
        no.bind(on_release=popup.dismiss)
        popup.open()

    def show_about(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(20))
        content.add_widget(Label(text="StudyMate", font_name=FONT,
                                 font_size=dp(28), bold=True,
                                 color=THEME["primary"],
                                 size_hint_y=None, height=dp(44)))
        content.add_widget(Label(text="v3.3 Final", font_name=FONT,
                                 font_size=dp(13), color=THEME["muted"],
                                 size_hint_y=None, height=dp(22)))
        content.add_widget(Label(text=fa("دستیار حرفه‌ای مطالعه"), font_name=FONT,
                                 font_size=dp(14), color=THEME["text"],
                                 size_hint_y=None, height=dp(26)))
        content.add_widget(Label(text=fa("ساخته‌شده با ❤️ با Kivy"), font_name=FONT,
                                 font_size=dp(12), color=THEME["muted"],
                                 size_hint_y=None, height=dp(22)))
        content.add_widget(Label(text=fa(
            "• پومودورو\n• فلش‌کارت SRS\n• آمار و نمودار\n• استریک و نشان‌ها"),
            font_name=FONT, font_size=dp(12), color=THEME["muted"]))
        popup = Popup(title="", title_size=0, content=content,
                      size_hint=(0.85, 0.6), background_color=THEME["card"],
                      background="", separator_color=THEME["primary"])
        popup.open()

# ══════════════════════════════════════════════════════════════
# APP
# ══════════════════════════════════════════════════════════════
class StudyMateApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DB()
        self._beep = None
        self._ach_queue = []
        self._ach_active = False
        self.root = None

    def toast(self, msg):
        try:
            content = BoxLayout(padding=dp(20))
            content.add_widget(Label(text=fa(msg), font_name=FONT,
                                     font_size=dp(14), color=THEME["text"]))
            popup = Popup(title="", title_size=0, content=content,
                          size_hint=(0.75, 0.22), background_color=THEME["card"],
                          background="", separator_color=THEME["primary"])
            popup.open()
            Clock.schedule_once(lambda dt: popup.dismiss(), 1.6)
        except Exception:
            pass

    def play_beep(self):
        try:
            if self._beep is None:
                p = make_beep()
                if p:
                    self._beep = SoundLoader.load(p)
            if self._beep:
                self._beep.play()
        except Exception:
            pass

    def notify(self, title, message):
        if plyer_notif is None:
            return
        try:
            plyer_notif.notify(title=title, message=message,
                               app_name="StudyMate", timeout=10)
        except Exception:
            pass

    def check_achievements(self):
        try:
            db = self.db
            earned = db.earned_achievements()
            new = []

            def add(k):
                if k not in earned and db.earn_achievement(k):
                    new.append(k)

            total_min = db.total_seconds() // 60
            sessions = db.total_sessions()
            streak = compute_streak(db.session_dates())
            lvl, _, _ = xp_to_level(int(total_min))
            fc = db.flashcards_count()
            tasks_done = db.tasks_done_count()
            notes = db.notes()
            subs = db.subjects()

            if sessions >= 1:
                add("first_step")
            if sessions >= 10:
                add("ten_sessions")
            if sessions >= 50:
                add("fifty_sessions")
            if sessions >= 100:
                add("hundred_sessions")
            if total_min >= 60:
                add("hour_1")
            if total_min >= 600:
                add("hour_10")
            if total_min >= 3000:
                add("hour_50")
            if streak >= 3:
                add("streak_3")
            if streak >= 7:
                add("streak_7")
            if streak >= 30:
                add("streak_30")
            if lvl >= 5:
                add("level_5")
            if lvl >= 10:
                add("level_10")
            if lvl >= 25:
                add("level_25")
            h = datetime.now().hour
            if 0 <= h < 7:
                add("early_bird")
            if h >= 23 or h < 3:
                add("night_owl")
            if fc >= 10:
                add("flashcard_10")
            if tasks_done >= 10:
                add("task_master")
            if len(notes) >= 5:
                add("note_keeper")
            if len(subs) >= 5:
                add("subject_5")

            for k in new:
                self._ach_queue.append(k)
            if new:
                Clock.schedule_once(lambda dt: self._show_next_ach(), 0.4)
        except Exception:
            pass

    def _show_next_ach(self):
        if self._ach_active or not self._ach_queue:
            return
        key = self._ach_queue.pop(0)
        self._display_ach(key)

    def _display_ach(self, key):
        if key not in ACH_MAP:
            self._show_next_ach()
            return
        self._ach_active = True
        icon, title, desc = ACH_MAP[key]
        try:
            content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(20))
            content.add_widget(Label(text=icon, font_name=FONT, font_size=dp(54),
                                     size_hint_y=None, height=dp(66)))
            content.add_widget(Label(text=fa("🏆 نشان جدید!"), font_name=FONT,
                                     font_size=dp(16), bold=True,
                                     color=THEME["warning"],
                                     size_hint_y=None, height=dp(26)))
            content.add_widget(Label(text=fa(title), font_name=FONT,
                                     font_size=dp(20), bold=True,
                                     color=THEME["text"],
                                     size_hint_y=None, height=dp(34)))
            content.add_widget(Label(text=fa(desc), font_name=FONT,
                                     font_size=dp(12), color=THEME["muted"],
                                     size_hint_y=None, height=dp(22)))
            ok = RoundedButton(text=fa("ادامه"), font_name=FONT, font_size=dp(15),
                               bold=True, size_hint_y=None, height=dp(50),
                               button_color=THEME["warning"])
            content.add_widget(ok)
            popup = Popup(title="", title_size=0, content=content,
                          size_hint=(0.85, 0.6), background_color=THEME["card"],
                          background="", separator_color=THEME["warning"])

            def close(*a):
                popup.dismiss()

            def on_dismiss(*a):
                self._ach_active = False
                Clock.schedule_once(lambda dt: self._show_next_ach(), 0.35)

            ok.bind(on_release=close)
            popup.bind(on_dismiss=on_dismiss)
            popup.open()
            if self.db.get_setting("sound", True):
                self.play_beep()
        except Exception:
            self._ach_active = False

    def _make_screens(self):
        return [
            SplashScreen(name="splash"),
            OnboardingScreen(name="onboarding"),
            HomeScreen(name="home"),
            TimerScreen(name="timer"),
            SubjectsScreen(name="subjects"),
            FlashcardsScreen(name="flashcards"),
            FlashcardStudyScreen(name="fc_study"),
            TasksScreen(name="tasks"),
            NotesScreen(name="notes"),
            StatsScreen(name="stats"),
            AchievementsScreen(name="achievements"),
            SettingsScreen(name="settings"),
        ]

    def rebuild_ui(self, go_to=None):
        current = go_to or (self.root.current if self.root else "home")
        try:
            if self.root:
                t = self.root.get_screen("timer")
                if t.running:
                    t.pause()
        except Exception:
            pass
        # reset achievement queue
        self._ach_queue = []
        self._ach_active = False
        try:
            self.root.clear_widgets()
            for s in self._make_screens():
                self.root.add_widget(s)
            try:
                self.root.current = current
            except Exception:
                self.root.current = "home"
        except Exception:
            pass

    def build(self):
        theme = self.db.get_setting("theme", "dark")
        set_theme(theme)
        self.root = ScreenManager(transition=FadeTransition(duration=0.22))
        for s in self._make_screens():
            self.root.add_widget(s)
        self.root.current = "splash"
        return self.root

    def on_stop(self):
        try:
            if self.root:
                t = self.root.get_screen("timer")
                if (t.running or t.elapsed > 0) and t.remaining > 0:
                    self.db.set_setting("active_timer", {
                        "mode": t.mode,
                        "cycle": t.cycle,
                        "duration": t.duration,
                        "remaining": t.remaining,
                        "elapsed": t.elapsed,
                        "subject": t.selected_subject,
                    })
                else:
                    self.db.set_setting("active_timer", None)
        except Exception:
            pass


if __name__ == "__main__":
    StudyMateApp().run()