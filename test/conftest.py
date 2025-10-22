#!/usr/bin/env python3
"""
Fixtures partagées pour les tests pytest de GeneWeb.

Ce fichier contient les fixtures communes utilisées par:
- test_gwu_golden.py (tests gwu)
- test_gwd_golden.py (tests gwd - à venir)
"""

import pytest
import shutil
from pathlib import Path
from typing import Tuple


@pytest.fixture(scope="session")
def dist_dir() -> Path:
    """
    Chemin vers le répertoire de distribution.
    
    Returns:
        Path vers ./distribution
    """
    return Path("./distribution")


@pytest.fixture(scope="session")
def gwu_bins(dist_dir: Path) -> Tuple[Path, Path]:
    """
    Localise les binaires gwu et gwc.
    
    Args:
        dist_dir: Répertoire de distribution
        
    Returns:
        Tuple (gwu_path, gwc_path)
        
    Raises:
        SystemExit: Si les binaires ne sont pas trouvés
    """
    gw_dir = dist_dir / "gw"
    gwu = gw_dir / "gwu"
    gwc = gw_dir / "gwc"
    
    if gwu.exists() and gwc.exists():
        return gwu, gwc
    
    # Fallback: binaires OPAM
    gwu_path = shutil.which("geneweb.gwu")
    gwc_path = shutil.which("geneweb.gwc")
    
    if gwu_path and gwc_path:
        return Path(gwu_path), Path(gwc_path)
    
    pytest.fail(
        "Impossible de localiser gwu/gwc. "
        "Construisez la distribution (make distrib) ou installez via OPAM."
    )


@pytest.fixture(scope="session")
def bases_dir(dist_dir: Path) -> Path:
    """
    Répertoire contenant les bases de données GeneWeb.
    
    Args:
        dist_dir: Répertoire de distribution
        
    Returns:
        Path vers distribution/bases
    """
    bases = dist_dir / "bases"
    bases.mkdir(parents=True, exist_ok=True)
    return bases


@pytest.fixture(scope="function")
def galichet_base(gwu_bins: Tuple[Path, Path], bases_dir: Path) -> str:
    """
    Prépare la base de données galichet pour les tests.
    
    Cette fixture reconstruit la base .gwb depuis le fichier .gw
    à chaque test pour assurer un état propre.
    
    Args:
        gwu_bins: Tuple (gwu, gwc)
        bases_dir: Répertoire des bases
        
    Returns:
        Nom de la base: "galichet"
    """
    from gwu_golden import build_gwb_if_needed
    
    gwu, gwc = gwu_bins
    base_name = "galichet"
    source_gw = Path("test") / f"{base_name}.gw"
    
    if not source_gw.exists():
        pytest.skip(f"Fichier source {source_gw} non trouvé")
    
    # Construire la base .gwb
    build_gwb_if_needed(gwc, bases_dir, base_name, source_gw)
    
    return base_name


@pytest.fixture(scope="function")
def ares_base(gwu_bins: Tuple[Path, Path], bases_dir: Path) -> str:
    """
    Prépare la base de données ares pour les tests.
    
    Args:
        gwu_bins: Tuple (gwu, gwc)
        bases_dir: Répertoire des bases
        
    Returns:
        Nom de la base: "ares"
    """
    from gwu_golden import build_gwb_if_needed
    
    gwu, gwc = gwu_bins
    base_name = "ares"
    
    # Chercher le fichier source dans test/ ou distribution/bases/
    source_gw = Path("test") / f"{base_name}.gw"
    if not source_gw.exists():
        # Essayer dans bases/
        source_gw = bases_dir / f"{base_name}.gw"
        if not source_gw.exists():
            pytest.skip(f"Fichier source {base_name}.gw non trouvé")
    
    # Construire la base .gwb
    build_gwb_if_needed(gwc, bases_dir, base_name, source_gw)
    
    return base_name


@pytest.fixture(scope="session")
def golden_dir() -> Path:
    """
    Répertoire contenant les fichiers golden de référence.
    
    Returns:
        Path vers test/golden
    """
    return Path("test") / "golden"


def pytest_configure(config):
    """Configuration personnalisée de pytest."""
    # Ajouter des marqueurs personnalisés si nécessaire
    config.addinivalue_line(
        "markers", "record: marque les tests qui créent des golden masters"
    )
