from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel,
                               QPushButton, QSlider, QVBoxLayout, QWidget)

from . import config as C
from .wheel import WheelCanvas, WheelItem

_SAMPLE = [("Browser", "#4f8cff"), ("Editor", "#34c38f"), ("Chat", "#f59e0b"), ("Mail", "#ef5da8"),
           ("Music", "#a78bfa"), ("Files", "#fbbf24"), ("Terminal", "#94a3b8"), ("Notes", "#fb7185")]


def _sample_items():
    out = []
    for name, col in _SAMPLE:
        pm = QPixmap(64, 64); pm.fill(Qt.transparent)
        p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(col)); p.setPen(Qt.NoPen); p.drawRoundedRect(4, 4, 56, 56, 14, 14)
        p.setPen(Qt.white); p.setFont(QFont("Segoe UI", 24, QFont.Bold))
        p.drawText(pm.rect(), Qt.AlignCenter, name[0]); p.end()
        out.append(WheelItem(name, "contoh.exe", QIcon(pm)))
    return out


class HotkeyButton(QPushButton):
    changed = Signal(int, int)

    def __init__(self, mods, vk):
        super().__init__()
        self.mods, self.vk, self._rec = mods, vk, False
        self._refresh()
        self.clicked.connect(self._start)

    def _refresh(self):
        self.setText("Tekan kombinasi tombol…" if self._rec else C.hotkey_text(self.mods, self.vk))

    def _start(self):
        self._rec = True; self._refresh(); self.setFocus()

    def event(self, e):
        if self._rec and e.type() == e.Type.ShortcutOverride:
            e.accept(); return True
        return super().event(e)

    def focusOutEvent(self, e):
        self._rec = False; self._refresh(); super().focusOutEvent(e)

    def keyPressEvent(self, e):
        if not self._rec:
            return super().keyPressEvent(e)
        if e.key() == Qt.Key_Escape:
            self._rec = False; self._refresh(); return
        if e.key() in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta, Qt.Key_AltGr):
            return
        m = e.modifiers()
        mods = ((C.MOD_ALT if m & Qt.AltModifier else 0) | (C.MOD_CTRL if m & Qt.ControlModifier else 0) |
                (C.MOD_SHIFT if m & Qt.ShiftModifier else 0) | (C.MOD_WIN if m & Qt.MetaModifier else 0))
        vk = e.nativeVirtualKey()
        if not mods or not vk:
            return          # wajib memakai minimal satu modifier
        self.mods, self.vk, self._rec = mods, vk, False
        self._refresh(); self.changed.emit(mods, vk)


class SettingsDialog(QDialog):
    applied = Signal(dict)

    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("WinRing – Pengaturan")
        self.cfg = dict(cfg)

        self.hotkey = HotkeyButton(cfg["mods"], cfg["vk"])
        self.sort = QComboBox(); self.sort.addItem("Terakhir dipakai", "recent"); self.sort.addItem("Alfabet", "alpha")
        self.sort.setCurrentIndex(0 if cfg["sort"] == "recent" else 1)
        self.theme = QComboBox(); self.theme.addItems(list(C.THEMES)); self.theme.setCurrentText(cfg["theme"])
        self.size = self._slider(70, 140, cfg["size"])
        self.opacity = self._slider(60, 100, cfg["opacity"])
        self.proc = QCheckBox("Tampilkan nama program di tengah roda"); self.proc.setChecked(cfg["show_process"])
        self.auto = QCheckBox("Jalankan saat Windows start"); self.auto.setChecked(cfg["autostart"])

        form = QFormLayout()
        form.addRow("Hotkey (tahan)", self.hotkey)
        form.addRow("Urutan window", self.sort)
        form.addRow("Tema", self.theme)
        form.addRow("Ukuran", self.size[1])
        form.addRow("Transparansi", self.opacity[1])
        form.addRow("", self.proc)
        form.addRow("", self.auto)

        self.preview = WheelCanvas()
        self.preview.items = _sample_items()
        self.preview.hover = 1
        left = QVBoxLayout(); left.addLayout(form); left.addStretch()
        top = QHBoxLayout(); top.addLayout(left); top.addWidget(self.preview, 0, Qt.AlignCenter)

        ok = QPushButton("Simpan"); ok.setDefault(True); ok.clicked.connect(self._save)
        cancel = QPushButton("Batal"); cancel.clicked.connect(self.reject)
        btns = QHBoxLayout(); btns.addStretch(); btns.addWidget(cancel); btns.addWidget(ok)
        hint = QLabel("Tahan hotkey → arahkan mouse ke window → lepas untuk berpindah. "
                      "Esc / klik kanan membatalkan. Scroll untuk ganti halaman bila window > 12.")
        hint.setWordWrap(True); hint.setStyleSheet("color: gray")
        root = QVBoxLayout(self); root.addLayout(top); root.addWidget(hint); root.addLayout(btns)

        for wdg in (self.theme,):
            wdg.currentTextChanged.connect(self._update_preview)
        for s, _ in (self.size, self.opacity):
            s.valueChanged.connect(self._update_preview)
        self.proc.toggled.connect(self._update_preview)
        self._update_preview()

    def _slider(self, lo, hi, val):
        s = QSlider(Qt.Horizontal); s.setRange(lo, hi); s.setValue(val)
        lab = QLabel(f"{val}%"); s.valueChanged.connect(lambda v: lab.setText(f"{v}%"))
        box = QWidget(); l = QHBoxLayout(box); l.setContentsMargins(0, 0, 0, 0); l.addWidget(s); l.addWidget(lab)
        return s, box

    def _update_preview(self, *_):
        self.preview.set_style(self.theme.currentText(), int(self.size[0].value() * 0.6),
                               self.opacity[0].value(), self.proc.isChecked())

    def _save(self):
        self.cfg.update(mods=self.hotkey.mods, vk=self.hotkey.vk, sort=self.sort.currentData(),
                        theme=self.theme.currentText(), size=self.size[0].value(),
                        opacity=self.opacity[0].value(), show_process=self.proc.isChecked(),
                        autostart=self.auto.isChecked())
        self.applied.emit(self.cfg)
        self.accept()
