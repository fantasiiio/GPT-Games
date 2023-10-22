@echo off
setlocal enabledelayedexpansion

if "%1"=="" (
    echo No parameter provided, using default value of 1
    set end_value=1
) else (
    set end_value=%1
)

set /a adjusted_end_value=!end_value! - 1  ; Subtract 1 from end_value

echo. > pids.txt  ; Empty the file if it already exists

for /l %%i in (0, 1, !adjusted_end_value!-1) do (
    echo Starting process with parameter %%i
    start /b python MainFrame.py -ai %%i
    echo !ERRORLEVEL! >> pids.txt  ; Append PID to pids.txt
)

endlocal