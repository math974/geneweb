# Couverture des options GWD par les tests Golden Master

## 📊 Vue d'ensemble

**Total des options gwd** : 36 options  
**Options actuellement testées** : 8 options (22%)  
**Options testables via golden master** : 15 options (42%)  
**Options non testables** via golden master : 21 options (58%)

---

## ✅ Options actuellement testées (8/36)

### Options de base (déjà utilisées)
| Option | Status | Utilisation | Scénarios |
|--------|--------|-------------|-----------|
| `-p <NUMBER>` | ✅ Testé | Port serveur | Tous les tests |
| `-bd <DIR>` | ✅ Testé | Répertoire des bases | Tous les tests |
| `-hd <DIR>` | ✅ Testé | Répertoire templates | Tous les tests |
| `-log <FILE>` | ✅ Testé | Fichier de log | Tous les tests |
| `-conn_tmout <SEC>` | ✅ Testé | Timeout connexion | Tous les tests (3600s) |
| `-robot_xcl <CNT>,<SEC>` | ✅ Testé | Exclusion robots | Tous les tests (10000,1) |

### Options spéciales
| Option | Status | Utilisation | Scénarios |
|--------|--------|-------------|-----------|
| `-predictable_mode` | ✅ Testé | Mode prédictible | Tous les tests |
| `-n_workers` | ✅ Testé | Nombre de workers | Tous les tests (0=synchrone) |

---

## 🎯 Options testables via Golden Master (15 options)

### Priorité HAUTE - Impact visible sur HTML

#### 1. Internationalisation
| Option | Impact | Difficulté | Golden Masters |
|--------|--------|------------|----------------|
| `-lang <LANG>` | **Élevé** | Faible | Tester fr, en, de |
| `-blang` | Moyen | Moyenne | Tester détection navigateur |

**Scénarios suggérés :**
- `lang_fr` : Page d'accueil en français
- `lang_en` : Page d'accueil en anglais
- `lang_de` : Page d'accueil en allemand
- `blang_auto` : Détection automatique langue navigateur

#### 2. Authentification et sécurité
| Option | Impact | Difficulté | Golden Masters |
|--------|--------|------------|----------------|
| `-auth <FILE>` | **Élevé** | Moyenne | Accès restreint |
| `-friend <PASSWD>` | **Élevé** | Moyenne | Password ami |
| `-wizard <PASSWD>` | **Élevé** | Moyenne | Password wizard |
| `-digest` | Moyen | Haute | Auth Digest |
| `-wjf` | Moyen | Faible | Wizard=Friend |

**Scénarios suggérés :**
- `auth_no_auth` : 401 sans authentification
- `auth_valid` : 200 avec credentials valides
- `auth_invalid` : 401 avec mauvais credentials
- `auth_friend` : Accès avec friend password
- `auth_wizard` : Accès avec wizard password

#### 3. Interface et affichage
| Option | Impact | Difficulté | Golden Masters |
|--------|--------|------------|----------------|
| `-setup_link` | Moyen | Faible | Lien gwsetup visible |
| `-images_url <URL>` | Moyen | Faible | URLs d'images modifiées |
| `-allowed_tags <FILE>` | Faible | Moyenne | Tags HTML filtrés |

**Scénarios suggérés :**
- `setup_link_on` : Vérifier présence lien gwsetup
- `setup_link_off` : Vérifier absence lien gwsetup
- `images_custom_url` : URLs d'images personnalisées
- `allowed_tags_restricted` : HTML avec tags restreints

### Priorité MOYENNE - Impact partiel

#### 4. Ressources et chemins
| Option | Impact | Difficulté | Golden Masters |
|--------|--------|------------|----------------|
| `-images_dir <DIR>` | Faible | Faible | Chemins images relatifs |
| `-add_lexicon <FILE>` | Faible | Moyenne | Lexique additionnel |
| `-cache_langs` | Faible | Haute | Performance cache |

**Scénarios suggérés :**
- `images_custom_dir` : Répertoire d'images personnalisé
- `lexicon_custom` : Termes personnalisés du lexique

### Priorité FAIBLE - Impact minimal sur HTML

#### 5. Logging et debug
| Option | Impact | Difficulté | Golden Masters |
|--------|--------|------------|----------------|
| `-debug` | Faible | Faible | Messages debug HTML |
| `-trace_failed_passwd` | Aucun | Faible | Logs uniquement |

---

## ❌ Options NON testables via Golden Master (21 options)

Ces options affectent la configuration serveur mais pas le rendu HTML :

### Configuration réseau
| Option | Raison |
|--------|--------|
| `-a <ADDRESS>` | Bind address (pas d'impact HTML) |
| `-only <ADDRESS>` | Restriction IP (pas d'impact HTML) |
| `-no_host_address` | Reverse DNS (pas d'impact HTML) |
| `-redirect <ADDR>` | Redirection service (pas d'impact HTML) |

### Mode d'exécution
| Option | Raison |
|--------|--------|
| `-cgi` | Mode CGI (différent environnement) |
| `-daemon` | Mode daemon (détaché du terminal) |

### Limites et timeouts
| Option | Raison |
|--------|--------|
| `-login_tmout <SEC>` | Timeout (nécessite tests temporels) |
| `-max_clients <NUM>` | Limite clients (nécessite tests de charge) |
| `-min_disp_req` | Trace robots (logs uniquement) |

### Fichiers et verrouillage
| Option | Raison |
|--------|--------|
| `-nolock` | Verrouillage fichiers (pas d'impact HTML) |
| `-wd <DIR>` | Répertoire travail (pas d'impact HTML) |

### Logging
| Option | Raison |
|--------|--------|
| `-log_level <N>` | Niveau syslog (logs uniquement) |

### Plugins
| Option | Raison |
|--------|--------|
| `-plugin <FILE>` | Chargement plugin (fonctionnalité variable) |
| `-plugins <DIR>` | Chargement plugins (fonctionnalité variable) |

---

## 📈 Plan d'implémentation recommandé

### Phase 1 : Langues (Priorité HAUTE)
**Effort** : 2-3 heures  
**Valeur** : Très élevée  
**Tests** : 5 scénarios

```python
"i18n": [
    {"name": "lang_fr", "lang": "fr", ...},
    {"name": "lang_en", "lang": "en", ...},
    {"name": "lang_de", "lang": "de", ...},
    {"name": "blang_fr", "blang": True, "accept_lang": "fr", ...},
    {"name": "blang_en", "blang": True, "accept_lang": "en", ...},
]
```

### Phase 2 : Authentification (Priorité HAUTE)
**Effort** : 3-4 heures  
**Valeur** : Très élevée  
**Tests** : 8 scénarios

```python
"auth": [
    {"name": "auth_no_auth", "expect_status": 401, ...},
    {"name": "auth_valid", "credentials": {...}, ...},
    {"name": "auth_invalid", "expect_status": 401, ...},
    {"name": "auth_friend", "friend_access": True, ...},
    {"name": "auth_wizard", "wizard_access": True, ...},
    {"name": "auth_digest", "use_digest": True, ...},
    {"name": "auth_wjf", "wizard_just_friend": True, ...},
]
```

### Phase 3 : Interface (Priorité MOYENNE)
**Effort** : 2 heures  
**Valeur** : Moyenne  
**Tests** : 4 scénarios

```python
"interface": [
    {"name": "setup_link_visible", "setup_link": True, ...},
    {"name": "images_custom_url", "images_url": "http://cdn.example.com", ...},
    {"name": "allowed_tags", "allowed_tags": "fixtures/allowed_tags.txt", ...},
]
```

### Phase 4 : Ressources (Priorité FAIBLE)
**Effort** : 1-2 heures  
**Valeur** : Faible  
**Tests** : 2 scénarios

```python
"resources": [
    {"name": "custom_lexicon", "add_lexicon": "fixtures/custom_lexicon.txt", ...},
    {"name": "images_dir", "images_dir": "custom/images", ...},
]
```

---

## 🚀 Commandes de test par phase

### Phase 1 : Langues
```bash
# Enregistrer
pytest test/test_gwd_golden.py --record -m i18n

# Vérifier
pytest test/test_gwd_golden.py -v -m i18n
```

### Phase 2 : Authentification
```bash
# Enregistrer
pytest test/test_gwd_golden.py --record -m auth

# Vérifier
pytest test/test_gwd_golden.py -v -m auth
```

### Phase 3 : Interface
```bash
# Enregistrer
pytest test/test_gwd_golden.py --record -m interface

# Vérifier
pytest test/test_gwd_golden.py -v -m interface
```

---

## 📊 Statistiques finales prévues

Après implémentation complète des 4 phases :

| Métrique | Valeur |
|----------|--------|
| **Options testées** | 23/36 (64%) |
| **Scénarios de test** | ~50 scénarios |
| **Couverture fonctionnelle** | ~80% des fonctionnalités visibles |
| **Temps d'exécution estimé** | ~2-3 minutes pour tous les tests |

---

## 🎯 Recommandation

**Ordre d'implémentation suggéré :**

1. **Phase 1 (Langues)** - Impact immédiat, facile à tester
2. **Phase 2 (Authentification)** - Critique pour la sécurité
3. **Phase 3 (Interface)** - Améliorations UX
4. **Phase 4 (Ressources)** - Nice to have

**ROI maximum** : Implémenter Phases 1 et 2 = 80% de la valeur pour 50% de l'effort
