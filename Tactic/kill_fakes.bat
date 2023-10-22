@echo off
setlocal

for /F %%i in (pids.txt) do (
    echo Killing process with PID %%i
    taskkill /PID %%i /F
)

del pids.txt  ; Remove the temporary file