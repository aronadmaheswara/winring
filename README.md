# WinRing

Menu radial untuk berpindah antar window di Windows 10/11 – seperti taskbar, tapi berbentuk roda.

**Cara pakai:** tahan hotkey (default `Alt+Q`) → roda muncul di kursor, berisi ikon semua window yang terbuka →
arahkan mouse ke salah satu slot → lepas tombol → window itu maju ke depan (dipulihkan bila diminimalkan).
`Esc` atau klik kanan = batal. Scroll mouse = ganti halaman (12 window per halaman).

## Menjalankan
```
pip install PySide6
pythonw winring.pyw
```
Aplikasi berjalan di system tray (klik ikon untuk Pengaturan: hotkey, urutan, tema, ukuran, transparansi, autostart).

## Build .exe
```
powershell -ExecutionPolicy Bypass -File build.ps1
```

## Struktur
- `winring/winapi.py` – daftar window & aktivasi (ctypes, tanpa pywin32)
- `winring/hotkey.py` – hook keyboard global (tahan/lepas)
- `winring/wheel.py` – gambar roda & overlay
- `winring/settings_dialog.py`, `winring/config.py` – pengaturan
- `winring/geometry.py` – hit-test slot (ada tes: `python tests_geometry.py`)

Catatan: window yang berjalan sebagai Administrator tidak bisa dibawa ke depan dari WinRing
kecuali WinRing juga dijalankan sebagai Administrator.
