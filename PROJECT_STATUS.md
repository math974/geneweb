# 📊 Status du Projet GeneWeb Python

**Dernière mise à jour**: 8 octobre 2025  
**Objectif**: Réécrire `gwd` (OCaml) en Python avec architecture clean

---

## 🎯 Vue d'ensemble

### Objectif
Recréer le serveur web GeneWeb (`gwd`) en Python moderne avec :
- ✅ Architecture clean/hexagonal
- ✅ Tests automatisés (44 tests existants)
- ✅ Comportement identique au binaire OCaml
- ✅ Code maintenable et évolutif

### Approche
**Test-Driven Rewrite (TDR)** : Les 44 tests existants valident chaque étape.

---

## 📈 Progression Globale

```
██████░░░░░░░░░░░░░░░░ 16% (Phase 0/5)

Phase 0 : Infrastructure       ████████████████████ 100% ✅
Phase 1 : Routing HTTP          ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Phase 2 : Base de données       ░░░░░░░░░░░░░░░░░░░░   0%
Phase 3 : Templates & Rendering ░░░░░░░░░░░░░░░░░░░░   0%
Phase 4 : Authentification      ░░░░░░░░░░░░░░░░░░░░   0%
Phase 5 : Features avancées     ░░░░░░░░░░░░░░░░░░░░   0%
```

---

## ✅ Phase 0 : Infrastructure (TERMINÉE)

**Durée**: ~1h  
**Status**: ✅ 100% complète

### Livrables
- ✅ Structure projet (`geneweb-python/`)
- ✅ Configuration Pydantic (50+ options gwd)
- ✅ Application FastAPI de base
- ✅ Serveur uvicorn
- ✅ CLI complet (argparse)
- ✅ Package installable (`pip install -e .`)
- ✅ Tests smoke passés

### Fichiers créés
```
geneweb-python/
├── src/geneweb/
│   ├── adapters/config/settings.py       # Configuration
│   ├── adapters/web/app.py               # FastAPI app
│   ├── infrastructure/server/            # Serveur
│   ├── cli/main.py                       # CLI
│   └── domain/                           # (à venir)
├── pyproject.toml                        # Package config
├── README.md                             # Documentation
└── .gitignore                            # Git config
```

### Validation
```bash
cd geneweb-python
source venv/bin/activate
python -m geneweb.cli.main --help
# ✅ Toutes les options affichées

python -m geneweb.cli.main -p 9999 -bd ../distribution/bases -hd ../distribution/gw &
curl http://localhost:9999/health
# ✅ {"status":"ok","version":"0.1.0"}
```

---

## ⏳ Phase 1 : Routing HTTP (EN COURS)

**Durée estimée**: 2-3h  
**Status**: ⏳ 0% - À démarrer  
**Tests visés**: 5/44

### Objectifs
1. Routes HTTP principales
2. Middleware (logging, errors)
3. Premiers golden masters

### Tâches
- [ ] Créer `PersonRepository` interface
- [ ] Route `/{base}/person?i=N`
- [ ] Route `/{base}/family?i=N`
- [ ] Route `/{base}/desc?i=N`
- [ ] Tests `basic_*` passent

---

## 📊 Tests Coverage

### Status actuel : 0/44 ✅

| Catégorie | Tests | Passés | % |
|-----------|-------|--------|---|
| **Golden Master** | 25 | 0 | 0% |
| - Basic | 8 | 0 | 0% |
| - Trees | 4 | 0 | 0% |
| - Person | 3 | 0 | 0% |
| - Lists | 3 | 0 | 0% |
| - Admin | 2 | 0 | 0% |
| - Auth | 5 | 0 | 0% |
| **Integration** | 19 | 0 | 0% |
| - Network | 4 | 0 | 0% |
| - Mode | 2 | 0 | 0% |
| - Limits | 3 | 0 | 0% |
| - Files | 2 | 0 | 0% |
| - Logs | 2 | 0 | 0% |
| - Cache | 1 | 0 | 0% |
| - Advanced | 5 | 0 | 0% |
| **TOTAL** | **44** | **0** | **0%** |

---

## 🚀 Prochaines Étapes

### Immédiat (aujourd'hui)
1. **Phase 1 : Routing HTTP**
   - Implémenter routes de base
   - Passer premiers tests

### Court terme (cette semaine)
1. **Phase 2 : Base de données**
   - Lecture format `.gwb`
   - Entities domain

### Moyen terme (semaine prochaine)
1. **Phase 3 : Templates**
   - Jinja2 templates
   - Golden masters passent

---

## 📚 Documentation

### Documents créés
- ✅ [ARCHITECTURE_ANALYSIS.md](./ARCHITECTURE_ANALYSIS.md) - Analyse architecture
- ✅ [REWRITE_STRATEGY.md](./REWRITE_STRATEGY.md) - Stratégie de réécriture
- ✅ [PHASE_0_COMPLETE.md](./PHASE_0_COMPLETE.md) - Phase 0 recap
- ✅ [geneweb-python/README.md](./geneweb-python/README.md) - Doc projet

### Tests existants
- ✅ [test/gwd_golden.py](./test/gwd_golden.py) - Golden master tests
- ✅ [test/gwd_integration_tests.py](./test/gwd_integration_tests.py) - Integration tests
- ✅ [test/run_all_tests.sh](./test/run_all_tests.sh) - Runner global

---

## 🔧 Stack Technique

### Production
- **FastAPI** - Web framework
- **uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Jinja2** - Templates
- **structlog** - Logging

### Development
- **pytest** - Testing
- **mypy** - Type checking
- **ruff** - Linting
- **black** - Formatting

---

## 📝 Commandes Utiles

### Développement
```bash
# Activer environnement
cd geneweb-python
source venv/bin/activate

# Lancer serveur
python -m geneweb.cli.main -p 2317 -bd ../distribution/bases -hd ../distribution/gw

# Tests
pytest
ruff src/
mypy src/
```

### Validation complète
```bash
# Tests OCaml vs Python (quand implémenté)
cd ..
./test/run_all_tests.sh
```

---

## 🎯 Critères de succès

### Fonctionnel
- [ ] 44/44 tests passent
- [ ] Output HTML identique
- [ ] Toutes options CLI supportées
- [ ] Performance acceptable (<2x OCaml)

### Qualité
- [ ] Architecture clean
- [ ] 100% type hints
- [ ] >80% couverture tests
- [ ] Code formaté

---

## 📞 Contacts & Resources

- **Projet OCaml** : `/Users/lucasmaelarnassalom/Project/geneweb/`
- **Projet Python** : `/Users/lucasmaelarnassalom/Project/geneweb/geneweb-python/`
- **Tests** : `/Users/lucasmaelarnassalom/Project/geneweb/test/`

---

**Status**: Phase 0 ✅ | Prochaine: Phase 1 ⏳ | Tests: 0/44 passés
