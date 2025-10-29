#!/bin/bash
set -e

echo "🚀 Fusion de toutes les branches GWD dans main"

# Vérifier que nous sommes sur la branche gwd-complete
current_branch=$(git branch --show-current)
if [ "$current_branch" != "gwd-complete" ]; then
    echo "⚠️ Vous n'êtes pas sur la branche gwd-complete!"
    echo "📌 Exécutez d'abord: git checkout gwd-complete"
    exit 1
fi

# Vérifier si tout est commité
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ Vous avez des modifications non commitées!"
    echo "📌 Commitez ou stashez d'abord ces changements"
    exit 1
fi

# Préparation pour la fusion dans main
echo "🔄 Passage à la branche main..."
git checkout main || git checkout master

echo "🔄 Fusion de gwd-complete dans main..."
git merge gwd-complete --no-edit

echo "✅ Fusion terminée! GWD est maintenant intégré dans la branche principale."
echo "🧪 Exécutez les tests pour vérifier l'intégration: cd src/python && python -m pytest gwd/test_imports.py -v"
