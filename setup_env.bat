@echo off
echo Setting up YouTube Video Generator development environment...

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Conda not found. Please install Miniconda or Anaconda first.
    exit /b 1
)

REM Create and activate conda environment
echo Creating conda environment...
call conda env create -f environment.yml
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to create conda environment.
    exit /b 1
)

REM Activate environment
echo Activating environment...
call conda activate videogen

REM Install development version
echo Installing package in development mode...
pip install -e .[dev]

REM Setup pre-commit
echo Setting up pre-commit hooks...
pre-commit install

REM Configure git
echo Configuring git...
git config --local core.autocrlf true

REM Create required directories
echo Creating project directories...
mkdir output 2>nul
mkdir temp 2>nul
mkdir test_files 2>nul
mkdir test_results 2>nul

REM Verify installation
echo.
echo Verifying installation...
echo.

echo Checking FFmpeg...
ffmpeg -version | findstr "version"

echo.
echo Checking Python packages...
python -c "import sys; print(f'Python: {sys.version.split()[0]}')"
python -c "import moviepy; print(f'moviepy: {moviepy.__version__}')"
python -c "import numpy; print(f'numpy: {numpy.__version__}')"
python -c "import pydub; print(f'pydub: {pydub.__version__}')"

echo.
echo Running initial tests...
pytest -v --collect-only

echo.
echo Setup complete! You can now use:
echo - 'conda activate videogen' to activate the environment
echo - 'pytest' to run tests
echo - 'pre-commit run --all-files' to check code quality
