@echo off
setlocal enabledelayedexpansion

rem ========================================
rem PDF Translation Tool - Conversion Process Script
rem Function: PDF -> Markdown -> DOCX (no translation)
rem ========================================

echo ========================================
echo PDF Translation Tool - Starting
echo ========================================
echo.

rem Get script directory
set SCRIPT_DIR=%~dp0
set AIMS_DIR=%SCRIPT_DIR%aims
set OUTPUT_DIR=%SCRIPT_DIR%output

rem Check if aims directory exists
if not exist "%AIMS_DIR%" (
    echo [ERROR] aims directory does not exist: %AIMS_DIR%
    echo Please put PDF files in aims directory first
    pause
    exit /b 1
)

rem Check if there are PDF files in aims directory
dir /b "%AIMS_DIR%\*.pdf" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No PDF files found in aims directory
    echo Please put PDF files in aims directory first
    pause
    exit /b 1
)

rem Activate conda environment
echo [1/5] Activating conda environment...
call conda activate pdf_translate_m
if errorlevel 1 (
    echo [ERROR] Failed to activate conda environment
    pause
    exit /b 1
)

rem Check if pandoc is installed
echo [2/5] Checking pandoc installation...
pandoc --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pandoc is not installed, DOCX conversion cannot be performed
    echo Visit https://pandoc.org/installing.html for installation
    cd /d "%SCRIPT_DIR%"
    pause
    exit /b 1
)

rem Enter aims directory for processing
cd /d "%AIMS_DIR%"

rem Clean previous temporary files (keep PDF files and their output directories)
echo [3/5] Cleaning temporary files...
for /d %%i in (*) do (
    if "%%i"=="media" (
        rd /s /q "%%i" 2>nul
    )
)
del /q *.md *.json *.log 2>nul
echo Temporary files cleaned

rem Run MinerU to convert PDF to Markdown
echo [4/5] Running MinerU PDF conversion...
call mineru -p ./ -o ./
if errorlevel 1 (
    echo [ERROR] MinerU conversion failed
    cd /d "%SCRIPT_DIR%"
    pause
    exit /b 1
)

rem Check if markdown files were generated (search recursively)
dir /s /b *.md >nul 2>&1
if errorlevel 1 (
    echo [ERROR] MinerU did not generate markdown files
    cd /d "%SCRIPT_DIR%"
    pause
    exit /b 1
)

echo MinerU conversion completed

cd /d "%SCRIPT_DIR%"

rem Convert to DOCX
echo [5/5] Converting markdown to DOCX...
python "%SCRIPT_DIR%convert_md_to_docx.py"
if errorlevel 1 (
    echo [ERROR] Errors occurred during DOCX conversion
    cd /d "%SCRIPT_DIR%"
    pause
    exit /b 1
)

rem Copy files to output directory
echo.
echo Copying files to output directory...
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
xcopy /s /e /y "%AIMS_DIR%\*" "%OUTPUT_DIR%\"
echo Files copied successfully

echo.
echo ========================================
echo Processing completed!
echo ========================================
echo Output directory: %OUTPUT_DIR%
echo.

rem Clean aims directory (optional, keep PDF files)
echo Do you want to clean temporary files in aims directory? (PDF files will be kept)
set /p CLEANUP="Enter Y to confirm, any other key to skip: "
if /i "%CLEANUP%"=="Y" (
    cd /d "%AIMS_DIR%"
    for /d %%i in (*) do rd /s /q "%%i" 2>nul
    del /q *.md *.json *.log 2>nul
    rd /s /q media 2>nul
    echo aims directory cleaned
    cd /d "%SCRIPT_DIR%"
)

pause
