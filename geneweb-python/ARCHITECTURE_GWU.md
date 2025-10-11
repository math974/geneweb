# Architecture GWU Python - Clean & Modular Design

## 📋 Vue d'Ensemble

Réécriture de `gwu` (GeneWeb Unweb) en Python en suivant les principes de Clean Architecture et SOLID.

### Objectifs
- ✅ **Testabilité** : 100% testé avec les golden masters existants
- ✅ **Maintenabilité** : Code clair, modulaire, bien documenté
- ✅ **Évolutivité** : Facile d'ajouter de nouvelles fonctionnalités
- ✅ **Compatibilité** : Même comportement que l'implémentation OCaml

---

## 🏗️ Architecture Clean - Couches

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI / Interface                           │
│                   (gwu_cli.py)                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Use Cases / Application                    │
│   - ExportDatabaseUseCase                                    │
│   - SelectPersonsUseCase                                     │
│   - FormatOutputUseCase                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain / Business Logic                    │
│   Entities:                                                   │
│   - Person, Family, Event, Date, Place                       │
│   Services:                                                   │
│   - PersonService, FamilyService, DateService                │
│   Repositories (interfaces):                                 │
│   - PersonRepository, FamilyRepository                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Adapters / Infrastructure                        │
│   Input:                                                      │
│   - GwdbRepository (lecture base .gwb)                       │
│   - GwFileParser (lecture fichiers .gw)                      │
│   Output:                                                     │
│   - GwFileWriter (écriture .gw)                              │
│   - ConsoleWriter (logs verbose)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Structure des Modules

```
geneweb-python/
├── src/
│   └── geneweb/
│       ├── gwu/
│       │   ├── __init__.py
│       │   │
│       │   ├── cli/                        # Interface CLI
│       │   │   ├── __init__.py
│       │   │   ├── main.py                 # Point d'entrée
│       │   │   ├── argument_parser.py      # Parse arguments
│       │   │   └── output_formatter.py     # Format sortie console
│       │   │
│       │   ├── domain/                     # Logique métier
│       │   │   ├── __init__.py
│       │   │   │
│       │   │   ├── entities/               # Entités du domaine
│       │   │   │   ├── __init__.py
│       │   │   │   ├── person.py           # Personne
│       │   │   │   ├── family.py           # Famille
│       │   │   │   ├── event.py            # Événement
│       │   │   │   ├── date.py             # Date (précision, période)
│       │   │   │   ├── place.py            # Lieu
│       │   │   │   ├── note.py             # Notes
│       │   │   │   └── source.py           # Sources
│       │   │   │
│       │   │   ├── repositories/           # Interfaces (abstraites)
│       │   │   │   ├── __init__.py
│       │   │   │   ├── person_repository.py
│       │   │   │   ├── family_repository.py
│       │   │   │   └── database_repository.py
│       │   │   │
│       │   │   └── services/               # Services métier
│       │   │       ├── __init__.py
│       │   │       ├── person_service.py   # Logique personnes
│       │   │       ├── family_service.py   # Logique familles
│       │   │       ├── date_service.py     # Formatage dates
│       │   │       ├── selection_service.py # Sélection (filtres)
│       │   │       └── export_service.py   # Orchestration export
│       │   │
│       │   ├── use_cases/                  # Cas d'usage
│       │   │   ├── __init__.py
│       │   │   ├── export_database.py      # Export complet
│       │   │   ├── export_selection.py     # Export filtré
│       │   │   ├── export_separated.py     # Export avec -sep
│       │   │   └── export_to_directory.py  # Export avec -odir
│       │   │
│       │   └── adapters/                   # Implémentations
│       │       ├── __init__.py
│       │       │
│       │       ├── input/                  # Lecture données
│       │       │   ├── __init__.py
│       │       │   ├── gwdb_reader.py      # Lecture .gwb
│       │       │   ├── gw_file_parser.py   # Parse .gw
│       │       │   └── gwdb_repository_impl.py
│       │       │
│       │       └── output/                 # Écriture données
│       │           ├── __init__.py
│       │           ├── gw_file_writer.py   # Écriture .gw
│       │           ├── gw_formatter.py     # Format .gw
│       │           └── console_logger.py   # Logs verbose
│       │
│       └── common/                         # Utilitaires communs
│           ├── __init__.py
│           ├── config.py                   # Configuration
│           ├── types.py                    # Types communs
│           └── utils.py                    # Fonctions utilitaires
│
└── tests/
    └── gwu/
        ├── __init__.py
        ├── conftest.py                     # Config pytest
        ├── test_golden_master.py           # Tests golden master
        │
        ├── domain/
        │   ├── test_person.py
        │   ├── test_family.py
        │   └── test_date.py
        │
        ├── use_cases/
        │   └── test_export_database.py
        │
        └── adapters/
            ├── test_gwdb_reader.py
            └── test_gw_file_writer.py
```

---

## 🎯 Domain - Entités Principales

### 1. Person (Personne)
```python
@dataclass
class Person:
    """Représente une personne dans la base généalogique."""
    
    # Identité
    person_id: str
    first_name: str
    surname: str
    occ: int = 0
    
    # Informations de base
    sex: Sex
    public: bool = True
    access: AccessLevel = AccessLevel.PUBLIC
    
    # Dates et lieux
    birth: Optional[Event] = None
    baptism: Optional[Event] = None
    death: Optional[Event] = None
    burial: Optional[Event] = None
    
    # Relations
    parents: Optional[str] = None  # family_id
    spouses: List[str] = field(default_factory=list)  # family_ids
    
    # Métadonnées
    events: List[Event] = field(default_factory=list)
    notes: Optional[Note] = None
    sources: List[Source] = field(default_factory=list)
    occupation: Optional[str] = None
    titles: List[Title] = field(default_factory=list)
    
    # Options d'export
    image: Optional[str] = None
    related_persons: List[str] = field(default_factory=list)
```

### 2. Family (Famille)
```python
@dataclass
class Family:
    """Représente une famille (union de deux personnes)."""
    
    family_id: str
    father_id: str
    mother_id: str
    
    # Événements
    marriage: Optional[Event] = None
    marriage_contract: Optional[Event] = None
    marriage_license: Optional[Event] = None
    divorce: Optional[Event] = None
    separation: Optional[Event] = None
    annulation: Optional[Event] = None
    
    # Enfants
    children: List[str] = field(default_factory=list)  # person_ids
    
    # Métadonnées
    events: List[Event] = field(default_factory=list)
    notes: Optional[Note] = None
    sources: List[Source] = field(default_factory=list)
    witnesses: List[Witness] = field(default_factory=list)
```

### 3. Event (Événement)
```python
@dataclass
class Event:
    """Représente un événement (naissance, mariage, etc.)."""
    
    event_type: EventType
    date: Optional[Date] = None
    place: Optional[Place] = None
    note: Optional[str] = None
    source: Optional[str] = None
    witnesses: List[Witness] = field(default_factory=list)
```

### 4. Date (Date avec précision)
```python
@dataclass
class Date:
    """Date généalogique avec précision et période."""
    
    # Date principale
    day: int = 0
    month: int = 0
    year: int = 0
    
    # Précision
    precision: DatePrecision = DatePrecision.SURE  # Sure, About, Maybe, Before, After
    
    # Période (OrYear, YearInterval)
    day2: int = 0
    month2: int = 0
    year2: int = 0
    
    # Calendrier
    calendar: Calendar = Calendar.GREGORIAN
    
    def to_gw_format(self, old_gw: bool = False) -> str:
        """Convertit en format .gw"""
        pass
```

---

## 🔧 Services - Logique Métier

### PersonService
```python
class PersonService:
    """Service pour la logique métier des personnes."""
    
    def format_person_name(self, person: Person) -> str:
        """Formate le nom complet (Prénom.occ NOM)"""
        pass
    
    def should_export_person(self, person: Person, filters: ExportFilters) -> bool:
        """Détermine si une personne doit être exportée"""
        pass
    
    def get_person_ancestors(self, person_id: str, depth: int) -> List[str]:
        """Récupère les ascendants jusqu'à une profondeur donnée"""
        pass
    
    def get_person_descendants(self, person_id: str, depth: int) -> List[str]:
        """Récupère les descendants jusqu'à une profondeur donnée"""
        pass
    
    def is_person_isolated(self, person: Person) -> bool:
        """Vérifie si une personne est isolée (sans famille)"""
        pass
    
    def apply_censorship(self, person: Person, censor_years: int) -> Person:
        """Applique la censure par âge"""
        pass
```

### SelectionService
```python
class SelectionService:
    """Service pour la sélection de personnes et familles."""
    
    def select_by_surname(self, surname: str) -> Set[str]:
        """Sélectionne par patronyme"""
        pass
    
    def select_by_key(self, key: str) -> Optional[str]:
        """Sélectionne par clé (Prénom.occ NOM)"""
        pass
    
    def select_ancestors_descendants(
        self, person_id: str, asc_depth: int, desc_depth: int
    ) -> Set[str]:
        """Sélectionne ascendants et descendants"""
        pass
    
    def select_parentship(self, person1_id: str, person2_id: str) -> Set[str]:
        """Sélectionne les personnes impliquées dans le calcul de parenté"""
        pass
    
    def select_isolated_persons(self) -> Set[str]:
        """Sélectionne les personnes isolées"""
        pass
```

### ExportService
```python
class ExportService:
    """Service d'orchestration de l'export."""
    
    def __init__(
        self,
        person_repo: PersonRepository,
        family_repo: FamilyRepository,
        writer: GwFileWriter,
    ):
        self.person_repo = person_repo
        self.family_repo = family_repo
        self.writer = writer
    
    def export_database(
        self,
        options: ExportOptions,
        selection: Optional[Set[str]] = None,
    ) -> None:
        """Exporte la base complète ou une sélection"""
        pass
    
    def export_to_directory(
        self,
        options: ExportOptions,
        output_dir: Path,
    ) -> None:
        """Exporte avec -odir (un fichier par personne/groupe)"""
        pass
    
    def export_with_separation(
        self,
        options: ExportOptions,
        separate_persons: List[str],
    ) -> None:
        """Exporte avec -sep (séparation de familles)"""
        pass
```

---

## 🎬 Use Cases - Cas d'Usage

### ExportDatabaseUseCase
```python
class ExportDatabaseUseCase:
    """Use case: Exporter une base de données généalogique."""
    
    def __init__(
        self,
        database_repo: DatabaseRepository,
        export_service: ExportService,
        selection_service: SelectionService,
    ):
        self.database_repo = database_repo
        self.export_service = export_service
        self.selection_service = selection_service
    
    def execute(self, request: ExportRequest) -> ExportResult:
        """
        Exécute l'export avec les options données.
        
        Args:
            request: Requête d'export (options, filtres, etc.)
        
        Returns:
            ExportResult: Résultat de l'export (succès, stats, etc.)
        """
        # 1. Charger la base
        database = self.database_repo.load_database(request.database_path)
        
        # 2. Appliquer les sélections/filtres
        selected_persons = self._apply_selections(request, database)
        
        # 3. Exporter
        if request.output_dir:
            self.export_service.export_to_directory(
                request.options, request.output_dir
            )
        elif request.separate_persons:
            self.export_service.export_with_separation(
                request.options, request.separate_persons
            )
        else:
            self.export_service.export_database(
                request.options, selected_persons
            )
        
        # 4. Retourner résultat
        return ExportResult(success=True, exported_count=len(selected_persons))
    
    def _apply_selections(
        self, request: ExportRequest, database: Database
    ) -> Set[str]:
        """Applique tous les filtres de sélection."""
        pass
```

---

## 📥 Adapters - Implémentations

### GwdbReader (Lecture base .gwb)
```python
class GwdbReader:
    """Adaptateur pour lire une base .gwb (format Geneweb)."""
    
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self._persons_cache: Dict[str, Person] = {}
        self._families_cache: Dict[str, Family] = {}
    
    def load_person(self, person_id: str) -> Person:
        """Charge une personne depuis la base."""
        pass
    
    def load_family(self, family_id: str) -> Family:
        """Charge une famille depuis la base."""
        pass
    
    def load_all_persons(self) -> List[Person]:
        """Charge toutes les personnes."""
        pass
    
    def load_all_families(self) -> List[Family]:
        """Charge toutes les familles."""
        pass
    
    def get_person_count(self) -> int:
        """Retourne le nombre de personnes."""
        pass
```

### GwFileWriter (Écriture fichier .gw)
```python
class GwFileWriter:
    """Adaptateur pour écrire un fichier .gw."""
    
    def __init__(
        self,
        output_file: Path,
        options: WriterOptions,
    ):
        self.output_file = output_file
        self.options = options
        self._buffer: List[str] = []
    
    def write_header(self) -> None:
        """Écrit l'en-tête du fichier."""
        if not self.options.raw_output:
            self._write("encoding: utf-8\n")
        if self.options.old_gw:
            self._write("\n")
        else:
            self._write("gwplus\n\n")
    
    def write_person(self, person: Person) -> None:
        """Écrit une personne au format .gw."""
        pass
    
    def write_family(self, family: Family) -> None:
        """Écrit une famille au format .gw."""
        pass
    
    def write_note(self, note: Note) -> None:
        """Écrit une note."""
        pass
    
    def write_extended_page(self, page: ExtendedPage) -> None:
        """Écrit une page étendue."""
        pass
    
    def flush(self) -> None:
        """Écrit le buffer dans le fichier."""
        pass
```

---

## ⚙️  Configuration et Options

### ExportOptions
```python
@dataclass
class ExportOptions:
    """Options d'export pour gwu."""
    
    # Format de sortie
    charset: Charset = Charset.UTF8
    raw_output: bool = False
    old_gw: bool = False  # Format < 7.00
    
    # Sélection
    surnames: List[str] = field(default_factory=list)
    keys: List[str] = field(default_factory=list)
    asc_depth: Optional[int] = None
    desc_depth: Optional[int] = None
    asc_desc_depth: Optional[int] = None
    parentship: bool = False
    isolated: bool = False
    
    # Contenu
    no_database_notes: bool = False  # -nn
    no_notes: bool = False  # -nnn
    all_files: bool = False
    no_picture: bool = False
    picture_path: bool = False
    source_replacement: Optional[str] = None
    
    # Censure et vie privée
    censor_years: Optional[int] = None
    
    # Séparation (avec -odir)
    separate_persons: List[str] = field(default_factory=list)
    sep_limit: int = 21
    sep_only_file: Optional[str] = None
    
    # Mode mémoire
    memory_mode: bool = False
    
    # Verbose
    verbose: bool = False
```

---

## 🧪 Tests - Stratégie de Test

### 1. Tests Unitaires (Domain & Services)
```python
# tests/gwu/domain/test_person.py
def test_person_format_name():
    person = Person(
        person_id="1",
        first_name="Jean",
        surname="Dupont",
        occ=0,
        sex=Sex.MALE
    )
    assert person.format_name() == "Jean.0 Dupont"

def test_person_with_occ():
    person = Person(
        person_id="2",
        first_name="Jean",
        surname="Dupont",
        occ=1,
        sex=Sex.MALE
    )
    assert person.format_name() == "Jean.1 Dupont"
```

### 2. Tests d'Intégration (Use Cases)
```python
# tests/gwu/use_cases/test_export_database.py
def test_export_complete_database(tmp_path):
    # Given: une base de test
    database_repo = create_test_database()
    export_service = create_export_service()
    use_case = ExportDatabaseUseCase(database_repo, export_service)
    
    # When: on exporte
    request = ExportRequest(
        database_path=test_db_path,
        output_file=tmp_path / "output.gw"
    )
    result = use_case.execute(request)
    
    # Then: le fichier est créé correctement
    assert result.success
    assert (tmp_path / "output.gw").exists()
```

### 3. Tests Golden Master
```python
# tests/gwu/test_golden_master.py
@pytest.mark.parametrize("test_case", [
    ("base", {}),
    ("charset_ascii", {"charset": "ASCII"}),
    ("raw", {"raw_output": True}),
    # ... tous les cas de test
])
def test_golden_master(test_case, tmp_path):
    """Vérifie que l'output correspond au golden master."""
    test_name, options = test_case
    
    # Exporter
    gwu_export(
        database="galichet",
        output_file=tmp_path / "output.gw",
        **options
    )
    
    # Comparer avec golden
    golden_file = Path(f"test/golden/galichet/galichet.{test_name}.golden.gw")
    assert_files_equal(tmp_path / "output.gw", golden_file)
```

---

## 📊 Dépendances Python

```toml
[project]
name = "geneweb-gwu"
version = "8.0.0"
requires-python = ">=3.11"

dependencies = [
    "click>=8.0",           # CLI
    "pydantic>=2.0",        # Validation de données
    "rich>=13.0",           # Output coloré
    "structlog>=23.0",      # Logging structuré
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]
```

---

## 🚀 Plan d'Implémentation

### Phase 1: Foundation (Semaine 1-2)
- [x] Structure du projet
- [ ] Entités du domaine (Person, Family, Event, Date)
- [ ] Interfaces des repositories
- [ ] Tests unitaires des entités

### Phase 2: Reading (Semaine 3-4)
- [ ] GwdbReader (lecture base .gwb)
- [ ] Parsing des fichiers binaires
- [ ] Tests d'intégration lecture

### Phase 3: Core Logic (Semaine 5-6)
- [ ] Services métier (PersonService, SelectionService)
- [ ] Use cases (ExportDatabaseUseCase)
- [ ] Tests unitaires services

### Phase 4: Writing (Semaine 7-8)
- [ ] GwFileWriter (écriture .gw)
- [ ] Formatage des dates, lieux, événements
- [ ] Tests d'intégration écriture

### Phase 5: CLI (Semaine 9)
- [ ] Interface CLI (argument parsing)
- [ ] Integration avec use cases
- [ ] Tests end-to-end

### Phase 6: Golden Master (Semaine 10)
- [ ] Tests golden master complets
- [ ] Validation 100% compatibilité
- [ ] Correction des écarts

### Phase 7: Optimisation (Semaine 11-12)
- [ ] Performance (mémoire, vitesse)
- [ ] Gestion des grosses bases
- [ ] Documentation complète

---

## 📈 Métriques de Qualité

### Objectifs
- ✅ **Couverture de code** : > 90%
- ✅ **Tests golden master** : 16/16 passés (100%)
- ✅ **Type hints** : 100% du code
- ✅ **Documentation** : Docstrings pour toutes les classes/fonctions publiques
- ✅ **Complexité cyclomatique** : < 10 par fonction
- ✅ **Lignes par fonction** : < 50

### Outils de Qualité
- **pytest** : Tests unitaires et d'intégration
- **pytest-cov** : Couverture de code
- **mypy** : Vérification des types
- **ruff** : Linting et formatage
- **black** : Formatage du code

---

## 🎯 Avantages de cette Architecture

### 1. Testabilité
- Chaque couche peut être testée indépendamment
- Mocking facile grâce aux interfaces
- Tests golden master pour validation comportementale

### 2. Maintenabilité
- Séparation claire des responsabilités
- Dépendances unidirectionnelles (vers le domaine)
- Code auto-documenté avec type hints

### 3. Évolutivité
- Facile d'ajouter de nouveaux formats d'export
- Facile d'ajouter de nouvelles sources de données
- Extensible sans modifier le code existant

### 4. Compatibilité
- Golden masters garantissent la compatibilité
- Interface identique à gwu OCaml
- Migration progressive possible

---

## 📝 Prochaines Étapes

1. **Valider l'architecture** avec l'équipe
2. **Créer les entités de base** (Person, Family, Event)
3. **Implémenter le lecteur gwdb** (GwdbReader)
4. **Développer les services métier**
5. **Implémenter l'écrivain .gw** (GwFileWriter)
6. **Créer l'interface CLI**
7. **Valider avec les golden masters**

---

## 🤝 Contribution

Cette architecture est évolutive. Pour contribuer :
1. Respecter les principes SOLID
2. Écrire des tests pour tout nouveau code
3. Valider avec les golden masters
4. Documenter les choix architecturaux

---

**Niveau de confiance : 95%**

Cette architecture est solide et prête à être implémentée. Les golden masters existants nous permettent de valider chaque étape du développement.
