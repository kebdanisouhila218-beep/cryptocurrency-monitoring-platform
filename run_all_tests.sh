#!/bin/bash

echo "🧪 ============================================"
echo "🧪 LANCEMENT DE TOUS LES TESTS"
echo "🧪 CryptoTracker - Suite de Tests Complète"
echo "🧪 ============================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Compteurs
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Fonction pour exécuter un test
run_test() {
    local test_name=$1
    local test_command=$2
    local test_dir=$3
    
    echo -e "${YELLOW}▶️  ${test_name}${NC}"
    
    if [ -n "$test_dir" ]; then
        pushd "$test_dir" > /dev/null 2>&1
    fi
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ${test_name} - PASSED${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}❌ ${test_name} - FAILED${NC}"
        ((FAILED_TESTS++))
    fi
    
    if [ -n "$test_dir" ]; then
        popd > /dev/null 2>&1
    fi
    
    ((TOTAL_TESTS++))
    echo ""
}

# ============================================
# TESTS BACKEND
# ============================================
echo -e "${BLUE}📦 TESTS BACKEND (Python/Pytest)${NC}"
echo "============================================"

# Vérifier si pytest est installé
if command -v pytest &> /dev/null; then
    run_test "Tests unitaires Collector" "pytest test_collector_logic.py -v" "collector"
    run_test "Tests unitaires API" "pytest test_api.py -v" "api"
    run_test "Tests Predictions" "pytest test_predictions.py -v" "api"
    run_test "Tests Technical Indicators" "pytest test_technical_indicators.py -v" "api"
    run_test "Tests Alerts" "pytest test_alerts.py -v" "api"
    run_test "Tests Portfolio" "pytest test_portfolio.py -v" "api"
else
    echo -e "${YELLOW}⚠️  pytest non installé. Installer avec: pip install pytest${NC}"
fi

# ============================================
# TESTS D'INTÉGRATION
# ============================================
echo ""
echo -e "${BLUE}🔗 TESTS D'INTÉGRATION${NC}"
echo "============================================"

if command -v docker-compose &> /dev/null; then
    run_test "Test Collector → MongoDB" "docker-compose run --rm test-integration"
else
    echo -e "${YELLOW}⚠️  docker-compose non disponible${NC}"
fi

# ============================================
# TESTS FRONTEND
# ============================================
echo ""
echo -e "${BLUE}⚛️  TESTS FRONTEND (React/Jest)${NC}"
echo "============================================"

if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    pushd frontend > /dev/null 2>&1
    
    if command -v npm &> /dev/null; then
        run_test "Tests authService" "npm test -- --testPathPattern=authService.test.js --passWithNoTests --watchAll=false"
        run_test "Tests cryptoService" "npm test -- --testPathPattern=cryptoService.test.js --passWithNoTests --watchAll=false"
        run_test "Tests CryptoList" "npm test -- --testPathPattern=CryptoList.test.js --passWithNoTests --watchAll=false"
    else
        echo -e "${YELLOW}⚠️  npm non disponible${NC}"
    fi
    
    popd > /dev/null 2>&1
else
    echo -e "${YELLOW}⚠️  Dossier frontend non trouvé${NC}"
fi

# ============================================
# TESTS E2E (optionnel)
# ============================================
if [ -d "tests/e2e" ]; then
    echo ""
    echo -e "${BLUE}🌐 TESTS E2E (Playwright)${NC}"
    echo "============================================"
    
    if python -c "import playwright" 2>/dev/null; then
        run_test "Test parcours utilisateur" "pytest tests/e2e/ -v"
    else
        echo -e "${YELLOW}⚠️  Playwright non installé. Installer avec:${NC}"
        echo "   pip install pytest-playwright"
        echo "   playwright install"
    fi
fi

# ============================================
# RÉSUMÉ
# ============================================
echo ""
echo "🧪 ============================================"
echo "🧪 RÉSUMÉ DES TESTS"
echo "🧪 ============================================"
echo -e "Total de tests : ${TOTAL_TESTS}"
echo -e "${GREEN}✅ Tests réussis : ${PASSED_TESTS}${NC}"
echo -e "${RED}❌ Tests échoués : ${FAILED_TESTS}${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════╗"
    echo "║  🎉 TOUS LES TESTS SONT PASSÉS ! 🎉  ║"
    echo "╚═══════════════════════════════════════╝"
    echo -e "${NC}"
    exit 0
else
    echo -e "${RED}"
    echo "╔═══════════════════════════════════════╗"
    echo "║  ⚠️  CERTAINS TESTS ONT ÉCHOUÉ  ⚠️   ║"
    echo "╚═══════════════════════════════════════╝"
    echo -e "${NC}"
    exit 1
fi
