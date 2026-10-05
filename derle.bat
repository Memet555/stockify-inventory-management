@echo off
chcp 65001 > nul
echo ======================================================
echo          Stockify .EXE Derleme Sihirbazi
echo ======================================================
echo.
echo 1. Adim: Sanal Ortam Aktiflestiriliyor...
call venv\Scripts\activate.bat

echo.
echo 2. Adim: PyInstaller Yukleniyor...
pip install pyinstaller

echo.
echo 3. Adim: Derleme Basliyor (1-2 Dakika Surebilir)...
pyinstaller --clean --noconsole --onefile --add-data "database/schema.sql;database" app.py

echo.
echo ======================================================
echo               Derleme Islemi Tamamlandi!
echo ======================================================
echo.
echo Bağımsız programınız "dist" klasörü içindedir.
echo.
pause
