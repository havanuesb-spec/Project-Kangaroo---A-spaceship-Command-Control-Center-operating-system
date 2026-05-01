@echo off
REM Run Project: Kangaroo on Windows 10
REM Usage: double-click or run from cmd: run_windows.bat

SET ROOT=%~dp0
nIF NOT "%ROOT%"=="" (
) 
cd /d "%~dp0"

IF NOT EXIST "%ROOT%.venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv "%ROOT%.venv"
)

necho Activating virtual environment...
call "%ROOT%.venv\Scripts\activate.bat"

necho Installing requirements (if present)...
IF EXIST "%ROOT%requirements.txt" (
    python -m pip install --upgrade pip
    python -m pip install -r "%ROOT%requirements.txt"
) ELSE (
    echo No requirements.txt found. Skipping.
)

necho Starting Project: Kangaroo (jscjr_multiverse.py)...
python "%ROOT%jscjr_multiverse.py" %*
