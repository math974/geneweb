#!/bin/bash
# Script de facilitation pour les tests golden master de gwd
#
# Usage:
#   ./test/gwd_test.sh record [scenarios...]
#   ./test/gwd_test.sh verify [scenarios...]
#   ./test/gwd_test.sh quick    # Vérification rapide (basic)
#   ./test/gwd_test.sh full     # Vérification complète (all)

set -e

# Répertoire racine du projet
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Configuration par défaut
BASE="${GWD_TEST_BASE:-galichet}"
DIST="${GWD_TEST_DIST:-./distribution}"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

error() {
    echo -e "${RED}[ERREUR]${NC} $1" >&2
    exit 1
}

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

check_requirements() {
    # Vérifier Python 3
    if ! command -v python3 &> /dev/null; then
        error "Python 3 est requis mais n'est pas installé"
    fi
    
    # Vérifier que la distribution existe
    if [ ! -f "$DIST/gw/gwd" ]; then
        error "gwd non trouvé dans $DIST/gw/. Exécutez 'make distrib' d'abord"
    fi
    
    # Vérifier que la base existe
    if [ ! -d "$DIST/bases/$BASE.gwb" ]; then
        error "La base $BASE.gwb n'existe pas dans $DIST/bases/"
    fi
}

cmd_record() {
    local scenarios="${1:-basic}"
    info "Enregistrement des golden masters pour: $scenarios"
    check_requirements
    python3 test/gwd_golden.py record --base "$BASE" --dist "$DIST" --scenarios $scenarios
}

cmd_verify() {
    local scenarios="${1:-basic}"
    info "Vérification des golden masters pour: $scenarios"
    check_requirements
    python3 test/gwd_golden.py verify --base "$BASE" --dist "$DIST" --scenarios $scenarios
}

cmd_quick() {
    info "Test rapide (scénarios basic uniquement)"
    cmd_verify "basic"
}

cmd_full() {
    info "Test complet (tous les scénarios)"
    cmd_verify "all"
}

cmd_help() {
    cat <<EOF
Usage: $0 <commande> [arguments]

Commandes:
  record [scenarios...]   Enregistrer les golden masters
  verify [scenarios...]   Vérifier contre les golden masters
  quick                   Vérification rapide (basic)
  full                    Vérification complète (all)
  help                    Afficher cette aide

Scénarios disponibles:
  basic     - Tests de base (homepage, search, statistics...)
  trees     - Arbres généalogiques
  person    - Pages de personnes
  lists     - Listes (naissances, décès, mariages...)
  admin     - Pages d'administration
  all       - Tous les scénarios

Variables d'environnement:
  GWD_TEST_BASE    Base de données à tester (défaut: galichet)
  GWD_TEST_DIST    Répertoire distribution (défaut: ./distribution)

Exemples:
  # Enregistrer les scénarios de base
  $0 record basic

  # Vérifier tous les scénarios
  $0 verify all

  # Test rapide
  $0 quick

  # Test complet
  $0 full

  # Utiliser une autre base
  GWD_TEST_BASE=autre_base $0 verify basic

EOF
}

# Traitement de la commande
case "${1:-help}" in
    record)
        shift
        cmd_record "$*"
        ;;
    verify)
        shift
        cmd_verify "$*"
        ;;
    quick)
        cmd_quick
        ;;
    full)
        cmd_full
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        error "Commande inconnue: $1. Utilisez '$0 help' pour l'aide"
        ;;
esac

