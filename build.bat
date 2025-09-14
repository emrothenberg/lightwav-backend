@echo off
call win-venv\Scripts\activate.bat
echo Activated venv
pyinstaller lightwav.exe.spec
echo Created exe
