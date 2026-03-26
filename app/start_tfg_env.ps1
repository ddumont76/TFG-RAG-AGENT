# ================================
# Script de arranque para el TFG RAG
# Autor: Deborah Dumont Gonzalez
# Este script configura el entorno, activa el virtualenv y lanza la API FastAPI.
# ================================

Write-Host "🚀 Iniciando configuración del entorno para el TFG..." -ForegroundColor Cyan

# --------------------------------
# 1. Habilitar ejecución de scripts para el usuario actual
# --------------------------------
$policy = Get-ExecutionPolicy -Scope CurrentUser

if ($policy -ne "RemoteSigned" -and $policy -ne "Unrestricted") {
    Write-Host "⚠️  Cambiando ExecutionPolicy para este usuario..." -ForegroundColor Yellow
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
    Write-Host "✔️  ExecutionPolicy configurado en RemoteSigned." -ForegroundColor Green
} else {
    Write-Host "✔️  ExecutionPolicy ya está configurado correctamente." -ForegroundColor Green
}

# --------------------------------
# 2. Ir a la carpeta del proyecto
# --------------------------------
$projectPath = "C:\Users\deborah.dumontgonzal\work\tfg-rag-agent"
Write-Host "📂 Moviéndonos a: $projectPath" -ForegroundColor Cyan
Set-Location $projectPath

# --------------------------------
# 3. Activar el entorno virtual
# --------------------------------
$venvPath = ".\venv\Scripts\Activate.ps1"

if (Test-Path $venvPath) {
    Write-Host "🐍 Activando entorno virtual..." -ForegroundColor Cyan
    & $venvPath
    Write-Host "✔️ Entorno virtual activado." -ForegroundColor Green
} else {
    Write-Host "❌ No se encontró el entorno virtual en: $venvPath" -ForegroundColor Red
    Write-Host "👉 Ejecuta: python -m venv venv" -ForegroundColor Yellow
    exit
}

# --------------------------------
# 4. Ejecutar la API con Uvicorn
# --------------------------------

Write-Host "🚀 Iniciando API FastAPI..." -ForegroundColor Cyan
uvicorn app.api.main:app --reload