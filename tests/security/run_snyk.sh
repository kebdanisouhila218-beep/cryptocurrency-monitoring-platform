#!/bin/bash
# tests/security/run_snyk.sh
# Script pour exécuter les analyses de sécurité Snyk

echo "========================================"
echo "🔒 SNYK SECURITY ANALYSIS"
echo "========================================"

# Vérifier si Snyk est installé
if ! command -v snyk &> /dev/null; then
    echo "❌ Snyk n'est pas installé"
    echo "   Installation: npm install -g snyk"
    echo "   Puis: snyk auth"
    exit 1
fi

# Vérifier l'authentification
if ! snyk auth check &> /dev/null; then
    echo "⚠️ Snyk non authentifié. Exécutez: snyk auth"
fi

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RESULTS_DIR="$PROJECT_ROOT/tests/security/results"
mkdir -p "$RESULTS_DIR"

echo ""
echo "📁 Projet: $PROJECT_ROOT"
echo "📅 Date: $(date)"
echo ""

# ===== ANALYSE PYTHON =====
echo "========================================"
echo "🐍 Analyse des dépendances Python (API)"
echo "========================================"

if [ -f "$PROJECT_ROOT/api/requirements.txt" ]; then
    cd "$PROJECT_ROOT/api"
    snyk test --file=requirements.txt --json > "$RESULTS_DIR/snyk_python.json" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Aucune vulnérabilité Python détectée"
    else
        echo "⚠️ Vulnérabilités Python détectées"
        snyk test --file=requirements.txt 2>/dev/null | head -50
    fi
else
    echo "⚠️ requirements.txt non trouvé"
fi

# ===== ANALYSE NODE.JS =====
echo ""
echo "========================================"
echo "📦 Analyse des dépendances Node.js (Frontend)"
echo "========================================"

if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    cd "$PROJECT_ROOT/frontend"
    snyk test --json > "$RESULTS_DIR/snyk_nodejs.json" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Aucune vulnérabilité Node.js détectée"
    else
        echo "⚠️ Vulnérabilités Node.js détectées"
        snyk test 2>/dev/null | head -50
    fi
else
    echo "⚠️ package.json non trouvé"
fi

# ===== ANALYSE DOCKER =====
echo ""
echo "========================================"
echo "🐳 Analyse des images Docker"
echo "========================================"

# API Dockerfile
if [ -f "$PROJECT_ROOT/api/Dockerfile" ]; then
    echo "Analyse de api/Dockerfile..."
    cd "$PROJECT_ROOT/api"
    snyk container test --file=Dockerfile --json > "$RESULTS_DIR/snyk_docker_api.json" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Image API: Aucune vulnérabilité critique"
    else
        echo "⚠️ Image API: Vulnérabilités détectées"
    fi
fi

# Collector Dockerfile
if [ -f "$PROJECT_ROOT/collector/Dockerfile" ]; then
    echo "Analyse de collector/Dockerfile..."
    cd "$PROJECT_ROOT/collector"
    snyk container test --file=Dockerfile --json > "$RESULTS_DIR/snyk_docker_collector.json" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Image Collector: Aucune vulnérabilité critique"
    else
        echo "⚠️ Image Collector: Vulnérabilités détectées"
    fi
fi

# ===== ANALYSE CODE =====
echo ""
echo "========================================"
echo "🔍 Analyse du code source (SAST)"
echo "========================================"

cd "$PROJECT_ROOT"
snyk code test --json > "$RESULTS_DIR/snyk_code.json" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Aucune vulnérabilité de code détectée"
else
    echo "⚠️ Vulnérabilités de code détectées"
    snyk code test 2>/dev/null | head -30
fi

# ===== RAPPORT FINAL =====
echo ""
echo "========================================"
echo "📊 RAPPORT FINAL"
echo "========================================"
echo "Résultats sauvegardés dans: $RESULTS_DIR"
echo ""
ls -la "$RESULTS_DIR"/*.json 2>/dev/null

echo ""
echo "========================================"
echo "✅ Analyse Snyk terminée"
echo "========================================"
