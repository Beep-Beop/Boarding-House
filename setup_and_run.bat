@echo off
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate
    
    echo Installing dependencies...
    python -m pip install -r requirements.txt || (
        echo.
        echo ------------------------------------------
        echo ERROR: Installation failed!
        echo ------------------------------------------
        pause
        exit /b 1
    )
    
    echo.
    echo ------------------------------------------
    echo Dependencies installed successfully!
    echo ------------------------------------------
    pause
) else (
    call .venv\Scripts\activate
)