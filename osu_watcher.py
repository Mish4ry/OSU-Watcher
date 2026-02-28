from pathlib import Path
from tkinter import filedialog
from tkinter import filedialog, messagebox
from typing import Callable
import base64
import datetime
import errno
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import threading

from PIL import Image
import customtkinter as ctk


# ====================================================================
# assets.py
# ====================================================================

LOGO_B64 = "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"

ICO_B64 = "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"

# ====================================================================
# utils.py
# ====================================================================

INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def file_hash(path: Path, chunk: int = 65536) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        while data := f.read(chunk):
            h.update(data)
    return h.hexdigest()


def sanitize(name: str) -> str:
    return INVALID_CHARS.sub("_", name).strip()


def unique_dest(folder: Path, name: str, ext: str) -> Path:
    dest = folder / f"{name}{ext}"
    c = 1
    while dest.exists():
        dest = folder / f"{name}_{c}{ext}"
        c += 1
    return dest


def get_free_space(path: Path) -> int:
    try:
        return shutil.disk_usage(path).free
    except Exception:
        return float("inf")


def format_size(n: int) -> str:
    for unit in ("o", "Ko", "Mo", "Go"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} To"

# ====================================================================
# config.py
# ====================================================================

CONFIG_PATH = Path.home() / "AppData" / "Local" / "osu_tool" / "config.json"

_DEFAULT_REPLAYS_DEST = Path.home() / "Desktop" / "OSU!" / "replays"
_DEFAULT_BG_DEST      = Path.home() / "Desktop" / "OSU!" / "Miniature"


def load() -> dict:
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save(data: dict) -> None:
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def get_replays_dest() -> Path:
    cfg = load()
    return Path(cfg["replays_dest"]) if "replays_dest" in cfg else _DEFAULT_REPLAYS_DEST


def get_bg_dest() -> Path:
    cfg = load()
    return Path(cfg["bg_dest"]) if "bg_dest" in cfg else _DEFAULT_BG_DEST


def get_shortcuts() -> dict:
    cfg = load()
    defaults = {
        "scan":   "<F5>",
        "send":   "<Return>",
        "clean":  "<F6>",
        "export": "<Control-s>",
    }
    saved = cfg.get("shortcuts", {})
    return {k: saved.get(k, v) for k, v in defaults.items()}


def set_replays_dest(path: Path) -> None:
    cfg = load()
    cfg["replays_dest"] = str(path)
    save(cfg)


def set_bg_dest(path: Path) -> None:
    cfg = load()
    cfg["bg_dest"] = str(path)
    save(cfg)


def set_osu_path(path: Path) -> None:
    cfg = load()
    cfg["osu_path"] = str(path)
    save(cfg)


def set_shortcuts(shortcuts: dict) -> None:
    cfg = load()
    cfg["shortcuts"] = shortcuts
    save(cfg)

# ====================================================================
# osu_path.py
# ====================================================================

_root: list[Path | None] = [None]  # liste pour permettre la mutation depuis App


def detect() -> Path | None:
    """Détecte le dossier osu! depuis la config ou les emplacements courants."""
    c = cfg.load()
    if "osu_path" in c:
        p = Path(c["osu_path"])
        if p.exists() and (p / "Replays").exists():
            return p

    candidates = [
        Path.home() / "AppData" / "Local" / "osu!",
        Path("C:/Games/osu!"),
        Path("D:/osu!"),
        Path("E:/osu!"),
    ]
    for candidate in candidates:
        if candidate.exists() and (candidate / "Replays").exists():
            return candidate
    return None


def init() -> None:
    _root[0] = detect()


def get() -> Path | None:
    return _root[0]


def set(path: Path) -> None:
    _root[0] = path
    cfg.set_osu_path(path)


def get_replays_folder() -> Path | None:
    return (_root[0] / "Replays") if _root[0] else None


def get_songs_folder() -> Path | None:
    return (_root[0] / "Songs") if _root[0] else None

# ====================================================================
# scanner.py
# ====================================================================

def get_map_info(osu_file: Path) -> tuple[Path | None, str]:
    """Extrait le chemin du fond d'écran et le nom de la beatmap depuis un .osu."""
    artist = title = ""
    bg_path = None
    try:
        with open(osu_file, "r", encoding="utf-8", errors="ignore") as f:
            in_events = in_meta = False
            for line in f:
                s = line.strip()
                if s == "[Metadata]":       in_meta, in_events = True, False
                elif s == "[Events]":       in_events, in_meta = True, False
                elif s.startswith("["):     in_meta = in_events = False
                if in_meta:
                    if s.startswith("Artist:"):  artist = s.split(":", 1)[1].strip()
                    elif s.startswith("Title:"): title  = s.split(":", 1)[1].strip()
                if in_events and s.startswith('0,0,"'):
                    parts = s.split(",")
                    if len(parts) >= 3:
                        img = parts[2].strip().strip('"')
                        p = osu_file.parent / img
                        if p.exists() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp"):
                            bg_path = p
    except Exception:
        pass
    map_name = sanitize(
        f"{artist} - {title}" if artist and title else title or osu_file.parent.name
    )
    return bg_path, map_name


def scan_replays(
    log: Callable[[str], None],
    progress: Callable[[float], None],
    seen_replays: set,
) -> list[Path]:
    folder = osu_path.get_replays_folder()
    if not folder or not folder.exists():
        log("⚠️  Replays folder not found! Set the osu! path in ⚙ Options.")
        progress(1)
        return []

    files = list(folder.glob("*.osr"))
    to_send = []
    total = len(files)
    log(f"🔍 {total} replay(s) detected…")
    for i, f in enumerate(files):
        if f.name in seen_replays:
            log(f"  ⏩ already known: {f.name}")
        else:
            to_send.append(f)
            log(f"  📄 {f.name}")
        progress((i + 1) / total if total else 1)
    log(f"→ {len(to_send)} replay(s) to send\n")
    return to_send


def scan_backgrounds(
    log: Callable[[str], None],
    progress: Callable[[float], None],
    status: Callable[[str], None],
    seen_hashes: set,
    quick: bool = False,
) -> list[tuple[Path, str]]:
    folder = osu_path.get_songs_folder()
    if not folder or not folder.exists():
        log("⚠️  Songs folder not found! Set the osu! path in ⚙ Options.")
        progress(1)
        return []

    all_dirs = sorted({f.parent for f in folder.rglob("*.osu")})
    if quick:
        cutoff = datetime.datetime.now() - datetime.timedelta(days=7)
        dirs = [d for d in all_dirs
                if datetime.datetime.fromtimestamp(d.stat().st_mtime) >= cutoff]
        log(f"⚡ Quick scan: {len(dirs)}/{len(all_dirs)} recent folder(s) (7 days)…")
    else:
        dirs = all_dirs
        log(f"🔍 {len(dirs)} beatmap(s) to analyze…")

    total = len(dirs)
    to_send = []
    for i, bdir in enumerate(dirs):
        progress((i + 1) / total if total else 1)
        status(f"Scanning map {i + 1}/{total}…")
        for osu in bdir.glob("*.osu"):
            bg, name = get_map_info(osu)
            if bg is None:
                continue
            h = file_hash(bg)
            if h in seen_hashes:
                break
            seen_hashes.add(h)
            to_send.append((bg, name))
            log(f"  🖼️  {name}{bg.suffix}")
            break

    log(f"→ {len(to_send)} background(s) to send\n")
    return to_send

# ====================================================================
# notifier.py
# ====================================================================

try:
    from win10toast import ToastNotifier
    _TOAST_OK = True
except ImportError:
    _TOAST_OK = False


def notify(title: str, msg: str, duration: int = 4) -> None:
    """Affiche une notification Windows toast de façon non-bloquante."""
    def _do():
        if _TOAST_OK:
            try:
                n = ToastNotifier()
                n.show_toast(title, msg, duration=duration, threaded=True)
                return
            except Exception:
                pass

        # Fallback : PowerShell natif (aucune dépendance requise)
        try:
            safe_msg = msg.replace("'", "''")
            safe_title = title.replace("'", "''")
            ps = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "$n=New-Object System.Windows.Forms.NotifyIcon;"
                "$n.Icon=[System.Drawing.SystemIcons]::Information;"
                "$n.Visible=$true;"
                f"$n.ShowBalloonTip({duration * 1000},'{safe_title}','{safe_msg}',"
                "[System.Windows.Forms.ToolTipIcon]::Info);"
                f"Start-Sleep -Milliseconds {duration * 1000 + 1000};"
                "$n.Dispose()"
            )
            subprocess.Popen(
                ["powershell", "-WindowStyle", "Hidden", "-Command", ps],
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            )
        except Exception:
            pass

    threading.Thread(target=_do, daemon=True).start()

# ====================================================================
# theme.py
# ====================================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PINK   = "#FF66AA"
DARK   = "#0D0D14"
CARD   = "#13131F"
CARD2  = "#1A1A2E"
BORDER = "#2A2A45"
WHITE  = "#E8E8F0"
DIM    = "#5050A0"
ORANGE = "#FF8833"

# ====================================================================
# options_window.py
# ====================================================================

class OptionsWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_forget_cb, on_shortcuts_saved_cb):
        super().__init__(parent)
        self._parent            = parent
        self._on_forget         = on_forget_cb
        self._on_shortcuts_saved = on_shortcuts_saved_cb

        self.title("Options")
        self.geometry("520x860")
        self.resizable(False, False)
        self.configure(fg_color=DARK)
        self.grab_set()

        self._build()

    # ─────────────────────────────── build ───────────────────────────────

    def _build(self):
        ctk.CTkLabel(self, text="⚙  Options",
            font=ctk.CTkFont("Trebuchet MS", 18, "bold"), text_color=PINK
        ).pack(pady=(18, 4))

        self._sep()

        # ── Dossier osu! source ──
        f_osu = self._section("🎮  osu! folder (source)")
        cur = str(osu_path.get()) if osu_path.get() else "Not configured"
        self._osu_lbl = ctk.CTkLabel(f_osu, text=cur,
            font=ctk.CTkFont("Consolas", 10), text_color=DIM, wraplength=390, anchor="w")
        self._osu_lbl.pack(anchor="w", padx=14, pady=(0, 4))
        ctk.CTkButton(f_osu, text="📁  Browse…",
            font=ctk.CTkFont("Trebuchet MS", 11),
            fg_color=CARD2, hover_color=BORDER, text_color=WHITE,
            border_width=1, border_color=BORDER, corner_radius=8, height=28,
            command=self._browse_osu
        ).pack(padx=14, pady=(0, 10), anchor="w")

        self._sep()

        # ── Destinations ──
        f_r = self._section("📄  Destination — Replays")
        self._dest_r_lbl = self._path_row(
            f_r, config.get_replays_dest(),
            lambda lbl: self._browse_dest("replays_dest", lbl, "Replays")
        )

        f_b = self._section("🖼️   Destination — Backgrounds")
        self._dest_b_lbl = self._path_row(
            f_b, config.get_bg_dest(),
            lambda lbl: self._browse_dest("bg_dest", lbl, "Fonds")
        )

        self._sep()

        # ── Raccourcis clavier ──
        f_keys = self._section("⌨️  Keyboard shortcuts")
        sc_now = config.get_shortcuts()
        shortcuts_def = [
            ("scan",   "Scan",          "<F5>"),
            ("send",   "Send",          "<Return>"),
            ("clean",  "Auto-Cleanup",   "<F6>"),
            ("export", "Export log", "<Control-s>"),
        ]
        self._sc_vars: dict[str, ctk.StringVar] = {}
        grid = ctk.CTkFrame(f_keys, fg_color="transparent")
        grid.pack(padx=14, pady=(0, 10), fill="x")
        for row_i, (key, label, default) in enumerate(shortcuts_def):
            ctk.CTkLabel(grid, text=label,
                font=ctk.CTkFont("Trebuchet MS", 11), text_color=DIM, anchor="w"
            ).grid(row=row_i, column=0, sticky="w", pady=2, padx=(0, 8))
            var = ctk.StringVar(value=sc_now.get(key, default))
            self._sc_vars[key] = var
            ctk.CTkEntry(grid, textvariable=var,
                font=ctk.CTkFont("Consolas", 11), width=140, height=26
            ).grid(row=row_i, column=1, sticky="w", pady=2)

        ctk.CTkButton(f_keys, text="💾  Save shortcuts",
            font=ctk.CTkFont("Trebuchet MS", 11),
            fg_color=CARD2, hover_color=BORDER, text_color=WHITE,
            border_width=1, border_color=BORDER, corner_radius=8, height=28,
            command=self._save_shortcuts
        ).pack(padx=14, pady=(0, 10), anchor="w")

        self._sep()

        # ── Oublier ──
        ctk.CTkButton(self,
            text="🗑  Forget all  (reset memory)",
            font=ctk.CTkFont("Trebuchet MS", 12),
            fg_color="#1A1A0A", hover_color="#332200", text_color=ORANGE,
            border_width=1, border_color=ORANGE, corner_radius=10, height=36,
            command=lambda: [self._on_forget(), self.destroy()]
        ).pack(padx=24, pady=8, fill="x")

    # ───────────────────────────── helpers ───────────────────────────────

    def _sep(self, parent=None):
        ctk.CTkFrame(parent or self, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=6)

    def _section(self, title: str) -> ctk.CTkFrame:
        f = ctk.CTkFrame(self, fg_color=CARD, corner_radius=10)
        f.pack(padx=24, pady=4, fill="x")
        ctk.CTkLabel(f, text=title,
            font=ctk.CTkFont("Trebuchet MS", 12, "bold"), text_color=WHITE
        ).pack(anchor="w", padx=14, pady=(10, 2))
        return f

    def _path_row(self, parent, path_val, on_browse) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(parent, text=str(path_val),
            font=ctk.CTkFont("Consolas", 10), text_color=DIM, wraplength=390, anchor="w")
        lbl.pack(anchor="w", padx=14, pady=(0, 4))
        ctk.CTkButton(parent, text="📁  Browse…",
            font=ctk.CTkFont("Trebuchet MS", 11),
            fg_color=CARD2, hover_color=BORDER, text_color=WHITE,
            border_width=1, border_color=BORDER, corner_radius=8, height=28,
            command=lambda: on_browse(lbl)
        ).pack(padx=14, pady=(0, 10), anchor="w")
        return lbl

    # ───────────────────────────── actions ───────────────────────────────

    def _browse_osu(self):
        folder = filedialog.askdirectory(
            title="Select the osu! folder (the one containing Replays and Songs)",
            initialdir=str(Path.home()), parent=self,
        )
        if folder:
            p = Path(folder)
            if (p / "Replays").exists():
                osu_path.set(p)
                self._osu_lbl.configure(text=str(p))
                self._parent.log(f"✔  osu! path configured: {p}")
                self._parent.status("osu! path updated. Run a scan.")
            else:
                self._parent.log(f"⚠️  No 'Replays' subfolder found in: {p}")

    def _browse_dest(self, cfg_key: str, lbl: ctk.CTkLabel, label: str):
        current = config.get_replays_dest() if cfg_key == "replays_dest" else config.get_bg_dest()
        folder = filedialog.askdirectory(
            title=f"Destination for {label}", initialdir=str(current), parent=self,
        )
        if folder:
            p = Path(folder)
            if cfg_key == "replays_dest":
                config.set_replays_dest(p)
            else:
                config.set_bg_dest(p)
            lbl.configure(text=str(p))
            self._parent.log(f"✔  {label} destination updated: {p}")

    def _save_shortcuts(self):
        sc = {k: v.get() for k, v in self._sc_vars.items()}
        config.set_shortcuts(sc)
        self._on_shortcuts_saved()
        self._parent.log("✔  Shortcuts saved and applied.")
        self.destroy()

# ====================================================================
# app.py
# ====================================================================

try:
    import pystray
    _PYSTRAY_OK = True
except ImportError:
    _PYSTRAY_OK = False


# ─────────────────────────────────────────────────────────────────────────────


class App(ctk.CTk):
    VERSION = "v0.1-alpha"

    def __init__(self):
        super().__init__()
        self.title("osu! Tool")
        self.geometry("660x800")
        self.resizable(False, False)
        self.configure(fg_color=DARK)

        self._seen_replays: set = set()
        self._seen_hashes:  set = set()
        self._pending_r: list[Path] = []
        self._pending_b: list[tuple[Path, str]] = []
        self._log_entries: list[dict] = []
        self._tray_icon = None
        self._last_dest: Path | None = None

        self.var_quick = ctk.BooleanVar(value=False)
        self.var_r     = ctk.BooleanVar(value=True)
        self.var_b     = ctk.BooleanVar(value=True)

        self._build()
        osu_path.init()
        self._check_osu_path()
        self._setup_shortcuts()

    # ═══════════════════════════════ BUILD ═══════════════════════════════

    def _build(self):
        # ── Logo + titre ──
        img_data = base64.b64decode(LOGO_B64)
        pil_img  = Image.open(io.BytesIO(img_data)).resize((44, 44), Image.LANCZOS)
        self._logo = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(44, 44))
        try:
            ico_data = base64.b64decode(ICO_B64)
            ico_img  = Image.open(io.BytesIO(ico_data))
            self._ico_ctk = ctk.CTkImage(light_image=ico_img, dark_image=ico_img, size=(1, 1))
            tmp = io.BytesIO()
            ico_img.save(tmp, format="ICO")
            tmp.seek(0)
            from PIL import ImageTk
            self._ico_tk = ImageTk.PhotoImage(Image.open(tmp))
            self.iconphoto(True, self._ico_tk)
        except Exception:
            pass

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(padx=24, pady=(16, 8), fill="x")
        ctk.CTkLabel(header, image=self._logo, text="").pack(side="left")
        ctk.CTkLabel(header,
            text="osu! Tool",
            font=ctk.CTkFont("Trebuchet MS", 26, "bold"), text_color=PINK
        ).pack(side="left", padx=12)
        ctk.CTkLabel(header, text=self.VERSION,
            font=ctk.CTkFont("Trebuchet MS", 10), text_color=DIM
        ).pack(side="left")
        self.btn_options = ctk.CTkButton(header,
            text="⚙", width=36, height=36,
            font=ctk.CTkFont("Trebuchet MS", 16),
            fg_color=CARD2, hover_color=BORDER, text_color=DIM,
            border_width=1, border_color=BORDER, corner_radius=8,
            command=self._open_options,
        )
        self.btn_options.pack(side="right")

        # ── Séparateur ──
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=4)

        # ── Cards (Replays / Fonds) ──
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(padx=24, pady=(8, 0), fill="x")
        self._card(cards, "📄  Replays (.osr)",
            "Copies replay files to your folder.", self.var_r
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._card(cards, "🖼️  Fonds d'écran",
            "Extracts backgrounds from beatmaps.", self.var_b
        ).pack(side="right", fill="x", expand=True)

        # ── Scan rapide ──
        opts_row = ctk.CTkFrame(self, fg_color="transparent")
        opts_row.pack(padx=24, pady=(10, 0), fill="x")
        ctk.CTkCheckBox(opts_row,
            text="⚡ Quick scan (beatmaps from the last 7 days)",
            variable=self.var_quick,
            font=ctk.CTkFont("Trebuchet MS", 11),
            text_color=DIM, fg_color=PINK, hover_color="#DD3388",
            checkmark_color=DARK, corner_radius=4,
        ).pack(side="left")

        # ── Bouton Scanner ──
        self.btn_scan = ctk.CTkButton(self,
            text="🔍  Scan",
            font=ctk.CTkFont("Trebuchet MS", 14, "bold"),
            fg_color=PINK, hover_color="#DD3388", text_color=DARK,
            corner_radius=12, height=42,
            command=self._on_scan,
        )
        self.btn_scan.pack(padx=24, pady=(12, 0), fill="x")

        # ── Bouton Envoyer ──
        self.btn_send = ctk.CTkButton(self,
            text="➤  Send",
            font=ctk.CTkFont("Trebuchet MS", 14, "bold"),
            fg_color="#2A2A3A", hover_color="#2A2A3A", text_color="#55557A",
            corner_radius=12, height=42, state="disabled",
            command=self._on_send,
        )
        self.btn_send.pack(padx=24, pady=(8, 0), fill="x")

        # ── Barre de progression ──
        self.bar = ctk.CTkProgressBar(self,
            fg_color=CARD, progress_color=PINK, corner_radius=6, height=6)
        self.bar.pack(padx=24, pady=(8, 0), fill="x")
        self.bar.set(0)

        # ── Journal ──
        self.logbox = ctk.CTkTextbox(self,
            font=ctk.CTkFont("Consolas", 11),
            fg_color=CARD, text_color=WHITE,
            corner_radius=10, height=200, state="disabled",
            wrap="word",
        )
        self.logbox.pack(padx=24, pady=(10, 0), fill="x")

        # ── Ouvrir destination ──
        self.btn_open_dest = ctk.CTkButton(self,
            text="📂  Open destination folder",
            font=ctk.CTkFont("Trebuchet MS", 12),
            fg_color=CARD2, hover_color=BORDER, text_color=DIM,
            border_width=1, border_color=BORDER,
            corner_radius=10, height=36, state="disabled",
            command=self._open_dest_folder,
        )
        self.btn_open_dest.pack(padx=24, pady=(8, 0), fill="x")

        # ── Auto-nettoyage ──
        self.btn_clean = ctk.CTkButton(self,
            text="🧹  Auto-Cleanup (orphan backgrounds)",
            font=ctk.CTkFont("Trebuchet MS", 12),
            fg_color=CARD2, hover_color=BORDER, text_color=DIM,
            border_width=1, border_color=BORDER,
            corner_radius=10, height=36,
            command=self._on_clean,
        )
        self.btn_clean.pack(padx=24, pady=(6, 0), fill="x")

        # ── Boutons bas (export + systray) ──
        btm_row = ctk.CTkFrame(self, fg_color="transparent")
        btm_row.pack(padx=24, pady=(6, 0), fill="x")
        self.btn_export_log = ctk.CTkButton(btm_row,
            text="💾  Export log",
            font=ctk.CTkFont("Trebuchet MS", 12),
            fg_color=CARD2, hover_color=BORDER, text_color=DIM,
            border_width=1, border_color=BORDER, corner_radius=10, height=34,
            command=self._on_export_log,
        )
        self.btn_export_log.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.btn_tray = ctk.CTkButton(btm_row,
            text="🗕  Minimize to tray",
            font=ctk.CTkFont("Trebuchet MS", 12),
            fg_color=CARD2, hover_color=BORDER, text_color=DIM,
            border_width=1, border_color=BORDER, corner_radius=10, height=34,
            command=self._minimize_to_tray,
            state="normal" if _PYSTRAY_OK else "disabled",
        )
        self.btn_tray.pack(side="right", fill="x", expand=True)

        # ── Status bar ──
        self.lbl_status = ctk.CTkLabel(self,
            text="Run a scan to get started.",
            font=ctk.CTkFont("Trebuchet MS", 11), text_color=DIM)
        self.lbl_status.pack(pady=(6, 12))

    def _card(self, parent, title, subtitle, var) -> ctk.CTkFrame:
        f = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=12)
        ctk.CTkCheckBox(f, text=title, variable=var,
            font=ctk.CTkFont("Trebuchet MS", 14, "bold"),
            text_color=WHITE, fg_color=PINK, hover_color="#DD3388",
            checkmark_color=DARK, corner_radius=6,
        ).pack(padx=16, pady=(14, 2))
        ctk.CTkLabel(f, text=subtitle,
            font=ctk.CTkFont("Trebuchet MS", 10), text_color=DIM
        ).pack(padx=16, pady=(0, 12))
        return f

    # ═══════════════════════════════ LOG ═════════════════════════════════

    def log(self, msg: str):
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        self._log_entries.append({"ts": ts, "msg": msg})
        def _do():
            self.logbox.configure(state="normal")
            self.logbox.insert("end", msg + "\n")
            self.logbox.see("end")
            self.logbox.configure(state="disabled")
        self.after(0, _do)

    def status(self, t: str):
        self.after(0, lambda: self.lbl_status.configure(text=t))

    def prog(self, v: float):
        self.after(0, lambda: self.bar.set(v))

    # ══════════════════════════ RACCOURCIS ════════════════════════════════

    def _setup_shortcuts(self):
        sc = config.get_shortcuts()
        binds = {
            sc.get("scan",   "<F5>"):         lambda e: self._on_scan()  if str(self.btn_scan.cget("state")) == "normal" else None,
            sc.get("send",   "<Return>"):      lambda e: self._on_send()  if str(self.btn_send.cget("state")) == "normal" else None,
            sc.get("clean",  "<F6>"):          lambda e: self._on_clean(),
            sc.get("export", "<Control-s>"):   lambda e: self._on_export_log(),
        }
        for key, cb in binds.items():
            try:
                self.bind_all(key, cb)
            except Exception:
                pass

    # ═══════════════════════════ SCAN / SEND ═════════════════════════════

    def _set_send_ready(self, n: int):
        def _do():
            if n > 0:
                self.btn_send.configure(
                    state="normal",
                    fg_color=PINK, hover_color="#DD3388", text_color=DARK,
                    text=f"➤  Send  ({n} file{'s' if n > 1 else ''})",
                )
            else:
                self.btn_send.configure(
                    state="disabled",
                    fg_color="#2A2A3A", hover_color="#2A2A3A", text_color="#55557A",
                    text="➤  Send",
                )
        self.after(0, _do)

    def _lock_scan(self, locked: bool):
        self.after(0, lambda: self.btn_scan.configure(
            state="disabled" if locked else "normal"
        ))

    def _on_scan(self):
        do_r, do_b = self.var_r.get(), self.var_b.get()
        if not do_r and not do_b:
            self.log("⚠️  Select at least one option!")
            return

        self._lock_scan(True)
        self._set_send_ready(0)
        self.bar.set(0)
        self._pending_r = []
        self._pending_b = []
        self.btn_open_dest.configure(
            state="disabled", text_color=DIM, border_color=BORDER,
            text="📂  Open destination folder"
        )

        seen_r = set(self._seen_replays)
        seen_h = set(self._seen_hashes)

        def task():
            self.status("Scanning…")
            self.log("━━━━━━━━━━━━  SCAN  ━━━━━━━━━━━━")
            quick = self.var_quick.get()

            if do_r and do_b:
                pr = scanner.scan_replays(self.log, lambda v: self.prog(v * 0.5), seen_r)
                pb = scanner.scan_backgrounds(self.log, lambda v: self.prog(0.5 + v * 0.5), self.status, seen_h, quick=quick)
            elif do_r:
                pr = scanner.scan_replays(self.log, self.prog, seen_r)
                pb = []
            else:
                pr = []
                pb = scanner.scan_backgrounds(self.log, self.prog, self.status, seen_h, quick=quick)

            def _update(pr=pr, pb=pb):
                self._pending_r = pr
                self._pending_b = pb
                total = len(pr) + len(pb)
                if total > 0:
                    self.log(f"✔  Scan complete — {total} file(s) ready to send.")
                    self.status(f"Scan complete — {total} file(s) ready")
                else:
                    self.log("✔  Everything is already up to date, nothing to send.")
                    self.status("Already up to date ✓")
                self._set_send_ready(total)
                self.btn_scan.configure(state="normal")
            self.after(0, _update)

        threading.Thread(target=task, daemon=True).start()

    def _on_send(self):
        if not self._pending_r and not self._pending_b:
            return

        pending_r = self._pending_r[:]
        pending_b = self._pending_b[:]
        total     = len(pending_r) + len(pending_b)

        self._set_send_ready(0)
        self._lock_scan(True)
        self.bar.set(0)

        def task():
            self.log("━━━━━━━━━━━━  SENDING  ━━━━━━━━━━━━")
            self.status("Sending…")

            dest_r = config.get_replays_dest()
            dest_b = config.get_bg_dest()

            # Supprimer puis recréer les dossiers destination
            for dest, label in [(dest_r, "Replays"), (dest_b, "Fonds")]:
                try:
                    if dest.exists():
                        shutil.rmtree(dest)
                        self.log(f"  🗑  {label} folder cleared.")
                    dest.mkdir(parents=True, exist_ok=True)
                    self.log(f"  📁  {label} folder recreated.")
                except Exception as ex:
                    self.log(f"  ❌  Could not reset {label} folder: {ex}")

            # Vérification espace disque
            needed_r = sum(f.stat().st_size for f in pending_r if f.exists())
            needed_b = sum(bg.stat().st_size for bg, _ in pending_b if bg.exists())
            free_r   = get_free_space(dest_r)
            free_b   = get_free_space(dest_b)
            same_drive = Path(dest_r.anchor) == Path(dest_b.anchor)

            if same_drive:
                if (needed_r + needed_b) > free_r:
                    self._show_disk_full(dest_r, format_size(needed_r + needed_b))
                    self._lock_scan(False)
                    return
            else:
                if pending_r and needed_r > free_r:
                    self._show_disk_full(dest_r, format_size(needed_r))
                    self._lock_scan(False)
                    return
                if pending_b and needed_b > free_b:
                    self._show_disk_full(dest_b, format_size(needed_b))
                    self._lock_scan(False)
                    return

            sent = 0

            for i, f in enumerate(pending_r):
                dst = unique_dest(dest_r, f.stem, f.suffix)
                try:
                    shutil.copy2(f, dst)
                    self.log(f"  ✅ {dst.name}")
                    self._seen_replays.add(f.name)
                    sent += 1
                except PermissionError:
                    self.log(f"  ❌ {f.name} — Permission denied")
                except OSError as ex:
                    if ex.errno == errno.ENOSPC:
                        self.log(f"  ❌ {f.name} — Disk full! Free: {format_size(get_free_space(dest_r))}")
                        self._show_disk_full(dest_r, f.name)
                    elif ex.errno == errno.ENOENT:
                        self.log(f"  ❌ {f.name} — File not found (deleted?)")
                    else:
                        self.log(f"  ❌ {f.name} — Error [{ex.errno}]: {ex.strerror}")
                except Exception as ex:
                    self.log(f"  ❌ {f.name} — {ex}")
                self.prog((i + 1) / total)

            offset = len(pending_r)
            for i, (bg, name) in enumerate(pending_b):
                dst = unique_dest(dest_b, name, bg.suffix)
                try:
                    shutil.copy2(bg, dst)
                    self.log(f"  ✅ {dst.name}")
                    self._seen_hashes.add(file_hash(bg))
                    sent += 1
                except PermissionError:
                    self.log(f"  ❌ {name} — Permission denied")
                except OSError as ex:
                    if ex.errno == errno.ENOSPC:
                        self.log(f"  ❌ {name} — Disk full! Free: {format_size(get_free_space(dest_b))}")
                        self._show_disk_full(dest_b, name)
                    elif ex.errno == errno.ENOENT:
                        self.log(f"  ❌ {name} — File not found")
                    else:
                        self.log(f"  ❌ {name} — Error [{ex.errno}]: {ex.strerror}")
                except Exception as ex:
                    self.log(f"  ❌ {name} — {ex}")
                self.prog((offset + i + 1) / total)

            errors = total - sent
            self.log(f"✔  {sent} file(s) sent successfully!")
            if errors:
                self.log(f"⚠️  {errors} file(s) failed.")
            self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.status(f"✔  {sent} file(s) sent{(' — ⚠️ ' + str(errors) + ' error(s)') if errors else ''}")
            self._pending_r = []
            self._pending_b = []
            self._lock_scan(False)

            if sent > 0 or errors > 0:
                msg_notif = f"{sent} file(s) copied"
                if errors:
                    msg_notif += f", {errors} error(s)"
                self.after(0, lambda m=msg_notif: notifier.notify("osu! Tool", m))

            if sent > 0:
                if pending_r and pending_b:
                    self._last_dest = config.get_replays_dest().parent
                elif pending_r:
                    self._last_dest = config.get_replays_dest()
                else:
                    self._last_dest = config.get_bg_dest()
                self.after(0, self._enable_open_dest)

        threading.Thread(target=task, daemon=True).start()

    # ══════════════════════════ NETTOYAGE ═════════════════════════════════

    def _on_clean(self):
        songs_folder = osu_path.get_songs_folder()
        bg_dest      = config.get_bg_dest()

        if not songs_folder or not songs_folder.exists():
            self.log("⚠️  Songs folder not found — cleanup unavailable.")
            return
        if not bg_dest.exists():
            self.log("⚠️  Backgrounds folder not found — nothing to clean.")
            return

        def task():
            self.log("━━━━━━━━━  CLEANUP ANALYSIS  ━━━━━━━━━")
            self.status("Analyzing…")
            self._lock_scan(True)

            self.log("🔍 Computing osu! hashes…")
            osu_hashes: set = set()
            dirs = sorted({f.parent for f in songs_folder.rglob("*.osu")})
            for i, bdir in enumerate(dirs):
                self.status(f"Analyzing map {i+1}/{len(dirs)}…")
                for osu in bdir.glob("*.osu"):
                    bg, _ = scanner.get_map_info(osu)
                    if bg:
                        osu_hashes.add(file_hash(bg))
                    break

            exts = {".jpg", ".jpeg", ".png", ".bmp"}
            orphans = [f for f in bg_dest.iterdir()
                       if f.suffix.lower() in exts and file_hash(f) not in osu_hashes]

            if not orphans:
                self.log("✔  No orphaned files — everything is in sync!")
                self.status("Cleanup: nothing to remove ✓")
                self._lock_scan(False)
                return

            self.log(f"⚠️  {len(orphans)} orphaned file(s):")
            for f in orphans:
                self.log(f"  🗑  {f.name}")
            self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            def ask():
                answer = messagebox.askyesno(
                    "Confirm deletion",
                    f"Delete {len(orphans)} orphaned file(s)?\n\n"
                    f"Dossier : {bg_dest}\n\nCette action est irréversible.",
                    icon="warning", parent=self,
                )
                if answer:
                    deleted = 0
                    for f in orphans:
                        try:
                            f.unlink()
                            self.log(f"  ✅ Deleted: {f.name}")
                            deleted += 1
                        except Exception as ex:
                            self.log(f"  ❌ {f.name} — {ex}")
                    self.log(f"✔  {deleted} file(s) deleted.")
                    self.status(f"Cleanup done — {deleted} deleted")
                else:
                    self.log("↩  Cleanup cancelled.")
                    self.status("Cleanup cancelled.")
                self._lock_scan(False)

            self.after(0, ask)

        threading.Thread(target=task, daemon=True).start()

    # ════════════════════════════ OPTIONS ═════════════════════════════════

    def _open_options(self):
        OptionsWindow(
            parent=self,
            on_forget_cb=self._forget_all,
            on_shortcuts_saved_cb=self._setup_shortcuts,
        )

    def _forget_all(self):
        self._seen_replays.clear()
        self._seen_hashes.clear()
        self._pending_r = []
        self._pending_b = []
        self._set_send_ready(0)
        self.bar.set(0)
        self.log("🗑  Memory reset — next scan starts fresh.")
        self.status("Memory cleared. Run a new scan.")

    def _check_osu_path(self):
        if osu_path.get() is None:
            self.log("⚠️  osu! folder not found automatically.")
            self.log("   Use ⚙ Options → Locate osu! to configure it.")
            self.status("⚠️  osu! not found — set the path in ⚙ Options")
        else:
            src = "saved config" if "osu_path" in config.load() else "auto-detected"
            self.log(f"✔  osu! détecté ({src}) : {osu_path.get()}")
            self.status("Run a scan to get started.")

    # ═══════════════════════════ ACTIONS UI ══════════════════════════════

    def _enable_open_dest(self):
        self.btn_open_dest.configure(
            state="normal", fg_color=CARD2, hover_color=BORDER,
            text_color=WHITE, border_color=PINK,
            text="📂  Open destination folder",
        )

    def _open_dest_folder(self):
        dest = self._last_dest or config.get_replays_dest().parent
        dest.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.Popen(["explorer", str(dest)])
        except Exception:
            try:
                os.startfile(str(dest))
            except Exception as ex:
                self.log(f"⚠️  Cannot open folder: {ex}")

    def _show_disk_full(self, path: Path, filename: str):
        free  = get_free_space(path)
        drive = Path(path.anchor) if path.anchor else path
        def _popup():
            messagebox.showerror(
                "⚠️  Disk full",
                f"Impossible de copier : {filename}\n\n"
                f"Disque plein sur {drive}\n"
                f"Espace libre : {format_size(free)}\n\n"
                f"Free up some space and try again.",
                parent=self,
            )
        self.after(0, _popup)

    # ═══════════════════════════ EXPORT LOG ══════════════════════════════

    def _on_export_log(self):
        if not self._log_entries:
            self.log("⚠️  Log is empty, nothing to export.")
            return
        folder = filedialog.askdirectory(
            title="Choose export folder",
            initialdir=str(Path.home() / "Desktop"),
            parent=self,
        )
        if not folder:
            return
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base = Path(folder) / f"osu_tool_log_{ts}"
        try:
            with open(base.with_suffix(".txt"), "w", encoding="utf-8") as f:
                for e in self._log_entries:
                    f.write(f"[{e['ts']}] {e['msg']}\n")
            self.log(f"✔  Log .txt: {base.with_suffix('.txt').name}")
        except Exception as ex:
            self.log(f"❌  Export error .txt: {ex}")
        try:
            with open(base.with_suffix(".json"), "w", encoding="utf-8") as f:
                json.dump({
                    "exported_at": datetime.datetime.now().isoformat(),
                    "entries": self._log_entries,
                }, f, indent=2, ensure_ascii=False)
            self.log(f"✔  Log .json: {base.with_suffix('.json').name}")
        except Exception as ex:
            self.log(f"❌  Export error .json: {ex}")

    # ══════════════════════════ SYSTRAY ══════════════════════════════════

    def _minimize_to_tray(self):
        if not _PYSTRAY_OK:
            self.log("⚠️  pystray not installed (pip install pystray).")
            return
        if self._tray_icon:
            return
        self.withdraw()
        try:
            img_data = base64.b64decode(LOGO_B64)
            tray_img = Image.open(io.BytesIO(img_data)).resize((64, 64), Image.LANCZOS).convert("RGBA")
        except Exception:
            tray_img = Image.new("RGBA", (64, 64), (255, 102, 170, 255))

        def _restore(icon, _item):
            icon.stop()
            self._tray_icon = None
            self.after(0, self.deiconify)

        menu = pystray.Menu(
            pystray.MenuItem("🎵  Show osu! Tool", _restore, default=True),
            pystray.MenuItem("❌  Quit", lambda icon, _: [icon.stop(), self.after(0, self.destroy)]),
        )
        self._tray_icon = pystray.Icon("osu_tool", tray_img, "osu! Tool", menu)
        threading.Thread(target=self._tray_icon.run, daemon=True).start()
