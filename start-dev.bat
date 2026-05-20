@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "NODE_OPTIONS=--max-old-space-size=4096"
set "BACKEND_HOST=127.0.0.1"
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=3000"
set "CELERY_BROKER_URL=redis://localhost:6379/0"
set "CELERY_RESULT_BACKEND=redis://localhost:6379/1"

title BridgeGuard v2 Local Stack Launcher

echo.
echo ============================================================
echo  BridgeGuard v2 - Local Development Stack
echo ============================================================
echo.
echo This script starts the full local v2 stack:
echo   Redis    : localhost:6379 ^(local or Docker fallback^)
echo   Celery   : bridge listener/alert worker
echo   Backend  : FastAPI on http://127.0.0.1:8000
echo   Frontend : built React app on http://localhost:3000
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found in PATH.
    echo Install Python, then run this script again.
    goto fail
)

where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js was not found in PATH.
    echo Install Node.js, then run this script again.
    goto fail
)

where npm.cmd >nul 2>nul
if errorlevel 1 (
    echo [ERROR] npm.cmd was not found in PATH.
    echo Install Node.js/npm, then run this script again.
    goto fail
)

echo [1/9] Verifying backend dependencies...
pushd "%BACKEND%"
python -c "import fastapi, sqlalchemy, alembic, celery, jose, passlib, redis" >nul 2>nul
if errorlevel 1 (
    echo Backend packages missing or incomplete. Installing requirements...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Backend dependency installation failed.
        popd
        goto fail
    )
) else (
    echo Backend dependencies already available.
)
popd

echo.
echo [2/9] Verifying frontend dependencies...
pushd "%FRONTEND%"
if not exist "node_modules" (
    echo node_modules missing. Running npm install...
    call npm.cmd install
    if errorlevel 1 (
        echo [ERROR] Frontend dependency installation failed.
        popd
        goto fail
    )
) else (
    echo node_modules already exists. Skipping npm install.
)
popd

echo.
echo [3/9] Checking Redis on localhost:6379...
set "REDIS_READY=0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $client=[Net.Sockets.TcpClient]::new(); $iar=$client.BeginConnect('127.0.0.1',6379,$null,$null); if(-not $iar.AsyncWaitHandle.WaitOne(1000)){ throw 'timeout' }; $client.EndConnect($iar); $client.Close(); exit 0 } catch { exit 1 }" >nul 2>nul
if not errorlevel 1 (
    set "REDIS_READY=1"
    echo Redis is already running.
) else (
    echo Redis is not reachable. Attempting Docker fallback...
    where docker >nul 2>nul
    if errorlevel 1 (
        echo [WARN] Docker was not found. Redis/Celery listener tasks may not run until Redis is started.
    ) else (
        docker start redis-bridgeguard >nul 2>nul
        if errorlevel 1 (
            docker run -d --name redis-bridgeguard -p 6379:6379 redis:alpine >nul 2>nul
        )
        if errorlevel 1 (
            echo [WARN] Could not start Redis via Docker. Continue without Redis only if listener tasks are not needed.
        ) else (
            echo Waiting for Redis Docker container...
            for /L %%I in (1,1,10) do (
                powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $client=[Net.Sockets.TcpClient]::new('127.0.0.1',6379); $client.Close(); exit 0 } catch { exit 1 }" >nul 2>nul
                if not errorlevel 1 (
                    set "REDIS_READY=1"
                    goto redis_done
                )
                powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 1" >nul 2>nul
            )
        )
    )
)

:redis_done
if "%REDIS_READY%"=="0" (
    echo [WARN] Redis is not running. Backend works, but Celery listener and alert tasks need Redis.
)

echo.
echo [4/9] Running Alembic migrations...
pushd "%BACKEND%"
python -c "import os, sqlite3, sys; url=os.getenv('DATABASE_URL','sqlite:///./bridgeguard.db'); path=url[10:] if url.startswith('sqlite:///') else ''; tables=set(); versioned=False; (lambda c: (tables.update(r[0] for r in c.execute('select name from sqlite_master')), c.close()))(sqlite3.connect(path)) if path and os.path.exists(path) else None; (lambda c: (globals().__setitem__('versioned', any(c.execute('select version_num from alembic_version'))), c.close()))(sqlite3.connect(path)) if 'alembic_version' in tables else None; sys.exit(42 if 'users' in tables and not versioned else 0)"
if errorlevel 42 (
    echo Existing SQLite schema has no Alembic version. Stamping pre-seed revision for v2 compatibility...
    where alembic >nul 2>nul
    if errorlevel 1 (
        python -c "from alembic.config import main; main(argv=['stamp','20260520_0006'])"
    ) else (
        alembic stamp 20260520_0006
    )
    if errorlevel 1 (
        echo [ERROR] Alembic stamp failed.
        popd
        goto fail
    )
)
where alembic >nul 2>nul
if errorlevel 1 (
    python -c "from alembic.config import main; main(argv=['upgrade','head'])"
) else (
    alembic upgrade head
)
if errorlevel 1 (
    echo [ERROR] Alembic migration failed.
    popd
    goto fail
)
popd

echo.
echo [5/9] Building v2 frontend...
if /I "%SKIP_FRONTEND_BUILD%"=="1" (
    echo SKIP_FRONTEND_BUILD=1 set. Skipping npm run build.
) else (
    pushd "%FRONTEND%"
    if exist "build" (
        echo Removing stale frontend build output...
        rmdir /S /Q "build"
    )
    call npm.cmd run build
    if errorlevel 1 (
        echo [ERROR] Frontend build failed.
        popd
        goto fail
    )
    popd
)

echo.
echo [6/9] Starting Celery worker...
if "%REDIS_READY%"=="1" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'cmd.exe' -ArgumentList '/k', 'title BridgeGuard Celery Worker && celery -A app.tasks worker --loglevel=info --pool=solo' -WorkingDirectory '%BACKEND%'"
) else (
    echo [WARN] Skipping Celery auto-start because Redis is unavailable.
)

echo.
echo [7/9] Starting FastAPI backend...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'cmd.exe' -ArgumentList '/k', 'title BridgeGuard Backend API && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000' -WorkingDirectory '%BACKEND%'"

echo.
echo [8/9] Starting frontend static server...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$env:BACKEND_HOST='127.0.0.1'; $env:BACKEND_PORT='8000'; $env:FRONTEND_PORT='3000'; Start-Process -FilePath 'cmd.exe' -ArgumentList '/k', 'title BridgeGuard Frontend UI && node scripts\\serve-frontend.js' -WorkingDirectory '%ROOT%'"

echo.
echo [9/9] Performing health checks...
echo Waiting for backend and frontend to become ready...

set "BACKEND_READY=0"
for /L %%I in (1,1,20) do (
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
echo Backend health:
if "%BACKEND_READY%"=="1" (
    where curl.exe >nul 2>nul
    if errorlevel 1 (
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 8 | ConvertTo-Json -Compress"
    ) else (
        curl.exe -fsS http://localhost:8000/health
    )
) else (
    echo [WARN] Backend not ready yet. Check the BridgeGuard Backend API window.
)

echo.
echo Frontend health:
if "%FRONTEND_READY%"=="1" (
    where curl.exe >nul 2>nul
    if errorlevel 1 (
        powershell -NoProfile -ExecutionPolicy Bypass -Command "(Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 8).StatusCode"
    ) else (
        curl.exe -fsS -o NUL -w "HTTP %%{http_code}" http://localhost:3000
        echo.
    )
) else (
    echo [WARN] Frontend not ready yet. Check the BridgeGuard Frontend UI window.
)

echo.
echo ============================================================
echo  BridgeGuard v2 stack launched
echo ============================================================
echo.
echo URLs:
echo   Frontend console : http://localhost:3000
echo   Backend health   : http://127.0.0.1:8000/health
echo   API docs         : http://127.0.0.1:8000/docs
echo   v1 API prefix    : http://127.0.0.1:8000/api/v1
echo   v2 API prefix    : http://127.0.0.1:8000/api/v2
echo.
echo Demo login after migrations:
echo   Email    : demo@bridgeguard.local
echo   Password : bridgeguard-demo
echo.
echo To stop the stack, close the Celery, backend, and frontend command windows.
goto end

:fail
echo.
echo ============================================================
echo  BridgeGuard v2 launch failed
echo ============================================================
echo Fix the error above and run start-dev.bat again.

:end
echo.
pause
