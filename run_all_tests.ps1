# run_all_tests.ps1
# Script PowerShell pour lancer tous les tests sur Windows

Write-Host "🧪 ============================================" -ForegroundColor Cyan
Write-Host "🧪 LANCEMENT DE TOUS LES TESTS" -ForegroundColor Cyan
Write-Host "🧪 CryptoTracker - Suite de Tests Complète" -ForegroundColor Cyan
Write-Host "🧪 ============================================" -ForegroundColor Cyan
Write-Host ""

# Compteurs
$TotalTests = 0
$PassedTests = 0
$FailedTests = 0

# Fonction pour exécuter un test
function Run-Test {
    param (
        [string]$TestName,
        [string]$TestCommand,
        [string]$TestDir = ""
    )
    
    Write-Host "▶️  $TestName" -ForegroundColor Yellow
    
    $originalDir = Get-Location
    
    if ($TestDir -ne "") {
        Set-Location $TestDir
    }
    
    try {
        $result = Invoke-Expression $TestCommand 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $TestName - PASSED" -ForegroundColor Green
            $script:PassedTests++
        } else {
            Write-Host "❌ $TestName - FAILED" -ForegroundColor Red
            $script:FailedTests++
        }
    } catch {
        Write-Host "❌ $TestName - FAILED (Exception)" -ForegroundColor Red
        $script:FailedTests++
    }
    
    if ($TestDir -ne "") {
        Set-Location $originalDir
    }
    
    $script:TotalTests++
    Write-Host ""
}

# ============================================
# TESTS BACKEND
# ============================================
Write-Host "📦 TESTS BACKEND (Python/Pytest)" -ForegroundColor Blue
Write-Host "============================================"

# Vérifier si pytest est installé
$pytestInstalled = Get-Command pytest -ErrorAction SilentlyContinue

if ($pytestInstalled) {
    Run-Test -TestName "Tests unitaires Collector" -TestCommand "pytest test_collector_logic.py -v" -TestDir "collector"
    Run-Test -TestName "Tests unitaires API" -TestCommand "pytest test_api.py -v" -TestDir "api"
    Run-Test -TestName "Tests Predictions" -TestCommand "pytest test_predictions.py -v" -TestDir "api"
    Run-Test -TestName "Tests Technical Indicators" -TestCommand "pytest test_technical_indicators.py -v" -TestDir "api"
    Run-Test -TestName "Tests Alerts" -TestCommand "pytest test_alerts.py -v" -TestDir "api"
    Run-Test -TestName "Tests Portfolio" -TestCommand "pytest test_portfolio.py -v" -TestDir "api"
} else {
    Write-Host "⚠️  pytest non installé. Installer avec: pip install pytest" -ForegroundColor Yellow
}

# ============================================
# TESTS D'INTÉGRATION
# ============================================
Write-Host ""
Write-Host "🔗 TESTS D'INTÉGRATION" -ForegroundColor Blue
Write-Host "============================================"

$dockerComposeInstalled = Get-Command docker-compose -ErrorAction SilentlyContinue

if ($dockerComposeInstalled) {
    Run-Test -TestName "Test Collector → MongoDB" -TestCommand "docker-compose run --rm test-integration"
} else {
    Write-Host "⚠️  docker-compose non disponible" -ForegroundColor Yellow
}

# ============================================
# TESTS FRONTEND
# ============================================
Write-Host ""
Write-Host "⚛️  TESTS FRONTEND (React/Jest)" -ForegroundColor Blue
Write-Host "============================================"

if (Test-Path "frontend/package.json") {
    $npmInstalled = Get-Command npm -ErrorAction SilentlyContinue
    
    if ($npmInstalled) {
        Run-Test -TestName "Tests authService" -TestCommand "npm test -- --testPathPattern=authService.test.js --passWithNoTests --watchAll=false" -TestDir "frontend"
        Run-Test -TestName "Tests cryptoService" -TestCommand "npm test -- --testPathPattern=cryptoService.test.js --passWithNoTests --watchAll=false" -TestDir "frontend"
        Run-Test -TestName "Tests CryptoList" -TestCommand "npm test -- --testPathPattern=CryptoList.test.js --passWithNoTests --watchAll=false" -TestDir "frontend"
    } else {
        Write-Host "⚠️  npm non disponible" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Dossier frontend non trouvé" -ForegroundColor Yellow
}

# ============================================
# TESTS E2E (optionnel)
# ============================================
if (Test-Path "tests/e2e") {
    Write-Host ""
    Write-Host "🌐 TESTS E2E (Playwright)" -ForegroundColor Blue
    Write-Host "============================================"
    
    try {
        python -c "import playwright" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Run-Test -TestName "Test parcours utilisateur" -TestCommand "pytest tests/e2e/ -v"
        } else {
            Write-Host "⚠️  Playwright non installé. Installer avec:" -ForegroundColor Yellow
            Write-Host "   pip install pytest-playwright" -ForegroundColor Yellow
            Write-Host "   playwright install" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  Playwright non installé" -ForegroundColor Yellow
    }
}

# ============================================
# RÉSUMÉ
# ============================================
Write-Host ""
Write-Host "🧪 ============================================" -ForegroundColor Cyan
Write-Host "🧪 RÉSUMÉ DES TESTS" -ForegroundColor Cyan
Write-Host "🧪 ============================================" -ForegroundColor Cyan
Write-Host "Total de tests : $TotalTests"
Write-Host "✅ Tests réussis : $PassedTests" -ForegroundColor Green
Write-Host "❌ Tests échoués : $FailedTests" -ForegroundColor Red

if ($FailedTests -eq 0) {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  🎉 TOUS LES TESTS SONT PASSÉS ! 🎉  ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════╝" -ForegroundColor Green
    exit 0
} else {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║  ⚠️  CERTAINS TESTS ONT ÉCHOUÉ  ⚠️   ║" -ForegroundColor Red
    Write-Host "╚═══════════════════════════════════════╝" -ForegroundColor Red
    exit 1
}
