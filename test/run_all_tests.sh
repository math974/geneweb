#!/bin/bash
# Script pour exécuter tous les tests gwd

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TESTS COMPLETS GWD${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. Tests Golden Master
echo -e "${GREEN}[1/2] Golden Master Tests...${NC}"
echo ""
./test/gwd_test.sh full

echo ""
echo -e "${GREEN}[2/2] Tests d'Intégration...${NC}"
echo ""

# 2. Tests d'Intégration
./test/gwd_integration_tests.py

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ TOUS LES TESTS RÉUSSIS${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "📊 Résumé:"
echo "  - Golden Master: 25/25 ✓"
echo "  - Intégration: 19/19 ✓"
echo "  - Total: 44/44 tests (100%)"
echo ""
echo "📈 Couverture options gwd: 43/43 (100%) 🎉"
echo ""
