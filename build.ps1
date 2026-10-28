# Build WinRing.exe (jalankan di Windows, dari folder proyek)
python -m pip install -r requirements.txt
python -m PyInstaller --noconsole --onefile --name WinRing winring.pyw
Write-Host "Selesai: dist\WinRing.exe"
