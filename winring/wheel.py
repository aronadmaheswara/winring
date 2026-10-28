"""Tampilan roda: WheelCanvas (menggambar) dan WheelOverlay (jendela melayang di kursor)."""
import math
from dataclasses import dataclass, field

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, QVariantAnimation, Signal
from PySide6.QtGui import (QColor, QCursor, QFont, QFontMetrics, QGuiApplication, QIcon,
                           QPainter, QPainterPath, QPen, QPixmap)
from PySide6.QtWidgets import QWidget

from . import geometry as geo
from .config import THEMES

R_OUT, R_IN, ICON, PAD = 168, 72, 40, 26     # ukuran dasar (px, skala 100%)


@dataclass
class WheelItem:
    title: str
    subtitle: str = ""
    icon: QIcon = field(default_factory=QIcon)
    payload: object = None                     # mis. hwnd


class WheelCanvas(QWidget):
    """Menggambar roda. Dipakai langsung untuk pratinjau di pengaturan."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: list[WheelItem] = []
        self.page = 0
        self.hover = -1                 # indeks pada halaman aktif
        self.scale = 1.0
        self.theme = THEMES["Midnight"]
        self.opacity = 0.94
        self.show_subtitle = True
        self._pop = 1.0
        self._pop_anim = QVariantAnimation(self, duration=120, startValue=0.0, endValue=1.0)
        self._pop_anim.valueChanged.connect(self._on_pop)
        self.setAttribute(Qt.WA_TranslucentBackground)

    # --- data ---
    def set_style(self, theme_name: str, size_percent: int, opacity_percent: int, show_subtitle=True):
        self.theme = THEMES.get(theme_name, THEMES["Midnight"])
        self.scale = size_percent / 100
        self.opacity = opacity_percent / 100
        self.show_subtitle = show_subtitle
        side = self.side()
        self.setFixedSize(side, side)
        self.update()

    def side(self) -> int:
        return int(2 * (R_OUT + PAD) * self.scale)

    def page_items(self):
        return geo.page_slice(self.items, self.page)

    def pages(self) -> int:
        return geo.page_count(len(self.items))

    def hovered_item(self) -> WheelItem | None:
        p = self.page_items()
        return p[self.hover] if 0 <= self.hover < len(p) else None

    def set_hover(self, i: int):
        if i != self.hover:
            self.hover = i
            self._pop_anim.stop()
            self._pop_anim.start()
            self.update()

    def _on_pop(self, v):
        self._pop = float(v)
        self.update()

    # --- gambar ---
    def _sector(self, c: QPointF, i: int, n: int, r_in: float, r_out: float) -> QPainterPath:
        step = 360 / n
        gap = 2.4 if n > 1 else 0.0
        a0 = 90 - i * step + (step - gap) / 2
        sweep = step - gap if n > 1 else 359.99
        outer = QRectF(c.x() - r_out, c.y() - r_out, 2 * r_out, 2 * r_out)
        inner = QRectF(c.x() - r_in, c.y() - r_in, 2 * r_in, 2 * r_in)
        p = QPainterPath()
        p.arcMoveTo(outer, a0)
        p.arcTo(outer, a0, -sweep)
        p.arcTo(inner, a0 - sweep, sweep)
        p.closeSubpath()
        return p

    def paintEvent(self, _):
        t, s = self.theme, self.scale
        g = QPainter(self)
        g.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        c = QPointF(self.width() / 2, self.height() / 2)
        r_out, r_in = R_OUT * s, R_IN * s
        ring, slot, accent = QColor(t["ring"]), QColor(t["slot"]), QColor(t["accent"])
        text, sub = QColor(t["text"]), QColor(t["sub"])
        ring.setAlphaF(self.opacity)
        slot.setAlphaF(min(1.0, self.opacity + 0.04))

        # bayangan lembut + piringan dasar
        for k in range(8, 0, -1):
            sh = QColor(0, 0, 0, 7)
            g.setPen(Qt.NoPen); g.setBrush(sh)
            rr = r_out + k * 2.2 * s
            g.drawEllipse(c + QPointF(0, 3 * s), rr, rr)
        g.setBrush(ring)
        g.drawEllipse(c, r_out + 5 * s, r_out + 5 * s)

        items = self.page_items()
        n = len(items)
        mid = (r_in + r_out) / 2
        for i, it in enumerate(items):
            hot = i == self.hover
            grow = 4 * s * self._pop if hot else 0
            path = self._sector(c, i, n, r_in + 6 * s - grow * 0.3, r_out - 2 * s + grow)
            if hot:
                col = QColor(accent); col.setAlphaF(0.92)
            else:
                col = slot
            g.setPen(Qt.NoPen); g.setBrush(col)
            g.drawPath(path)

            sx, sy = geo.slot_center(i, n, mid)
            px = ICON * s * (1.0 + 0.16 * self._pop if hot else 1.0)
            r = QRectF(c.x() + sx - px / 2, c.y() + sy - px / 2, px, px)
            pm = it.icon.pixmap(int(px * 2), int(px * 2)) if not it.icon.isNull() else QPixmap()
            if pm.isNull():
                g.setBrush(QColor(255, 255, 255, 40)); g.drawRoundedRect(r, 8 * s, 8 * s)
                g.setPen(text); g.setFont(QFont("Segoe UI", int(15 * s), QFont.Bold))
                g.drawText(r, Qt.AlignCenter, (it.title[:1] or "?").upper())
            else:
                g.drawPixmap(r, pm, QRectF(pm.rect()))

        self._paint_center(g, c, r_in, text, sub, accent, items)

    def _paint_center(self, g, c, r_in, text, sub, accent, items):
        s = self.scale
        disc = QColor(self.theme["ring"]); disc.setAlphaF(self.opacity)
        g.setPen(Qt.NoPen); g.setBrush(disc)
        g.drawEllipse(c, r_in - 2 * s, r_in - 2 * s)
        w = (r_in - 8 * s) * 1.7
        box = QRectF(c.x() - w / 2, c.y() - r_in * 0.62, w, r_in * 1.24)

        it = self.hovered_item()
        if not items:
            title, subtitle = "Tidak ada window", ""
        elif it:
            title, subtitle = it.title, (it.subtitle if self.show_subtitle else "")
        else:
            title, subtitle = f"{len(self.items)} window", "Arahkan ke slot, lalu lepas"

        tf = QFont("Segoe UI", max(7, int(10.5 * s)), QFont.DemiBold)
        sf = QFont("Segoe UI", max(6, int(8.5 * s)))
        fm = QFontMetrics(tf)
        title = _clip_lines(title, fm, int(w), 3)
        sfm = QFontMetrics(sf)
        sub_h = sfm.height() if subtitle else 0
        th = fm.boundingRect(0, 0, int(w), 999, Qt.TextWordWrap, title).height()
        y = box.center().y() - (th + sub_h) / 2
        g.setFont(tf); g.setPen(text)
        g.drawText(QRectF(box.x(), y, w, th), Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap, title)
        if subtitle:
            g.setFont(sf); g.setPen(accent if it else sub)
            g.drawText(QRectF(box.x(), y + th + 2, w, sub_h + 2), Qt.AlignHCenter | Qt.AlignTop,
                       sfm.elidedText(subtitle, Qt.ElideRight, int(w)))

        pages = self.pages()
        if pages > 1:                       # titik indikator halaman
            d, gap = 5 * s, 9 * s
            x0 = c.x() - (pages - 1) * gap / 2
            yy = c.y() + r_in * 0.78
            for k in range(pages):
                g.setBrush(accent if k == self.page else sub)
                g.drawEllipse(QPointF(x0 + k * gap, yy), d / 2, d / 2)


def _clip_lines(text: str, fm: QFontMetrics, width: int, max_lines: int) -> str:
    """Potong teks supaya muat max_lines baris, tambah … bila terpotong."""
    lim = max_lines * max(1, width // max(1, fm.averageCharWidth()))
    if len(text) > lim:
        text = text[:max(1, lim - 1)].rstrip() + "…"
    return text


class WheelOverlay(WheelCanvas):
    """Jendela melayang tanpa fokus yang muncul di kursor dan melacak arah mouse."""
    cancel_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |
                            Qt.WindowDoesNotAcceptFocus | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setMouseTracking(True)
        self._timer = QTimer(self, interval=16)
        self._timer.timeout.connect(self._track)
        self._fade = QVariantAnimation(self, duration=110, startValue=0.0, endValue=1.0)
        self._fade.valueChanged.connect(lambda v: self.setWindowOpacity(float(v)))

    def open_at_cursor(self, items: list[WheelItem]):
        self.items, self.page, self.hover = items, 0, -1
        side = self.side()
        pos = QCursor.pos()
        screen = QGuiApplication.screenAt(pos) or QGuiApplication.primaryScreen()
        a = screen.availableGeometry()
        cx = min(max(pos.x(), a.left() + side // 2), a.right() - side // 2)
        cy = min(max(pos.y(), a.top() + side // 2), a.bottom() - side // 2)
        if (cx, cy) != (pos.x(), pos.y()):
            QCursor.setPos(cx, cy)          # selalu mulai dari pusat roda
        self.move(cx - side // 2, cy - side // 2)
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self._fade.start()
        self._timer.start()

    def close_wheel(self):
        self._timer.stop()
        self.hide()

    def _track(self):
        p = QCursor.pos() - self.mapToGlobal(self.rect().center())
        n = len(self.page_items())
        self.set_hover(geo.slot_at(p.x(), p.y(), n, (R_IN - 6) * self.scale))

    def wheelEvent(self, e):
        pages = self.pages()
        if pages > 1:
            self.page = (self.page + (-1 if e.angleDelta().y() > 0 else 1)) % pages
            self.hover = -1
            self._track()
            self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.cancel_requested.emit()
