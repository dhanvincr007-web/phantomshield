@echo off
echo =====================================================================
echo   PhantomShield (GraphShield AI) — hackFront India 2026
echo   GraphOps Engine for Autonomous Threat Hunting & AI Deception
echo =====================================================================
echo.

if "%1"=="docker" goto rundocker

echo [1/3] Starting Neo4j / Docker stack if available...
where docker >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Docker detected. Launching via Docker Compose...
    docker-compose up -d
    echo Stack is running!
    echo SOC Dashboard: http://localhost:3000
    echo Backend API:   http://localhost:8000/docs
    echo Neo4j Browser: http://localhost:7474
    exit /b 0
)

echo Docker not found or standalone mode selected.
echo Running in Native Python + Node.js Mode...
echo.
echo [2/3] Starting Backend in new window...
start cmd /k "cd backend && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo [3/3] Starting Frontend in new window...
start cmd /k "cd frontend && npm install && npm run dev"

echo.
echo All services launched!
echo SOC Dashboard: http://localhost:3000
echo Backend API:   http://localhost:8000/docs
exit /b 0

:rundocker
docker-compose up --build

