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
echo Training Configuration
echo ========================

:: Set default values for non-full scratch configs
set "max_epochs=100"
set "run_name=model"
set "config_path=./configs/presets/config_dit_mel_seed_uvit_whisper_base_f0_44k.yml"
set "batch_size=3"

echo.
echo VRAM Requirements for Batch Size:
echo * For 12GB VRAM: Use batch_size=3
echo * For 24GB VRAM: Use batch_size=6
echo * Default value: 3
set /p "batch_input=Enter batch size (press Enter to use default): "
if not "!batch_input!"=="" set "batch_size=!batch_input!"

:: Select model type
echo ------------------------
echo Select model type:
echo 1) Realtime Fine Tune
echo 2) Singing Fine Tune
echo 3) Full Scratch Training
set /p "model_type=Enter your choice (1-3): "

if "!model_type!"=="1" (
    set "config_path=./configs/presets/config_dit_mel_seed_uvit_xlsr_tiny.yml"
) else if "!model_type!"=="2" (
    set "config_path=./configs/presets/config_dit_mel_seed_uvit_whisper_base_f0_44k.yml"
) else if "!model_type!"=="3" (
    set "config_path=./configs/presets/config_ultimate_quality.yml"
    set "max_epochs=1000"
) else (
    echo Invalid selection. Using default Singing config.
    set "model_type=2"
)

:: Ask for max epochs
echo ------------------------
set /p "epochs_input=Enter maximum epochs (default: !max_epochs!, press Enter to use default): "
if not "!epochs_input!"=="" set "max_epochs=!epochs_input!"

:: Ask for run name
echo ------------------------
set /p "name_input=Enter run name (default: model, press Enter to use default): "
if not "!name_input!"=="" set "run_name=!name_input!"

echo ------------------------
echo Configuration Summary:
echo - Training Type: !model_type! (1=Realtime, 2=Singing, 3=Full)
echo - Config File: !config_path!
echo - Maximum Epochs: !max_epochs!
echo - Batch Size: !batch_size!
echo - Run Name: !run_name!
echo.
set /p "confirm=Is this correct? (Y/N): "
if /i not "!confirm!"=="Y" goto end

:: Store these variables in global environment variables
endlocal & set "TRAIN_MAX_EPOCHS=%max_epochs%" & set "TRAIN_RUN_NAME=%run_name%" & set "TRAIN_CONFIG_PATH=%config_path%" & set "TRAIN_MODEL_TYPE=%model_type%" & set "TRAIN_BATCH_SIZE=%batch_size%"

echo.
echo ========================
echo Converting WAV files...
echo ========================
python wave_conv.py %TRAIN_MODEL_TYPE%

setlocal enabledelayedexpansion

:: Count WAV files in training_data_conv directory and calculate max_steps
set "wav_count=0"
for %%F in (training_data_conv\*.wav) do set /a wav_count+=1

:: Calculate max_steps with ceiling division and multiply by epochs
set /a "steps_per_epoch=(wav_count + %TRAIN_BATCH_SIZE% - 1) / %TRAIN_BATCH_SIZE%"
set /a "max_steps=steps_per_epoch * %TRAIN_MAX_EPOCHS%"

echo.
echo Calculated training parameters:
echo - Steps per Epoch: !steps_per_epoch! (based on !wav_count! WAV files)
echo - Maximum Steps: !max_steps!

endlocal & set "TRAIN_MAX_STEPS=%max_steps%"

echo.
echo ========================
echo Starting training...
echo ========================
python train.py --config %TRAIN_CONFIG_PATH% --dataset-dir ./training_data_conv --run-name %TRAIN_RUN_NAME% --batch-size %TRAIN_BATCH_SIZE% --max-steps %TRAIN_MAX_STEPS% --max-epochs %TRAIN_MAX_EPOCHS% --save-every 500 --num-workers 0

:end
echo Script finished. Press any key to exit...
pause
exit