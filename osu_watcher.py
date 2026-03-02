# ── Bootstrap : vérifie et installe les dépendances avant tout ──────────────
import sys, subprocess

def _bootstrap():
    import importlib.util
    deps = {"PyQt6": "PyQt6", "PIL": "pillow", "pystray": "pystray", "win10toast": "win10toast"}
    missing = [pip for mod, pip in deps.items() if importlib.util.find_spec(mod) is None]
    if not missing:
        return  # tout est déjà installé

    # Popup tkinter (toujours dispo avec Python)
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk(); root.withdraw()
    names = ", ".join(missing)
    ok = messagebox.askyesno(
        "osu! Tool — Installation requise",
        f"Les modules suivants sont manquants :\n\n  {names}\n\n"
        f"Voulez-vous les installer automatiquement ?\n"
        f"(Une fenêtre noire apparaîtra brièvement)",
        icon="question"
    )
    root.destroy()
    if not ok:
        sys.exit(0)

    # Installation silencieuse
    for pkg in missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg],
                              creationflags=0x08000000 if sys.platform == "win32" else 0)

    # Relancer le script après installation
    import os
    os.execv(sys.executable, [sys.executable] + sys.argv)

_bootstrap()
# ─────────────────────────────────────────────────────────────────────────────

from pathlib import Path
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

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QTextEdit, QProgressBar,
    QDialog, QScrollArea, QLineEdit, QGridLayout, QFrame,
    QFileDialog, QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QIcon, QPixmap, QImage, QShortcut, QKeySequence
import sys

LOGO_B64 = "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"

ICO_B64 = "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"

PINK   = "#FF66AA"
DARK   = "#0D0D14"
CARD   = "#13131F"
CARD2  = "#1A1A2E"
BORDER = "#2A2A45"
WHITE  = "#E8E8F0"
DIM    = "#5050A0"
ORANGE = "#FF8833"

STYLE = f"""
QMainWindow, QDialog {{ background-color: {DARK}; }}
QWidget {{ background-color: {DARK}; color: {WHITE}; font-family: 'Trebuchet MS'; font-size: 12px; }}
QPushButton {{ background-color: {CARD2}; color: {DIM}; border: 1px solid {BORDER}; border-radius: 8px; padding: 6px 14px; }}
QPushButton:hover {{ background-color: {BORDER}; color: {WHITE}; }}
QPushButton:disabled {{ background-color: #1A1A2A; color: #33335A; border-color: #1E1E35; }}
QPushButton#primary {{ background-color: {PINK}; color: {DARK}; border: none; border-radius: 10px; font-size: 14px; font-weight: bold; padding: 10px; }}
QPushButton#primary:hover {{ background-color: #DD3388; }}
QPushButton#primary:disabled {{ background-color: #2A2A3A; color: #55557A; border: none; }}
QTextEdit {{ background-color: {CARD}; color: {WHITE}; border: 1px solid {BORDER}; border-radius: 8px; font-family: Consolas; font-size: 11px; padding: 6px; }}
QProgressBar {{ background-color: {CARD}; border: none; border-radius: 3px; }}
QProgressBar::chunk {{ background-color: {PINK}; border-radius: 3px; }}
QCheckBox {{ color: {WHITE}; font-size: 13px; font-weight: bold; spacing: 8px; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 2px solid {BORDER}; background: {CARD2}; }}
QCheckBox::indicator:checked {{ background-color: {PINK}; border-color: {PINK}; }}
QCheckBox#dim {{ color: {DIM}; font-size: 11px; font-weight: normal; }}
QFrame#card {{ background-color: {CARD}; border-radius: 10px; border: 1px solid {BORDER}; }}
QFrame#sep {{ background-color: {BORDER}; max-height: 1px; min-height: 1px; }}
QLineEdit {{ background-color: {CARD2}; color: {WHITE}; border: 1px solid {BORDER}; border-radius: 6px; padding: 4px 8px; font-family: Consolas; }}
QScrollArea {{ border: none; background: {DARK}; }}
QScrollBar:vertical {{ background: {CARD}; width: 8px; border-radius: 4px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; }}
"""

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
        dest = folder / f"{name}_{c}{ext}"; c += 1
    return dest

def get_free_space(path: Path) -> int:
    try: return shutil.disk_usage(path).free
    except Exception: return float("inf")

def format_size(n: int) -> str:
    for unit in ("o", "Ko", "Mo", "Go"):
        if n < 1024: return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} To"

CONFIG_PATH           = Path.home() / "AppData" / "Local" / "osu_tool" / "config.json"
_DEFAULT_REPLAYS_DEST = Path.home() / "Desktop" / "OSU!" / "replays"
_DEFAULT_BG_DEST      = Path.home() / "Desktop" / "OSU!" / "Miniature"

def _cfg_load() -> dict:
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: pass
    return {}

def _cfg_save(data: dict):
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception: pass

class _CfgProxy:
    def load(self): return _cfg_load()
    def get(self, key, default=None): return _cfg_load().get(key, default)
    def get_replays_dest(self):
        c = _cfg_load(); return Path(c["replays_dest"]) if "replays_dest" in c else _DEFAULT_REPLAYS_DEST
    def get_bg_dest(self):
        c = _cfg_load(); return Path(c["bg_dest"]) if "bg_dest" in c else _DEFAULT_BG_DEST
    def get_shortcuts(self):
        defaults = {"scan": "F5", "send": "Return", "clean": "F6", "export": "Ctrl+S"}
        saved = _cfg_load().get("shortcuts", {})
        return {k: saved.get(k, v) for k, v in defaults.items()}
    def set_replays_dest(self, p): c = _cfg_load(); c["replays_dest"] = str(p); _cfg_save(c)
    def set_bg_dest(self, p): c = _cfg_load(); c["bg_dest"] = str(p); _cfg_save(c)
    def set_osu_path(self, p): c = _cfg_load(); c["osu_path"] = str(p); _cfg_save(c)
    def set_shortcuts(self, sc): c = _cfg_load(); c["shortcuts"] = sc; _cfg_save(c)

config = _CfgProxy()

_root: list = [None]

def detect() -> Path | None:
    c = config.load()
    if "osu_path" in c:
        p = Path(c["osu_path"])
        if p.exists() and (p / "Replays").exists(): return p
    for candidate in [Path.home() / "AppData" / "Local" / "osu!", Path("C:/Games/osu!"), Path("D:/osu!"), Path("E:/osu!")]:
        if candidate.exists() and (candidate / "Replays").exists(): return candidate
    return None

class _OsuPathProxy:
    def init(self): _root[0] = detect()
    def get(self): return _root[0]
    def set(self, path): _root[0] = path; config.set_osu_path(path)
    def get_replays_folder(self): return (_root[0] / "Replays") if _root[0] else None
    def get_songs_folder(self): return (_root[0] / "Songs") if _root[0] else None

osu_path = _OsuPathProxy()

def get_map_info(osu_file: Path) -> tuple:
    artist = title = ""; bg_path = None
    try:
        with open(osu_file, "r", encoding="utf-8", errors="ignore") as f:
            in_events = in_meta = False
            for line in f:
                s = line.strip()
                if s == "[Metadata]":   in_meta, in_events = True, False
                elif s == "[Events]":   in_events, in_meta = True, False
                elif s.startswith("["): in_meta = in_events = False
                if in_meta:
                    if s.startswith("Artist:"): artist = s.split(":", 1)[1].strip()
                    elif s.startswith("Title:"): title  = s.split(":", 1)[1].strip()
                if in_events and s.startswith('0,0,"'):
                    parts = s.split(",")
                    if len(parts) >= 3:
                        img = parts[2].strip().strip('"')
                        p = osu_file.parent / img
                        if p.exists() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp"):
                            bg_path = p
    except Exception: pass
    return bg_path, sanitize(f"{artist} - {title}" if artist and title else title or osu_file.parent.name)

def scan_replays(log, progress, seen_replays):
    folder = osu_path.get_replays_folder()
    if not folder or not folder.exists():
        log("⚠️  Replays folder not found! Set the osu! path in ⚙ Options."); progress(1.0); return []
    files = list(folder.glob("*.osr")); to_send = []; total = len(files)
    log(f"🔍 {total} replay(s) detected…")
    for i, f in enumerate(files):
        if f.name in seen_replays: log(f"  ⏩ already known: {f.name}")
        else: to_send.append(f); log(f"  📄 {f.name}")
        progress((i + 1) / total if total else 1.0)
    log(f"→ {len(to_send)} replay(s) to send\n"); return to_send

def scan_backgrounds(log, progress, status, seen_hashes, quick=False):
    folder = osu_path.get_songs_folder()
    if not folder or not folder.exists():
        log("⚠️  Songs folder not found! Set the osu! path in ⚙ Options."); progress(1.0); return []
    all_dirs = sorted({f.parent for f in folder.rglob("*.osu")})
    if quick:
        cutoff = datetime.datetime.now() - datetime.timedelta(days=7)
        dirs = [d for d in all_dirs if datetime.datetime.fromtimestamp(d.stat().st_mtime) >= cutoff]
        log(f"⚡ Quick scan: {len(dirs)}/{len(all_dirs)} recent folder(s) (7 days)…")
    else:
        dirs = all_dirs; log(f"🔍 {len(dirs)} beatmap(s) to analyze…")
    total = len(dirs); to_send = []
    for i, bdir in enumerate(dirs):
        progress((i + 1) / total if total else 1.0); status(f"Scanning map {i + 1}/{total}…")
        for osu in bdir.glob("*.osu"):
            bg, name = get_map_info(osu)
            if bg is None: continue
            h = file_hash(bg)
            if h in seen_hashes: break
            seen_hashes.add(h); to_send.append((bg, name)); log(f"  🖼️  {name}{bg.suffix}"); break
    log(f"→ {len(to_send)} background(s) to send\n"); return to_send

try:
    from win10toast import ToastNotifier
    _TOAST_OK = True
except ImportError:
    _TOAST_OK = False

try:
    import pystray
    from PIL import Image as PilImage
    _PYSTRAY_OK = True
except ImportError:
    _PYSTRAY_OK = False

def notify(title: str, msg: str, duration: int = 4):
    def _do():
        if _TOAST_OK:
            try: ToastNotifier().show_toast(title, msg, duration=duration, threaded=True); return
            except Exception: pass
        try:
            ps = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "$n=New-Object System.Windows.Forms.NotifyIcon;"
                "$n.Icon=[System.Drawing.SystemIcons]::Information;$n.Visible=$true;"
                f"$n.ShowBalloonTip({duration*1000},'{title.replace(chr(39),chr(39)*2)}','{msg.replace(chr(39),chr(39)*2)}',"
                f"[System.Windows.Forms.ToolTipIcon]::Info);Start-Sleep -Milliseconds {duration*1000+1000};$n.Dispose()"
            )
            subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps], creationflags=0x08000000)
        except Exception: pass
    threading.Thread(target=_do, daemon=True).start()

def _sep() -> QFrame:
    f = QFrame(); f.setObjectName("sep"); f.setFrameShape(QFrame.Shape.HLine); f.setFixedHeight(1); return f

def _card() -> QFrame:
    f = QFrame(); f.setObjectName("card"); return f

class Signals(QObject):
    log      = pyqtSignal(str)
    status   = pyqtSignal(str)
    progress = pyqtSignal(float)
    done     = pyqtSignal(list, list)

class ScanWorker(QThread):
    def __init__(self, do_r, do_b, quick, seen_r, seen_h):
        super().__init__()
        self.do_r = do_r; self.do_b = do_b; self.quick = quick
        self.seen_r = seen_r; self.seen_h = seen_h
        self.signals = Signals()
    def run(self):
        s = self.signals
        s.log.emit("━━━━━━━━━━━━  SCAN  ━━━━━━━━━━━━")
        if self.do_r and self.do_b:
            pr = scan_replays(s.log.emit, lambda v: s.progress.emit(v * 0.5), self.seen_r)
            pb = scan_backgrounds(s.log.emit, lambda v: s.progress.emit(0.5 + v * 0.5), s.status.emit, self.seen_h, self.quick)
        elif self.do_r:
            pr = scan_replays(s.log.emit, s.progress.emit, self.seen_r); pb = []
        else:
            pr = []; pb = scan_backgrounds(s.log.emit, s.progress.emit, s.status.emit, self.seen_h, self.quick)
        s.done.emit(pr, pb)

class SendWorker(QThread):
    def __init__(self, pending_r, pending_b):
        super().__init__()
        self.pending_r = pending_r; self.pending_b = pending_b
        self.signals = Signals(); self.seen_r_out: set = set(); self.seen_h_out: set = set()
    def run(self):
        s = self.signals; log = s.log.emit; progress = s.progress.emit; status = s.status.emit
        log("━━━━━━━━━━━━  SENDING  ━━━━━━━━━━━━"); status("Sending…")
        dest_r = config.get_replays_dest(); dest_b = config.get_bg_dest()
        total  = len(self.pending_r) + len(self.pending_b)
        for dest, label in [(dest_r, "Replays"), (dest_b, "Fonds")]:
            try:
                if dest.exists(): shutil.rmtree(dest); log(f"  🗑  {label} folder cleared.")
                dest.mkdir(parents=True, exist_ok=True); log(f"  📁  {label} folder recreated.")
            except Exception as ex: log(f"  ❌  Could not reset {label} folder: {ex}")
        needed_r = sum(f.stat().st_size for f in self.pending_r if f.exists())
        needed_b = sum(bg.stat().st_size for bg, _ in self.pending_b if bg.exists())
        free_r = get_free_space(dest_r); free_b = get_free_space(dest_b)
        same = Path(dest_r.anchor) == Path(dest_b.anchor)
        if same and (needed_r + needed_b) > free_r:
            log(f"❌  Disk full on {dest_r.anchor}!"); s.done.emit([], []); return
        elif not same:
            if self.pending_r and needed_r > free_r: log(f"❌  Disk full!"); s.done.emit([], []); return
            if self.pending_b and needed_b > free_b: log(f"❌  Disk full!"); s.done.emit([], []); return
        sent = 0
        for i, f in enumerate(self.pending_r):
            dst = unique_dest(dest_r, f.stem, f.suffix)
            try: shutil.copy2(f, dst); log(f"  ✅ {dst.name}"); self.seen_r_out.add(f.name); sent += 1
            except Exception as ex: log(f"  ❌ {f.name} — {ex}")
            progress((i + 1) / total)
        offset = len(self.pending_r)
        for i, (bg, name) in enumerate(self.pending_b):
            dst = unique_dest(dest_b, name, bg.suffix)
            try: shutil.copy2(bg, dst); log(f"  ✅ {dst.name}"); self.seen_h_out.add(file_hash(bg)); sent += 1
            except Exception as ex: log(f"  ❌ {name} — {ex}")
            progress((offset + i + 1) / total)
        errors = total - sent
        log(f"✔  {sent} file(s) sent!{(' — ⚠️ ' + str(errors) + ' error(s)') if errors else ''}")
        log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        status(f"✔  {sent} file(s) sent")
        s.done.emit(self.pending_r, self.pending_b)

class OptionsWindow(QDialog):
    def __init__(self, parent, on_forget_cb, on_shortcuts_saved_cb):
        super().__init__(parent)
        self._parent = parent; self._on_forget = on_forget_cb; self._on_sc_saved = on_shortcuts_saved_cb
        self.setWindowTitle("Options"); self.setFixedSize(520, 780); self.setStyleSheet(STYLE)
        scroll = QScrollArea(self); scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container = QWidget(); self._lay = QVBoxLayout(container)
        self._lay.setSpacing(6); self._lay.setContentsMargins(20, 16, 20, 16)
        t = QLabel("⚙  Options"); t.setStyleSheet(f"color:{PINK};font-size:18px;font-weight:bold;")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter); self._lay.addWidget(t); self._lay.addWidget(_sep())
        self._build(); self._lay.addStretch()
        scroll.setWidget(container)
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0); outer.addWidget(scroll)

    def _section(self, title):
        f = _card(); v = QVBoxLayout(f); v.setContentsMargins(12, 10, 12, 10); v.setSpacing(4)
        l = QLabel(title); l.setStyleSheet(f"color:{WHITE};font-size:12px;font-weight:bold;")
        v.addWidget(l); self._lay.addWidget(f); return f

    def _build(self):
        f_osu = self._section("🎮  osu! folder (source)")
        cur = str(osu_path.get()) if osu_path.get() else "Not configured"
        self._osu_lbl = QLabel(cur); self._osu_lbl.setStyleSheet(f"color:{DIM};font-family:Consolas;font-size:10px;"); self._osu_lbl.setWordWrap(True)
        f_osu.layout().addWidget(self._osu_lbl)
        b = QPushButton("📁  Browse…"); b.clicked.connect(self._browse_osu); f_osu.layout().addWidget(b)
        self._lay.addWidget(_sep())

        f_r = self._section("📄  Destination — Replays")
        self._lbl_r = QLabel(str(config.get_replays_dest())); self._lbl_r.setStyleSheet(f"color:{DIM};font-family:Consolas;font-size:10px;"); self._lbl_r.setWordWrap(True)
        f_r.layout().addWidget(self._lbl_r)
        br = QPushButton("📁  Browse…"); br.clicked.connect(lambda: self._browse_dest("replays_dest", self._lbl_r, "Replays")); f_r.layout().addWidget(br)

        f_b = self._section("🖼️  Destination — Backgrounds")
        self._lbl_b = QLabel(str(config.get_bg_dest())); self._lbl_b.setStyleSheet(f"color:{DIM};font-family:Consolas;font-size:10px;"); self._lbl_b.setWordWrap(True)
        f_b.layout().addWidget(self._lbl_b)
        bb = QPushButton("📁  Browse…"); bb.clicked.connect(lambda: self._browse_dest("bg_dest", self._lbl_b, "Fonds")); f_b.layout().addWidget(bb)
        self._lay.addWidget(_sep())

        f_k = self._section("⌨️  Keyboard shortcuts")
        sc = config.get_shortcuts()
        self._sc_fields: dict[str, QLineEdit] = {}
        grid = QGridLayout(); grid.setContentsMargins(8, 4, 8, 4)
        for i, (key, label, default) in enumerate([("scan","Scan","F5"),("send","Send","Return"),("clean","Auto-Cleanup","F6"),("export","Export log","Ctrl+S")]):
            lbl = QLabel(label); lbl.setStyleSheet(f"color:{DIM};font-size:11px;")
            entry = QLineEdit(sc.get(key, default)); entry.setFixedWidth(140)
            self._sc_fields[key] = entry
            grid.addWidget(lbl, i, 0); grid.addWidget(entry, i, 1)
        f_k.layout().addLayout(grid)
        bs = QPushButton("💾  Save shortcuts"); bs.clicked.connect(self._save_sc); f_k.layout().addWidget(bs)
        self._lay.addWidget(_sep())

        bf = QPushButton("🗑  Forget all  (reset memory)")
        bf.setStyleSheet(f"QPushButton{{background:{CARD};color:{ORANGE};border:1px solid {ORANGE};border-radius:10px;padding:8px;}}QPushButton:hover{{background:#332200;}}")
        bf.clicked.connect(lambda: [self._on_forget(), self.accept()]); self._lay.addWidget(bf)

    def _browse_osu(self):
        folder = QFileDialog.getExistingDirectory(self, "Select osu! folder", str(Path.home()))
        if folder:
            p = Path(folder)
            if (p / "Replays").exists():
                osu_path.set(p); self._osu_lbl.setText(str(p))
                self._parent.log(f"✔  osu! path configured: {p}"); self._parent.set_status("osu! path updated. Run a scan.")
            else:
                self._parent.log(f"⚠️  No 'Replays' subfolder found in: {p}")

    def _browse_dest(self, key, lbl, label):
        current = config.get_replays_dest() if key == "replays_dest" else config.get_bg_dest()
        folder = QFileDialog.getExistingDirectory(self, f"Destination for {label}", str(current))
        if folder:
            p = Path(folder)
            (config.set_replays_dest if key == "replays_dest" else config.set_bg_dest)(p)
            lbl.setText(str(p)); self._parent.log(f"✔  {label} destination updated: {p}")

    def _save_sc(self):
        config.set_shortcuts({k: v.text() for k, v in self._sc_fields.items()})
        self._on_sc_saved(); self._parent.log("✔  Shortcuts saved."); self.accept()

class App(QMainWindow):
    VERSION = "v0.1-alpha"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("osu! Tool")
        self.setMinimumSize(500, 600)
        self.resize(660, 820)
        self.setStyleSheet(STYLE)
        try:
            ico_data = base64.b64decode(ICO_B64)
            ico_img = QImage.fromData(ico_data)
            self.setWindowIcon(QIcon(QPixmap.fromImage(ico_img)))
        except Exception:
            pass
        self._seen_replays: set = set(); self._seen_hashes: set = set()
        self._pending_r: list = []; self._pending_b: list = []
        self._last_dest: Path | None = None; self._tray_icon = None; self._log_entries: list = []
        self._build(); osu_path.init(); self._check_osu_path(); self._setup_shortcuts()

    def _build(self):
        root = QWidget(); self.setCentralWidget(root)
        m = QVBoxLayout(root); m.setContentsMargins(24, 16, 24, 16); m.setSpacing(8)

        # Header
        h = QHBoxLayout()
        try:
            data = base64.b64decode(LOGO_B64)
            qimg = QImage.fromData(data)
            pix = QPixmap.fromImage(qimg).scaled(44, 44, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            ll = QLabel(); ll.setPixmap(pix); ll.setFixedSize(48, 48); h.addWidget(ll)
        except Exception: pass
        tl = QLabel("osu! Tool"); tl.setStyleSheet(f"color:{PINK};font-size:26px;font-weight:bold;"); h.addWidget(tl)
        vl = QLabel(self.VERSION); vl.setStyleSheet(f"color:{DIM};font-size:10px;"); h.addWidget(vl)
        h.addStretch()
        self.btn_options = QPushButton("⚙"); self.btn_options.setFixedSize(36, 36); self.btn_options.clicked.connect(self._open_options); h.addWidget(self.btn_options)
        m.addLayout(h); m.addWidget(_sep())

        # Cards
        cr = QHBoxLayout(); cr.setSpacing(12)
        for attr, txt, sub in [("chk_r", "📄  Replays (.osr)", "Copies replay files to your folder."),
                                ("chk_b", "🖼️  Fonds d'écran",  "Extracts backgrounds from beatmaps.")]:
            f = _card(); v = QVBoxLayout(f); v.setContentsMargins(14, 12, 14, 12)
            chk = QCheckBox(txt); chk.setChecked(True); setattr(self, attr, chk)
            sl = QLabel(sub); sl.setStyleSheet(f"color:{DIM};font-size:10px;font-weight:normal;")
            v.addWidget(chk); v.addWidget(sl); cr.addWidget(f)
        m.addLayout(cr)

        self.chk_quick = QCheckBox("⚡ Quick scan (beatmaps from the last 7 days)")
        self.chk_quick.setObjectName("dim"); m.addWidget(self.chk_quick)

        self.btn_scan = QPushButton("🔍  Scan"); self.btn_scan.setObjectName("primary"); self.btn_scan.setFixedHeight(44); self.btn_scan.clicked.connect(self._on_scan); m.addWidget(self.btn_scan)
        self.btn_send = QPushButton("➤  Send"); self.btn_send.setObjectName("primary"); self.btn_send.setFixedHeight(44); self.btn_send.setEnabled(False); self.btn_send.clicked.connect(self._on_send); m.addWidget(self.btn_send)

        self.bar = QProgressBar(); self.bar.setRange(0, 1000); self.bar.setValue(0); self.bar.setTextVisible(False); self.bar.setFixedHeight(8); m.addWidget(self.bar)

        self.logbox = QTextEdit(); self.logbox.setReadOnly(True); self.logbox.setMinimumHeight(120); m.addWidget(self.logbox, stretch=1)

        self.btn_open_dest = QPushButton("📂  Open destination folder"); self.btn_open_dest.setEnabled(False); self.btn_open_dest.clicked.connect(self._open_dest_folder); m.addWidget(self.btn_open_dest)
        self.btn_clean = QPushButton("🧹  Auto-Cleanup (orphan backgrounds)"); self.btn_clean.clicked.connect(self._on_clean); m.addWidget(self.btn_clean)

        br = QHBoxLayout()
        self.btn_export = QPushButton("💾  Export log"); self.btn_export.clicked.connect(self._on_export_log); br.addWidget(self.btn_export)
        self.btn_tray = QPushButton("🗕  Minimize to tray"); self.btn_tray.setEnabled(_PYSTRAY_OK); self.btn_tray.clicked.connect(self._minimize_to_tray); br.addWidget(self.btn_tray)
        m.addLayout(br)

        self.lbl_status = QLabel("Run a scan to get started.")
        self.lbl_status.setStyleSheet(f"color:{DIM};font-size:11px;"); self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter); m.addWidget(self.lbl_status)

    def log(self, msg: str):
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        self._log_entries.append({"ts": ts, "msg": msg}); self.logbox.append(msg)

    def set_status(self, t: str): self.lbl_status.setText(t)
    def set_progress(self, v: float): self.bar.setValue(int(v * 1000))

    def _set_send_ready(self, n: int):
        self.btn_send.setEnabled(n > 0)
        self.btn_send.setText(f"➤  Send  ({n} file{'s' if n > 1 else ''})" if n > 0 else "➤  Send")

    def _setup_shortcuts(self):
        sc = config.get_shortcuts()
        for key, fn in [(sc.get("scan","F5"), self._on_scan), (sc.get("send","Return"), self._on_send),
                        (sc.get("clean","F6"), self._on_clean), (sc.get("export","Ctrl+S"), self._on_export_log)]:
            try: QShortcut(QKeySequence(key), self).activated.connect(fn)
            except Exception: pass

    def _on_scan(self):
        if not self.chk_r.isChecked() and not self.chk_b.isChecked():
            self.log("⚠️  Select at least one option!"); return
        self.btn_scan.setEnabled(False); self._set_send_ready(0); self.bar.setValue(0)
        self._pending_r = []; self._pending_b = []; self.set_status("Scanning…")
        self._scan_w = ScanWorker(self.chk_r.isChecked(), self.chk_b.isChecked(), self.chk_quick.isChecked(), set(self._seen_replays), set(self._seen_hashes))
        w = self._scan_w; w.signals.log.connect(self.log); w.signals.status.connect(self.set_status); w.signals.progress.connect(self.set_progress); w.signals.done.connect(self._scan_done); w.start()

    def _scan_done(self, pr, pb):
        self._pending_r = pr; self._pending_b = pb; total = len(pr) + len(pb)
        if total > 0:
            self.log(f"✔  Scan complete — {total} file(s) ready to send."); self.set_status(f"Scan complete — {total} file(s) ready")
        else:
            self.log("✔  Everything is already up to date."); self.set_status("Already up to date ✓")
        self._set_send_ready(total); self.btn_scan.setEnabled(True)

    def _on_send(self):
        if not self._pending_r and not self._pending_b: return
        self.btn_scan.setEnabled(False); self._set_send_ready(0); self.bar.setValue(0)
        self._send_w = SendWorker(self._pending_r[:], self._pending_b[:])
        w = self._send_w; w.signals.log.connect(self.log); w.signals.status.connect(self.set_status); w.signals.progress.connect(self.set_progress); w.signals.done.connect(self._send_done); w.start()

    def _send_done(self, sent_r, sent_b):
        w = self._send_w
        self._seen_replays.update(w.seen_r_out); self._seen_hashes.update(w.seen_h_out)
        self._pending_r = []; self._pending_b = []; self.btn_scan.setEnabled(True)
        if sent_r or sent_b:
            self._last_dest = config.get_replays_dest().parent if sent_r and sent_b else (config.get_replays_dest() if sent_r else config.get_bg_dest())
            self.btn_open_dest.setEnabled(True)
        notify("osu! Tool", f"{len(sent_r) + len(sent_b)} file(s) copied")

    def _on_clean(self):
        sf = osu_path.get_songs_folder(); bd = config.get_bg_dest()
        if not sf or not sf.exists(): self.log("⚠️  Songs folder not found."); return
        if not bd.exists(): self.log("⚠️  Backgrounds folder not found."); return
        def task():
            self.log("━━━━━━━━━  CLEANUP  ━━━━━━━━━"); self.set_status("Analyzing…")
            osu_h: set = set(); dirs = sorted({f.parent for f in sf.rglob("*.osu")})
            for i, bdir in enumerate(dirs):
                self.set_status(f"Analyzing map {i+1}/{len(dirs)}…")
                for osu in bdir.glob("*.osu"):
                    bg, _ = get_map_info(osu)
                    if bg: osu_h.add(file_hash(bg))
                    break
            exts = {".jpg", ".jpeg", ".png", ".bmp"}
            orphans = [f for f in bd.iterdir() if f.suffix.lower() in exts and file_hash(f) not in osu_h]
            if not orphans: self.log("✔  No orphaned files!"); self.set_status("Cleanup: nothing to remove ✓"); return
            self.log(f"⚠️  {len(orphans)} orphaned file(s):")
            for f in orphans: self.log(f"  🗑  {f.name}")
            ans = QMessageBox.question(self, "Confirm deletion", f"Delete {len(orphans)} orphaned file(s)?\n\nFolder: {bd}\n\nThis action is irreversible.")
            if ans == QMessageBox.StandardButton.Yes:
                deleted = 0
                for f in orphans:
                    try: f.unlink(); self.log(f"  ✅ Deleted: {f.name}"); deleted += 1
                    except Exception as ex: self.log(f"  ❌ {f.name} — {ex}")
                self.log(f"✔  {deleted} file(s) deleted."); self.set_status(f"Cleanup done — {deleted} deleted")
            else: self.log("↩  Cleanup cancelled."); self.set_status("Cleanup cancelled.")
        threading.Thread(target=task, daemon=True).start()

    def _open_options(self):
        OptionsWindow(self, self._forget_all, self._setup_shortcuts).exec()

    def _forget_all(self):
        self._seen_replays.clear(); self._seen_hashes.clear(); self._pending_r = []; self._pending_b = []
        self._set_send_ready(0); self.bar.setValue(0)
        self.log("🗑  Memory reset — next scan starts fresh."); self.set_status("Memory cleared. Run a new scan.")

    def _check_osu_path(self):
        if osu_path.get() is None:
            self.log("⚠️  osu! folder not found automatically.")
            self.log("   Use ⚙ Options → Locate osu! to configure it.")
            self.set_status("⚠️  osu! not found — set the path in ⚙ Options")
        else:
            src = "saved config" if "osu_path" in config.load() else "auto-detected"
            self.log(f"✔  osu! detected ({src}): {osu_path.get()}"); self.set_status("Run a scan to get started.")

    def _open_dest_folder(self):
        dest = self._last_dest or config.get_replays_dest().parent
        dest.mkdir(parents=True, exist_ok=True)
        try: subprocess.Popen(["explorer", str(dest)])
        except Exception:
            try: os.startfile(str(dest))
            except Exception as ex: self.log(f"⚠️  Cannot open folder: {ex}")

    def _on_export_log(self):
        if not self._log_entries: self.log("⚠️  Log is empty."); return
        folder = QFileDialog.getExistingDirectory(self, "Choose export folder", str(Path.home() / "Desktop"))
        if not folder: return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S"); base = Path(folder) / f"osu_tool_log_{ts}"
        try:
            with open(base.with_suffix(".txt"), "w", encoding="utf-8") as f:
                for e in self._log_entries: f.write(f"[{e['ts']}] {e['msg']}\n")
            self.log(f"✔  Log .txt: {base.with_suffix('.txt').name}")
        except Exception as ex: self.log(f"❌  Export error .txt: {ex}")
        try:
            with open(base.with_suffix(".json"), "w", encoding="utf-8") as f:
                json.dump({"exported_at": datetime.datetime.now().isoformat(), "entries": self._log_entries}, f, indent=2, ensure_ascii=False)
            self.log(f"✔  Log .json: {base.with_suffix('.json').name}")
        except Exception as ex: self.log(f"❌  Export error .json: {ex}")

    def _minimize_to_tray(self):
        if not _PYSTRAY_OK: self.log("⚠️  pystray not installed."); return
        if self._tray_icon: return
        self.hide()
        try:
            img_data = base64.b64decode(LOGO_B64)
            tray_img = PilImage.open(io.BytesIO(img_data)).resize((64, 64), PilImage.LANCZOS).convert("RGBA")
        except Exception:
            tray_img = PilImage.new("RGBA", (64, 64), (255, 102, 170, 255))
        def _restore(icon, _): icon.stop(); self._tray_icon = None; self.show()
        menu = pystray.Menu(pystray.MenuItem("🎵  Show osu! Tool", _restore, default=True),
                            pystray.MenuItem("❌  Quit", lambda icon, _: [icon.stop(), QApplication.quit()]))
        self._tray_icon = pystray.Icon("osu_tool", tray_img, "osu! Tool", menu)
        threading.Thread(target=self._tray_icon.run, daemon=True).start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = App()
    window.show()
    sys.exit(app.exec())