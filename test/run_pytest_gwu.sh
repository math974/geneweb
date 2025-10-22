#!/bin/bash
# Script de lancement rapide pour les tests pytest gwu
set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TESTS PYTEST GWU${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Création de l'environnement virtuel...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    echo -e "${YELLOW}Installation de pytest...${NC}"
    pip install pytest pytest-xdist > /dev/null 2>&1
    echo -e "${GREEN}✓ Environnement prêt${NC}"
    echo ""
else
    source .venv/bin/activate
fi

# Mode d'exécution (par défaut: normal)
MODE="${1:-normal}"

case "$MODE" in
    "quick")
        echo -e "${GREEN}Mode rapide: Tests de base uniquement${NC}"
        echo ""
        pytest -m gwu test/test_gwu_golden.py::TestGwuBasics -v
        ;;
    "verbose")
        echo -e "${GREEN}Mode verbeux: Tous les tests avec détails${NC}"
        echo ""
        pytest -m gwu test/test_gwu_golden.py -vv -s
        ;;
    "parallel")
        echo -e "${GREEN}Mode parallèle: Exécution multi-thread${NC}"
        echo ""
        pytest -m gwu test/test_gwu_golden.py -n auto -v
        ;;
    "collect")
        echo -e "${GREEN}Liste des tests disponibles:${NC}"
        echo ""
        pytest --collect-only -q test/test_gwu_golden.py | grep "test_"
        ;;
    *)
        echo -e "${GREEN}Mode normal: Tous les tests gwu${NC}"
        echo ""
        pytest -m gwu test/test_gwu_golden.py -v
        ;;
esac

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ TOUS LES TESTS RÉUSSIS${NC}"
else
    echo -e "${RED}❌ CERTAINS TESTS ONT ÉCHOUÉ${NC}"
fi

echo ""
echo -e "${BLUE}Commandes utiles:${NC}"
echo -e "  ${YELLOW}./test/run_pytest_gwu.sh quick${NC}     - Tests rapides"
echo -e "  ${YELLOW}./test/run_pytest_gwu.sh verbose${NC}   - Tests verbeux"
echo -e "  ${YELLOW}./test/run_pytest_gwu.sh parallel${NC}  - Tests parallèles (⚠️  conflits possibles)"
echo -e "  ${YELLOW}./test/run_pytest_gwu.sh collect${NC}   - Lister les tests"
echo ""
echo -e "${YELLOW}Note:${NC} L'exécution séquentielle (mode normal) est recommandée pour éviter les conflits."
echo ""

exit $EXIT_CODE
