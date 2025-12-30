# tests/security/run_snyk.ps1
# Script PowerShell pour exécuter les analyses de sécurité Snyk

Write-Host "========================================"
Write-Host "🔒 SNYK SECURITY ANALYSIS" -ForegroundColor Cyan
Write-Host "========================================"

# Vérifier si Snyk est installé
$snykPath = Get-Command snyk -ErrorAction SilentlyContinue
if (-not $snykPath) {
    Write-Host "❌ Snyk n'est pas installé" -ForegroundColor Red
    Write-Host "   Installation: npm install -g snyk"
    Write-Host "   Puis: snyk auth"
    exit 1
}

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$ResultsDir = Join-Path $PSScriptRoot "results"

# Créer le dossier results
if (-not (Test-Path $ResultsDir)) {
    New-Item -ItemType Directory -Path $ResultsDir | Out-Null
}

Write-Host ""
Write-Host "📁 Projet: $ProjectRoot"
Write-Host "📅 Date: $(Get-Date)"
Write-Host ""

# ===== ANALYSE PYTHON =====
Write-Host "========================================"
Write-Host "🐍 Analyse des dépendances Python (API)" -ForegroundColor Yellow
Write-Host "========================================"

$requirementsPath = Join-Path $ProjectRoot "api\requirements.txt"
if (Test-Path $requirementsPath) {
    Set-Location (Join-Path $ProjectRoot "api")
    
    $result = snyk test --file=requirements.txt --json 2>$null
    $result | Out-File (Join-Path $ResultsDir "snyk_python.json")
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Aucune vulnérabilité Python détectée" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Vulnérabilités Python détectées" -ForegroundColor Yellow
        snyk test --file=requirements.txt 2>$null | Select-Object -First 30
    }
} else {
    Write-Host "⚠️ requirements.txt non trouvé" -ForegroundColor Yellow
}

# ===== ANALYSE NODE.JS =====
Write-Host ""
Write-Host "========================================"
Write-Host "📦 Analyse des dépendances Node.js (Frontend)" -ForegroundColor Yellow
Write-Host "========================================"

$packagePath = Join-Path $ProjectRoot "frontend\package.json"
if (Test-Path $packagePath) {
    Set-Location (Join-Path $ProjectRoot "frontend")
    
    $result = snyk test --json 2>$null
    $result | Out-File (Join-Path $ResultsDir "snyk_nodejs.json")
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Aucune vulnérabilité Node.js détectée" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Vulnérabilités Node.js détectées" -ForegroundColor Yellow
        snyk test 2>$null | Select-Object -First 30
    }
} else {
    Write-Host "⚠️ package.json non trouvé" -ForegroundColor Yellow
}

# ===== ANALYSE CODE =====
Write-Host ""
Write-Host "========================================"
Write-Host "🔍 Analyse du code source (SAST)" -ForegroundColor Yellow
Write-Host "========================================"

Set-Location $ProjectRoot
$result = snyk code test --json 2>$null
$result | Out-File (Join-Path $ResultsDir "snyk_code.json")

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Aucune vulnérabilité de code détectée" -ForegroundColor Green
} else {
    Write-Host "⚠️ Vulnérabilités de code détectées" -ForegroundColor Yellow
    snyk code test 2>$null | Select-Object -First 20
}

# ===== RAPPORT FINAL =====
Write-Host ""
Write-Host "========================================"
Write-Host "📊 RAPPORT FINAL" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host "Résultats sauvegardés dans: $ResultsDir"
Write-Host ""
Get-ChildItem $ResultsDir -Filter "*.json" | Format-Table Name, Length, LastWriteTime

Write-Host ""
Write-Host "========================================"
Write-Host "✅ Analyse Snyk terminée" -ForegroundColor Green
Write-Host "========================================"

Set-Location $ProjectRoot
