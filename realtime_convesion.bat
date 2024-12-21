setlocal enabledelayedexpansion

goto begin

:: Function to display error and loop back to the beginning
:error_handler
echo [ERROR] %1
goto end

:begin
echo.
echo ========================
echo Executing common setup...
echo ========================
:: Check for Python virtual environment
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    if !ERRORLEVEL! neq 0 (
        call :error_handler "Failed to create a virtual environment. Error code: !ERRORLEVEL!"
    )
)

echo.
echo ========================
echo Activating virtual environment...
echo ========================

endlocal
call venv\Scripts\activate
setlocal enabledelayedexpansion

if !ERRORLEVEL! neq 0 (
    call :error_handler "Failed to activate the virtual environment. Error code: !ERRORLEVEL!"
)

echo ========================
echo Checking for Visual C++ Build Tools...
echo ========================

:: Check if Visual C++ Build Tools are installed
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo Visual C++ Build Tools are not installed.
    echo Please install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    goto end
)

echo ========================
echo Upgrading pip...
echo ========================

python -m pip install --upgrade pip
if !ERRORLEVEL! neq 0 (
    call :error_handler "Failed to upgrade pip. Error code: !ERRORLEVEL!"
    goto end
)

echo.
echo ========================
echo Installing dependencies...
echo ========================
pip install -U -r requirements.txt
if !ERRORLEVEL! neq 0 (
    call :error_handler "Failed to install dependencies. Error code: !ERRORLEVEL!"
)

echo.
echo ========================
echo Select model folder...
echo ========================

:: List all folders in ./runs directory
set "index=0"
for /d %%D in (./runs/*) do (
    set /a "index+=1"
    set "folder[!index!]=%%~nxD"
    echo !index!^) %%~nxD
)

set /p choice="Enter the number of the folder you want to use: "

:: Validate input
if !choice! leq 0 goto invalid_choice
if !choice! gtr !index! goto invalid_choice

:: Get selected folder name
set "selected_folder=!folder[%choice%]!"

echo.
echo ========================
echo Finding config file in !selected_folder!...
echo ========================

:: Search for yml file in the selected folder
set "config_file="
for /f "delims=" %%F in ('dir /b ".\runs\!selected_folder!\*.yml" 2^>nul') do (
    if not defined config_file (
        set "config_file=%%F"
        echo Found config file: %%F
    )
)

:: If no yml file found in selected folder, use default config
if not defined config_file (
    echo No config file found in selected folder, using default config...
    set "config_file=./configs/presets/config_dit_mel_seed_uvit_whisper_base_f0_44k.yml"
) else (
    set "config_file=./runs/!selected_folder!/!config_file!"
)

echo.
echo ========================
echo Starting app with !selected_folder!...
echo Using config: !config_file!
echo ========================

:: Store the selected folder and config file in global environment variables before endlocal
endlocal & (
    set "SELECTED_MODEL_FOLDER=%selected_folder%"
    set "CONFIG_FILE=%config_file%"
)

python real-time-gui.py --checkpoint ./runs/%SELECTED_MODEL_FOLDER%/ft_model.pth --config %CONFIG_FILE%

setlocal enabledelayedexpansion

if !ERRORLEVEL! neq 0 (
    echo Failed to start the application.
    exit /b 1
)

goto end

:invalid_choice
echo Invalid selection. Please try again.
goto end

:end
echo Script finished. Press any key to exit...
pause
exit