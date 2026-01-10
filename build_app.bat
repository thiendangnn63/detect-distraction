@echo off
echo --- HAWKEYE BUILDER ---
echo.

cd /d "%~dp0"

echo Creating virtual environment for Python 3.12
py -3.12 -m venv venv

call venv\Scripts\activate
echo Installing required libraries
pip install -r required/requirements.txt

echo.
echo Building .exe file...
echo This might take a minute. Please wait.
pyinstaller --onefile --noconsole --name "Hawkeye" --collect-all mediapipe --add-data "required/face_landmarker.task;." iris_tracking.py

echo.
echo Cleaning up build folders...
rmdir /s /q build
del /q Hawkeye.spec

echo.
echo ========================================================
echo SUCCESS! Your app is in the "dist" folder.
echo ========================================================
pause