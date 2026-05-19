@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "NODE_OPTIONS=--max-old-space-size=4096"

title CarthEdge BridgeGuard MVP Launcher

echo.
echo ============================================================
echo  CarthEdge BridgeGuard - Local MVP Launcher
echo ============================================================
echo.
echo This script starts the local defensive MVP:
echo   Backend : FastAPI on http://127.0.0.1:8000
echo   Frontend: React on http://localhost:3000
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found in PATH.
    echo Install Python, then run this script again.
    goto end
)

where npm.cmd >nul 2>nul
if errorlevel 1 (
    echo [ERROR] npm.cmd was not found in PATH.
    echo Install Node.js, then run this script again.
    goto end
)

echo [1/5] Installing or verifying backend dependencies...
pushd "%BACKEND%"
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Backend dependency installation failed.
    popd
    goto end
)
popd

echo.
echo [2/5] Installing or verifying frontend dependencies...
pushd "%FRONTEND%"
if not exist "node_modules" (
    call npm.cmd install
    if errorlevel 1 (
        echo [ERROR] Frontend dependency installation failed.
        popd
        goto end
    )
) else (
    echo node_modules already exists. Skipping npm install.
)
popd

echo.
choice /C YN /N /M "Run backend tests before launch? [Y/N] "
if errorlevel 2 goto skip_backend_tests
echo.
echo [3/5] Running backend tests...
pushd "%BACKEND%"
python -m pytest tests
if errorlevel 1 (
    echo [ERROR] Backend tests failed. Fix them before publishing or demoing.
    popd
    goto end
)
popd
goto backend_tests_done

:skip_backend_tests
echo [3/5] Backend tests skipped.

:backend_tests_done
echo.
echo.
echo [4/5] Building frontend static bundle...
node "%ROOT%scripts\build-frontend.js"
if errorlevel 1 (
    echo [ERROR] Frontend bundle build failed.
    goto end
)

echo.
echo [5/5] Starting local servers...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'cmd.exe' -ArgumentList '/k', 'python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000' -WorkingDirectory '%BACKEND%'"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$psi=[System.Diagnostics.ProcessStartInfo]::new(); $psi.FileName='node.exe'; $psi.Arguments='scripts\\serve-frontend.js'; $psi.WorkingDirectory='%ROOT%'; $psi.UseShellExecute=$true; [System.Diagnostics.Process]::Start($psi) | Out-Null"

echo.
echo Waiting for local servers before health checks...

set "BACKEND_READY=0"
for /L %%I in (1,1,10) do (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
    if not errorlevel 1 (
        set "BACKEND_READY=1"
        goto backend_ready
    )
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 2" >nul 2>nul
)

:backend_ready
set "FRONTEND_READY=0"
for /L %%I in (1,1,20) do (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
    if not errorlevel 1 (
        set "FRONTEND_READY=1"
        goto frontend_ready
    )
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 2" >nul 2>nul
)

:frontend_ready

echo.
echo Backend health check:
if "%BACKEND_READY%"=="1" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 8 | ConvertTo-Json -Compress"
) else (
    echo Backend not ready yet. Check the "BridgeGuard Backend API" window.
)

echo.
echo Frontend check:
if "%FRONTEND_READY%"=="1" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "(Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 8).StatusCode"
) else (
    echo Frontend not ready yet. Check the "BridgeGuard Frontend UI" window.
)

echo.
echo ============================================================
echo  BridgeGuard MVP launched
echo ============================================================
echo.
echo Open:
echo   Frontend dashboard : http://localhost:3000
echo   Backend health     : http://127.0.0.1:8000/health
echo   API docs           : http://127.0.0.1:8000/docs
echo.
echo Useful manual tests:
echo   curl http://127.0.0.1:8000/health
echo   curl http://127.0.0.1:8000/attacks
echo   curl -X POST "http://127.0.0.1:8000/simulate-attack/Ronin%%20Bridge"
echo.
echo To stop the MVP, close the backend window and stop the node.exe frontend process if needed.

:end
echo.
pause
