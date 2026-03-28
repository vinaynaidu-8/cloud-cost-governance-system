@echo off
echo ========================================
echo Cloud Cost Governance - Windows Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check AWS CLI installation
aws --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: AWS CLI not found
    echo Please install AWS CLI from https://aws.amazon.com/cli/
    echo Or configure AWS credentials manually
    echo.
)

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment created

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated

REM Install dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Create data directory
if not exist data mkdir data
echo ✅ Data directory created

REM Copy sample data for testing
echo.
echo Copying sample data for testing...
xcopy "sample_data" "data" /E /I /Y >nul
echo ✅ Sample data copied

REM Test AWS credentials
echo.
echo Testing AWS credentials...
python aws_setup.py
if errorlevel 1 (
    echo WARNING: AWS credentials test failed
    echo You can still test with sample data
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Configure AWS credentials: aws configure
echo 2. Run pipeline: python pipeline\run_pipeline.py
echo 3. Start dashboard: python web\app.py
echo 4. Open browser: http://localhost:5000
echo.
echo For live AWS data, ensure you have:
echo - AWS credentials configured
echo - Required IAM permissions
echo - Cost Explorer enabled
echo.
pause
