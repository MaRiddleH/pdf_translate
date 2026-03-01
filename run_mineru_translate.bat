@echo off

rem 1. Open cmd (batch file runs in cmd by default)

rem 2. Change to specified directory
cd /d %~dp0aims

rem 3. Activate conda environment
call conda activate pdf_translate_m

rem 4. Clear all folders in current directory
echo Cleaning folders in directory...
for /d %%i in (*) do rd /s /q "%%i"
echo Folders cleaning completed

rem 5. Run mineru command
echo Running mineru command...
mineru -p ./ -o ./

cd ../

rem 6. Translating Markdown files
echo Translating Markdown files...
python ./translate_md.py

rem 7. Move all files from aims to Output folder
echo Moving files to output folder...
if not exist output mkdir output
xcopy /s /e /y aims\* output\
echo Files moved successfully to output folder

rem 8. Delete all files in aims folder
echo Deleting all files in aims folder...
for /d %%i in (aims\*) do rd /s /q "%%i"
del /q aims\*.*
echo All files in aims folder deleted successfully

pause
