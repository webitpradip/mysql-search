@echo off
REM Check if the virtual environment exists
if not exist "env\" (
    echo Creating Python virtual environment...
    python -m venv env
)

REM Activate the virtual environment
call env\Scripts\activate

REM Install the required packages from requirements.txt
if exist "requirements.txt" (
    echo Installing packages from requirements.txt...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found. Please make sure it is present in the directory.
    exit /b
)

REM Ask for a port number
set /p PORT="Enter the port number you want to run Django on (default is 8000): "

REM Set default port if not provided
if "%PORT%"=="" set PORT=8000

REM Run Django server on the specified port
echo Starting Django server on port %PORT%...
python manage.py runserver %PORT%

REM Deactivate the virtual environment
deactivate
