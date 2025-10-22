#!/usr/bin/env python3
"""
Tests Golden Master pytest pour gwu (GeneWeb Unification)

Ce module contient les tests de régression pour l'utilitaire gwu
en utilisant la méthodologie Golden Master avec pytest.

Usage:
    # Tous les tests gwu
    pytest -m gwu
    
    # Un scénario spécifique
    pytest test/test_gwu_golden.py::test_gwu_galichet_verify[default]
    
    # Tests verbeux
    pytest -vv -m gwu
    
    # Tests parallèles (avec pytest-xdist)
    pytest -m gwu -n auto
"""

import pytest
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

# Import des fonctions du module gwu_golden
from gwu_golden import (
    cmd_verify,
    build_scenario_suffix,
    gwu_extra_args,
)


def discover_gwu_scenarios(base: str) -> List[Dict[str, Any]]:
    """
    Découvre automatiquement tous les scénarios golden pour une base donnée.
    
    Parse les noms de fichiers golden du format:
        base.option1.option2.golden.gw
        
    Args:
        base: Nom de la base (ex: "galichet")
        
    Returns:
        Liste de dictionnaires contenant:
        - id: Identifiant du scénario
        - options: Dictionnaire des options parsées
    """
    golden_dir = Path("test") / "golden" / base
    if not golden_dir.exists():
        return []
    
    scenarios = []
    seen = set()
    
    for file in golden_dir.glob("*.golden.gw"):
        # Extraire le suffixe entre base et .golden.gw
        # Ex: galichet.charset-ASCII.golden.gw -> charset-ASCII
        stem = file.stem  # galichet.charset-ASCII.golden
        
        # Enlever .golden
        if stem.endswith(".golden"):
            stem = stem[:-7]
        
        # Enlever le nom de base
        if stem.startswith(f"{base}."):
            suffix = stem[len(base)+1:]
        elif stem == base:
            suffix = ""
        else:
            continue
        
        scenario_id = suffix if suffix else "default"
        
        if scenario_id in seen:
            continue
        seen.add(scenario_id)
        
        # Parser le suffixe pour extraire les options
        options = parse_scenario_suffix(suffix)
        
        scenarios.append({
            "id": scenario_id,
            "options": options,
        })
    
    # Trier par ID pour avoir un ordre prévisible
    scenarios.sort(key=lambda x: x["id"])
    
    return scenarios


def parse_scenario_suffix(suffix: str) -> Dict[str, Any]:
    """
    Parse le suffixe d'un scénario pour extraire les options gwu.
    
    Format attendu: "option1.option2.option3"
    Ex: "charset-ASCII.raw.a3" -> {charset: "ASCII", raw: True, asc: 3}
    
    Args:
        suffix: Suffixe du scénario (sans base ni .golden.gw)
        
    Returns:
        Dictionnaire des options gwu
        
    Note:
        Les options key-N et sep-N sont ignorées car elles nécessitent
        des valeurs spécifiques non récupérables depuis le nom de fichier.
        Les tests correspondants sont donc skippés.
    """
    options: Dict[str, Any] = {
        "charset": None,
        "raw": False,
        "surnames": None,
        "keys": None,
        "asc": None,
        "desc": None,
        "asc_desc": None,
        "parentship": False,
        "isolated": False,
        "nn": False,
        "nnn": False,
        "all_files": False,
        "nopicture": False,
        "picture_path": False,
        "source": None,
        "censor": None,
        "sep": None,
        "sep_limit": None,
        "sep_only_file": None,
        "old_gw": False,
        "mem": False,
        "_has_keys": False,  # Flag pour savoir si le scénario utilise des clés
        "_has_sep": False,   # Flag pour savoir si le scénario utilise des séparations
    }
    
    if not suffix:
        return options
    
    parts = suffix.split(".")
    
    for part in parts:
        # Charset
        if part.startswith("charset-"):
            options["charset"] = part.split("-", 1)[1]
        # Raw
        elif part == "raw":
            options["raw"] = True
        # Surnames
        elif part.startswith("s-"):
            surnames_str = part[2:]
            options["surnames"] = [s.replace("_", " ") for s in surnames_str.split("-")]
        # Keys - marquer mais ne pas parser
        elif part.startswith("key-"):
            options["_has_keys"] = True
        # Ascendance
        elif part.startswith("a") and part[1:].isdigit():
            options["asc"] = int(part[1:])
        # Descendance
        elif part.startswith("d") and part[1:].isdigit():
            options["desc"] = int(part[1:])
        # Asc+Desc
        elif part.startswith("ad") and part[2:].isdigit():
            options["asc_desc"] = int(part[2:])
        # Parentship
        elif part == "parentship":
            options["parentship"] = True
        # Isolated
        elif part == "isolated":
            options["isolated"] = True
        # No notes
        elif part == "nn":
            options["nn"] = True
        elif part == "nnn":
            options["nnn"] = True
        # All files
        elif part == "all_files":
            options["all_files"] = True
        # Pictures
        elif part == "nopicture":
            options["nopicture"] = True
        elif part == "picture_path":
            options["picture_path"] = True
        # Source
        elif part.startswith("source-"):
            options["source"] = part.split("-", 1)[1].replace("_", " ")
        # Censor
        elif part.startswith("c") and part[1:].isdigit():
            options["censor"] = int(part[1:])
        # Sep - marquer mais ne pas parser
        elif part.startswith("sep-"):
            options["_has_sep"] = True
        elif part.startswith("seplimit") and part[8:].isdigit():
            options["sep_limit"] = int(part[8:])
        elif part == "sepfile":
            options["sep_only_file"] = "sep_output.gw"
        # Old format
        elif part == "old_gw":
            options["old_gw"] = True
        # Memory
        elif part == "mem":
            options["mem"] = True
    
    return options


# ============================================================================
# TESTS PARAMÉTRÉS - Découverte automatique
# ============================================================================

@pytest.mark.gwu
@pytest.mark.parametrize(
    "scenario",
    [s["id"] for s in discover_gwu_scenarios("galichet")],
    ids=lambda s: s,
)
def test_gwu_galichet_verify(
    galichet_base: str,
    dist_dir: Path,
    scenario: str,
):
    """
    Test de régression gwu pour chaque scénario golden de la base galichet.
    
    Ce test:
    1. Reconstruit la base .gwb
    2. Exporte avec gwu selon les options du scénario
    3. Compare avec le fichier golden de référence
    4. Vérifie aussi les logs (-v)
    
    Args:
        galichet_base: Nom de la base (fixture)
        dist_dir: Répertoire distribution (fixture)
        scenario: ID du scénario (paramétré)
        
    Note:
        Les scénarios utilisant -key ou -sep sont skippés car ils nécessitent
        des valeurs spécifiques (clés de personnes, personnes à séparer)
        non récupérables depuis le nom du fichier golden.
    """
    # Récupérer les scénarios et trouver celui qui correspond
    scenarios = discover_gwu_scenarios("galichet")
    scenario_data = next((s for s in scenarios if s["id"] == scenario), None)
    
    if not scenario_data:
        pytest.fail(f"Scénario {scenario} non trouvé")
    
    options = scenario_data["options"]
    
    # Skip les scénarios qui nécessitent des clés ou séparations spécifiques
    if options.get("_has_keys"):
        pytest.skip(
            f"Scénario {scenario} nécessite des clés de personnes spécifiques "
            "non récupérables depuis le nom de fichier"
        )
    
    # Pour sep: on ne peut jamais reconstruire la liste des personnes à séparer
    # Même si sep_limit est présent, le fichier golden a été créé avec sep + sep_limit
    if options.get("_has_sep"):
        pytest.skip(
            f"Scénario {scenario} nécessite des personnes à séparer spécifiques "
            "non récupérables depuis le nom de fichier"
        )
    
    # Nettoyer les flags internes avant de passer à cmd_verify
    clean_options = {k: v for k, v in options.items() if not k.startswith("_")}
    
    # Exécuter la vérification
    exit_code = cmd_verify(
        base=galichet_base,
        dist_dir=dist_dir,
        ignore_trailing_space=True,
        **clean_options,
    )
    
    assert exit_code == 0, f"Vérification échouée pour le scénario '{scenario}'"


# ============================================================================
# TESTS EXPLICITES - Cas importants
# ============================================================================

@pytest.mark.gwu
class TestGwuBasics:
    """Tests de base pour gwu sans options."""
    
    def test_default_export(self, galichet_base: str, dist_dir: Path):
        """Export standard sans aucune option."""
        exit_code = cmd_verify(
            base=galichet_base,
            dist_dir=dist_dir,
            ignore_trailing_space=True,
            charset=None,
            raw=False,
            surnames=None,
            keys=None,
            asc=None,
            desc=None,
            asc_desc=None,
            parentship=False,
            isolated=False,
            nn=False,
            nnn=False,
            all_files=False,
            nopicture=False,
            picture_path=False,
            source=None,
            censor=None,
            sep=None,
            sep_limit=None,
            sep_only_file=None,
            old_gw=False,
            mem=False,
        )
        assert exit_code == 0


@pytest.mark.gwu
class TestGwuCharsets:
    """Tests des différents encodages de sortie."""
    
    @pytest.mark.parametrize("charset", ["ASCII", "ANSEL", "ANSI"])
    def test_charset_export(
        self, galichet_base: str, dist_dir: Path, charset: str
    ):
        """Test export avec différents charsets."""
        exit_code = cmd_verify(
            base=galichet_base,
            dist_dir=dist_dir,
            ignore_trailing_space=True,
            charset=charset,
            raw=False,
            surnames=None,
            keys=None,
            asc=None,
            desc=None,
            asc_desc=None,
            parentship=False,
            isolated=False,
            nn=False,
            nnn=False,
            all_files=False,
            nopicture=False,
            picture_path=False,
            source=None,
            censor=None,
            sep=None,
            sep_limit=None,
            sep_only_file=None,
            old_gw=False,
            mem=False,
        )
        assert exit_code == 0, f"Charset {charset} failed"


@pytest.mark.gwu
class TestGwuFiltering:
    """Tests des options de filtrage."""
    
    def test_isolated_persons(self, galichet_base: str, dist_dir: Path):
        """Export incluant les personnes isolées."""
        exit_code = cmd_verify(
            base=galichet_base,
            dist_dir=dist_dir,
            ignore_trailing_space=True,
            charset=None,
            raw=False,
            surnames=None,
            keys=None,
            asc=None,
            desc=None,
            asc_desc=None,
            parentship=False,
            isolated=True,
            nn=False,
            nnn=False,
            all_files=False,
            nopicture=False,
            picture_path=False,
            source=None,
            censor=None,
            sep=None,
            sep_limit=None,
            sep_only_file=None,
            old_gw=False,
            mem=False,
        )
        assert exit_code == 0


@pytest.mark.gwu
class TestGwuNotes:
    """Tests des options liées aux notes."""
    
    def test_no_base_notes(self, galichet_base: str, dist_dir: Path):
        """Export sans notes de base (--nn)."""
        exit_code = cmd_verify(
            base=galichet_base,
            dist_dir=dist_dir,
            ignore_trailing_space=True,
            charset=None,
            raw=False,
            surnames=None,
            keys=None,
            asc=None,
            desc=None,
            asc_desc=None,
            parentship=False,
            isolated=False,
            nn=True,
            nnn=False,
            all_files=False,
            nopicture=False,
            picture_path=False,
            source=None,
            censor=None,
            sep=None,
            sep_limit=None,
            sep_only_file=None,
            old_gw=False,
            mem=False,
        )
        assert exit_code == 0
    
    def test_no_notes_at_all(self, galichet_base: str, dist_dir: Path):
        """Export sans aucune note (--nnn)."""
        exit_code = cmd_verify(
            base=galichet_base,
            dist_dir=dist_dir,
            ignore_trailing_space=True,
            charset=None,
            raw=False,
            surnames=None,
            keys=None,
            asc=None,
            desc=None,
            asc_desc=None,
            parentship=False,
            isolated=False,
            nn=False,
            nnn=True,
            all_files=False,
            nopicture=False,
            picture_path=False,
            source=None,
            censor=None,
            sep=None,
            sep_limit=None,
            sep_only_file=None,
            old_gw=False,
            mem=False,
        )
        assert exit_code == 0
    
    def test_all_notes_files(self, galichet_base: str, dist_dir: Path):
        """Export avec tous les fichiers notes (--all-files)."""
        exit_code = cmd_verify(
            base=galichet_base,
            dist_dir=dist_dir,
            ignore_trailing_space=True,
            charset=None,
            raw=False,
            surnames=None,
            keys=None,
            asc=None,
            desc=None,
            asc_desc=None,
            parentship=False,
            isolated=False,
            nn=False,
            nnn=False,
            all_files=True,
            nopicture=False,
            picture_path=False,
            source=None,
            censor=None,
            sep=None,
            sep_limit=None,
            sep_only_file=None,
            old_gw=False,
            mem=False,
        )
        assert exit_code == 0


@pytest.mark.gwu
class TestGwuPictures:
    """Tests des options liées aux images."""
    
    def test_nopicture(self, galichet_base: str, dist_dir: Path):
        """Export sans extraction d'images."""
        exit_code = cmd_verify(
            base=galichet_base,
            dist_dir=dist_dir,
            ignore_trailing_space=True,
            charset=None,
            raw=False,
            surnames=None,
            keys=None,
            asc=None,
            desc=None,
            asc_desc=None,
            parentship=False,
            isolated=False,
            nn=False,
            nnn=False,
            all_files=False,
            nopicture=True,
            picture_path=False,
            source=None,
            censor=None,
            sep=None,
            sep_limit=None,
            sep_only_file=None,
            old_gw=False,
            mem=False,
        )
        assert exit_code == 0
    
    def test_picture_path(self, galichet_base: str, dist_dir: Path):
        """Export avec chemins d'images."""
        exit_code = cmd_verify(
            base=galichet_base,
            dist_dir=dist_dir,
            ignore_trailing_space=True,
            charset=None,
            raw=False,
            surnames=None,
            keys=None,
            asc=None,
            desc=None,
            asc_desc=None,
            parentship=False,
            isolated=False,
            nn=False,
            nnn=False,
            all_files=False,
            nopicture=False,
            picture_path=True,
            source=None,
            censor=None,
            sep=None,
            sep_limit=None,
            sep_only_file=None,
            old_gw=False,
            mem=False,
        )
        assert exit_code == 0


@pytest.mark.gwu
@pytest.mark.slow
class TestGwuCensorship:
    """Tests de la censure par âge."""
    
    def test_censor_100_years(self, galichet_base: str, dist_dir: Path):
        """Export avec censure à 100 ans."""
        exit_code = cmd_verify(
            base=galichet_base,
            dist_dir=dist_dir,
            ignore_trailing_space=True,
            charset=None,
            raw=False,
            surnames=None,
            keys=None,
            asc=None,
            desc=None,
            asc_desc=None,
            parentship=False,
            isolated=False,
            nn=False,
            nnn=False,
            all_files=False,
            nopicture=False,
            picture_path=False,
            source=None,
            censor=100,
            sep=None,
            sep_limit=None,
            sep_only_file=None,
            old_gw=False,
            mem=False,
        )
        assert exit_code == 0


@pytest.mark.gwu
class TestGwuFormats:
    """Tests des formats de sortie."""
    
    def test_old_gw_format(self, galichet_base: str, dist_dir: Path):
        """Export en format ancien (< 7.00)."""
        exit_code = cmd_verify(
            base=galichet_base,
            dist_dir=dist_dir,
            ignore_trailing_space=True,
            charset=None,
            raw=False,
            surnames=None,
            keys=None,
            asc=None,
            desc=None,
            asc_desc=None,
            parentship=False,
            isolated=False,
            nn=False,
            nnn=False,
            all_files=False,
            nopicture=False,
            picture_path=False,
            source=None,
            censor=None,
            sep=None,
            sep_limit=None,
            sep_only_file=None,
            old_gw=True,
            mem=False,
        )
        assert exit_code == 0
    
    def test_raw_output(self, galichet_base: str, dist_dir: Path):
        """Export brut sans conversion UTF-8."""
        exit_code = cmd_verify(
            base=galichet_base,
            dist_dir=dist_dir,
            ignore_trailing_space=True,
            charset=None,
            raw=True,
            surnames=None,
            keys=None,
            asc=None,
            desc=None,
            asc_desc=None,
            parentship=False,
            isolated=False,
            nn=False,
            nnn=False,
            all_files=False,
            nopicture=False,
            picture_path=False,
            source=None,
            censor=None,
            sep=None,
            sep_limit=None,
            sep_only_file=None,
            old_gw=False,
            mem=False,
        )
        assert exit_code == 0
    
    def test_mem_mode(self, galichet_base: str, dist_dir: Path):
        """Export en mode économie mémoire."""
        exit_code = cmd_verify(
            base=galichet_base,
            dist_dir=dist_dir,
            ignore_trailing_space=True,
            charset=None,
            raw=False,
            surnames=None,
            keys=None,
            asc=None,
            desc=None,
            asc_desc=None,
            parentship=False,
            isolated=False,
            nn=False,
            nnn=False,
            all_files=False,
            nopicture=False,
            picture_path=False,
            source=None,
            censor=None,
            sep=None,
            sep_limit=None,
            sep_only_file=None,
            old_gw=False,
            mem=True,
        )
        assert exit_code == 0


# ============================================================================
# TESTS DE CRÉATION DE GOLDEN (skip par défaut)
# ============================================================================

@pytest.mark.record
@pytest.mark.skip(reason="Use --record flag to create golden masters")
def test_record_default_golden(galichet_base: str, dist_dir: Path):
    """Crée le golden master par défaut."""
    from gwu_golden import cmd_record
    
    cmd_record(
        base=galichet_base,
        dist_dir=dist_dir,
        ignore_trailing_space=True,
        charset=None,
        raw=False,
        surnames=None,
        keys=None,
        asc=None,
        desc=None,
        asc_desc=None,
        parentship=False,
        isolated=False,
        nn=False,
        nnn=False,
        all_files=False,
        nopicture=False,
        picture_path=False,
        source=None,
        censor=None,
        sep=None,
        sep_limit=None,
        sep_only_file=None,
        old_gw=False,
        mem=False,
    )
