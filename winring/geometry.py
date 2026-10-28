"""Hitung-hitungan roda (tanpa Qt / Windows supaya mudah diuji)."""
import math

PAGE_SIZE = 12


def slot_at(dx: float, dy: float, n: int, dead_radius: float) -> int:
    """Slot mana yang ditunjuk oleh vektor (dx, dy) dari pusat roda.

    Slot 0 berada di atas, urutan searah jarum jam. Mengembalikan -1 bila
    kursor berada di zona tengah (dead zone) atau tidak ada slot.
    """
    if n <= 0 or math.hypot(dx, dy) < dead_radius:
        return -1
    angle = math.atan2(dx, -dy)  # 0 = atas, positif = searah jarum jam
    step = 2 * math.pi / n
    return int(((angle + step / 2) % (2 * math.pi)) // step) % n


def slot_center(i: int, n: int, radius: float):
    """Posisi tengah slot i relatif ke pusat roda."""
    a = 2 * math.pi * i / max(n, 1)
    return radius * math.sin(a), -radius * math.cos(a)


def page_count(total: int, page_size: int = PAGE_SIZE) -> int:
    return max(1, math.ceil(total / page_size))


def page_slice(items, page: int, page_size: int = PAGE_SIZE):
    return items[page * page_size:(page + 1) * page_size]
