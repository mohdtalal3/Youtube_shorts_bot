@echo off

:: Check if virtual environment exists
IF EXIST "myenv\Scripts\activate.bat" (
    echo Virtual environment exists. Activating...
    call myenv\Scripts\activate.bat
) ELSE (
    echo Creating new virtual environment...
    python -m venv myenv
    call myenv\Scripts\activate.bat
    
    :: Install packages only when creating new environment
    IF EXIST "requirements.txt" (
        echo Installing packages from requirements.txt...
        pip install -r requirements.txt
    ) ELSE (
        echo No requirements.txt found. Skipping package installation.
    )
)

:: Run your Python script
IF EXIST "account_creator_gui.py" (
    echo Running account_creator_gui.py...
    python account_creator_gui.py
) ELSE (
    echo account_creator_gui.py not found. Please create your Python script.
)

:: Keep the window open
pause