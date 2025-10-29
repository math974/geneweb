#!/usr/bin/env python3
"""
Golden Master Testing pour gwd (GeneWeb Web Server)

Ce script permet de tester le serveur web gwd en capturant ses réponses HTTP
et en les comparant à des "golden masters" (réponses de référence).

Usage:
    ./gwd_golden.py record --base galichet [--scenarios basic]
    ./gwd_golden.py verify --base galichet [--scenarios basic]
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
import signal
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import difflib
import urllib.parse
import urllib.request
import socket


def log(msg: str) -> None:
    """Affiche un message de log."""
    print(f"[gwd_golden] {msg}")


def run(cmd: List[str], cwd: Path | None = None) -> None:
    """Exécute une commande et lève une exception en cas d'échec."""
    result = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    if result.returncode != 0:
        raise SystemExit(f"Commande échouée ({result.returncode}): {' '.join(cmd)}")


def find_gwd(dist_dir: Path) -> Path:
    """Localise l'exécutable gwd."""
    gw_dir = dist_dir / "gw"
    gwd = gw_dir / "gwd"
    if gwd.exists():
        return gwd
    
    # Fallback: essayer le binaire installé via OPAM
    gwd_path = shutil.which("geneweb.gwd")
    if gwd_path:
        return Path(gwd_path)
    
    raise SystemExit(
        f"Impossible de localiser gwd. Construisez la distribution (make distrib) "
        f"ou installez via OPAM."
    )


def ensure_dir(p: Path) -> None:
    """Crée un répertoire s'il n'existe pas."""
    p.mkdir(parents=True, exist_ok=True)


def read_text_lines(path: Path, ignore_trailing_space: bool) -> List[str]:
    """Lit les lignes d'un fichier texte."""
    with path.open("r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    if ignore_trailing_space:
        return [ln.rstrip().rstrip("\r") + "\n" for ln in lines]
    return lines


def unified_diff(a_path: Path, b_path: Path, ignore_trailing_space: bool) -> str:
    """Génère un diff unifié entre deux fichiers."""
    a_lines = read_text_lines(a_path, ignore_trailing_space)
    b_lines = read_text_lines(b_path, ignore_trailing_space)
    diff = difflib.unified_diff(
        a_lines,
        b_lines,
        fromfile=str(a_path),
        tofile=str(b_path),
        lineterm="",
        n=3,
    )
    return "\n".join(diff)


def find_free_port() -> int:
    """Trouve un port TCP libre."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


class GwdServer:
    """Gestionnaire du serveur gwd pour les tests."""
    
    def __init__(
        self,
        gwd_path: Path,
        bases_dir: Path,
        hd_dir: Path,
        port: int,
        predictable_mode: bool = False,
    ):
        self.gwd_path = gwd_path
        self.bases_dir = bases_dir
        self.hd_dir = hd_dir
        self.port = port
        self.predictable_mode = predictable_mode
        self.process: Optional[subprocess.Popen] = None
        self.log_file: Optional[Path] = None
    
    def start(self) -> None:
        """Démarre le serveur gwd."""
        log(f"Démarrage de gwd sur le port {self.port}...")
        
        # Fichier de log temporaire
        self.log_file = Path(f"/tmp/gwd_golden_{self.port}.log")
        
        # Construction de la commande
        cmd = [
            str(self.gwd_path),
            "-p", str(self.port),
            "-bd", str(self.bases_dir),
            "-hd", str(self.hd_dir),
            "-log", str(self.log_file),
            "-n_workers", "0",  # Mode synchrone pour les tests
            "-conn_tmout", "3600",
            "-robot_xcl", "10000,1",  # Désactiver protection robot
        ]
        
        if self.predictable_mode:
            cmd.append("-predictable_mode")
        
        log(f"Commande: {' '.join(cmd)}")
        
        # Démarrer le processus
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if os.name != "nt" else None,
        )
        
        # Attendre que le serveur soit prêt
        self._wait_for_ready()
        log("Serveur gwd prêt ✓")
    
    def stop(self) -> None:
        """Arrête le serveur gwd."""
        if self.process:
            log("Arrêt du serveur gwd...")
            try:
                if os.name != "nt":
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                else:
                    self.process.terminate()
                self.process.wait(timeout=10)
            except (subprocess.TimeoutExpired, ProcessLookupError):
                if os.name != "nt":
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                else:
                    self.process.kill()
            finally:
                self.process = None
                log("Serveur gwd arrêté ✓")
        
        # Nettoyer le fichier de log
        if self.log_file and self.log_file.exists():
            self.log_file.unlink()
    
    def _wait_for_ready(self, timeout: int = 30) -> None:
        """Attend que le serveur soit prêt à accepter des connexions."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Tenter une connexion simple
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect(("localhost", self.port))
                    return
            except (socket.error, ConnectionRefusedError):
                time.sleep(0.5)
        
        raise SystemExit(f"Le serveur gwd n'a pas démarré dans les {timeout}s")
    
    def get_url(self, base: str, params: Dict[str, str]) -> str:
        """Construit une URL pour le serveur."""
        query = urllib.parse.urlencode(params) if params else ""
        if query:
            return f"http://localhost:{self.port}/{base}?{query}"
        return f"http://localhost:{self.port}/{base}"
    
    def fetch(self, base: str, params: Dict[str, str]) -> Tuple[str, int]:
        """Récupère une page du serveur.
        
        Returns:
            (content, status_code)
        """
        url = self.get_url(base, params)
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode("utf-8", errors="replace")
                return content, response.status
        except urllib.error.HTTPError as e:
            content = e.read().decode("utf-8", errors="replace")
            return content, e.code
        except Exception as e:
            log(f"ERREUR lors de la récupération de {url}: {e}")
            return f"<!-- ERROR: {e} -->", 500


def normalize_html(content: str) -> str:
    """Normalise le contenu HTML pour éviter les faux positifs.
    
    Retire les éléments variables comme:
    - Timestamps
    - Session IDs
    - Chemins absolus
    - Numéros de version
    """
    # Retirer les commentaires de génération avec timestamps
    content = re.sub(
        r"<!-- generated at .*? -->",
        "<!-- generated at [TIMESTAMP] -->",
        content,
    )
    
    # Retirer les timestamps ISO
    content = re.sub(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        "[TIMESTAMP]",
        content,
    )
    
    # Retirer les dates formatées
    content = re.sub(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
        "[TIMESTAMP]",
        content,
    )
    
    # Normaliser les chemins absolus
    content = re.sub(
        r"/Users/[^/]+/[^\s\"'<>]+",
        "[ABSOLUTE_PATH]",
        content,
    )
    
    # Normaliser les session IDs (si présents)
    content = re.sub(
        r"session=[a-f0-9]{32,}",
        "session=[SESSION_ID]",
        content,
    )
    
    return content


# Définition des scénarios de test
# Basés sur les requêtes de test/run_gw_test.sh

SCENARIO_SETS = {
    "basic": [
        {
            "name": "homepage",
            "params": {},
            "description": "Page d'accueil de la base",
        },
        {
            "name": "person_by_name",
            "params": {"p": "anthoine", "n": "geruzet", "oc": "0"},
            "description": "Personne par nom/prénom",
        },
        {
            "name": "person_not_found",
            "params": {"p": "xxx", "n": "yyy"},
            "description": "Personne inexistante",
        },
        {
            "name": "search",
            "params": {"m": "S", "n": "geruzet", "p": ""},
            "description": "Recherche par nom",
        },
        {
            "name": "statistics",
            "params": {"m": "STAT"},
            "description": "Page de statistiques",
        },
        {
            "name": "surnames_alpha",
            "params": {"m": "N", "tri": "A"},
            "description": "Liste des noms alphabétique",
        },
        {
            "name": "surnames_freq",
            "params": {"m": "N", "tri": "F"},
            "description": "Liste des noms par fréquence",
        },
        {
            "name": "firstnames_alpha",
            "params": {"m": "P", "tri": "A"},
            "description": "Liste des prénoms alphabétique",
        },
    ],
    "trees": [
        {
            "name": "ancestors_tree",
            "params": {"m": "A", "i": "26"},
            "description": "Arbre des ancêtres",
        },
        {
            "name": "ancestors_table",
            "params": {"m": "A", "i": "26", "t": "T", "v": "5"},
            "description": "Tableau des ancêtres",
        },
        {
            "name": "ancestors_vertical",
            "params": {"m": "A", "i": "26", "t": "A", "v": "5"},
            "description": "Ancêtres vertical",
        },
        {
            "name": "ancestors_compact",
            "params": {"m": "A", "i": "26", "t": "C", "v": "5"},
            "description": "Ancêtres compact",
        },
        {
            "name": "descendants",
            "params": {"m": "D", "i": "26"},
            "description": "Arbre des descendants",
        },
        {
            "name": "descendants_vertical",
            "params": {"m": "D", "i": "26", "t": "V", "v": "3"},
            "description": "Descendants vertical",
        },
    ],
    "person": [
        {
            "name": "person_details",
            "params": {"i": "26"},
            "description": "Fiche détaillée d'une personne",
        },
        {
            "name": "person_relations",
            "params": {"m": "R", "i": "26"},
            "description": "Relations d'une personne",
        },
        {
            "name": "person_chronology",
            "params": {"m": "C", "i": "26", "v": "3"},
            "description": "Chronologie d'une personne",
        },
        {
            "name": "person_family",
            "params": {"m": "F", "i": "26"},
            "description": "Famille d'une personne",
        },
    ],
    "lists": [
        {
            "name": "list_recent_births",
            "params": {"m": "LB", "k": "30"},
            "description": "Liste des naissances récentes",
        },
        {
            "name": "list_recent_deaths",
            "params": {"m": "LD", "k": "30"},
            "description": "Liste des décès récents",
        },
        {
            "name": "list_recent_marriages",
            "params": {"m": "LM", "k": "30"},
            "description": "Liste des mariages récents",
        },
        {
            "name": "list_oldest",
            "params": {"m": "OA", "k": "30"},
            "description": "Liste des plus âgés",
        },
    ],
    "admin": [
        {
            "name": "welcome",
            "params": {"m": "CONN_WIZ"},
            "description": "Page d'accueil wizard",
        },
        {
            "name": "add_individual",
            "params": {"m": "ADD_IND"},
            "description": "Formulaire ajout individu",
        },
        {
            "name": "add_family",
            "params": {"m": "ADD_FAM"},
            "description": "Formulaire ajout famille",
        },
    ],
}


def get_all_scenarios() -> List[Dict[str, Any]]:
    """Retourne tous les scénarios de test."""
    all_scenarios = []
    for scenarios in SCENARIO_SETS.values():
        all_scenarios.extend(scenarios)
    return all_scenarios


def get_scenarios(scenario_sets: Optional[List[str]]) -> List[Dict[str, Any]]:
    """Retourne les scénarios correspondant aux sets demandés."""
    if not scenario_sets:
        return get_all_scenarios()
    
    scenarios = []
    for set_name in scenario_sets:
        if set_name == "all":
            return get_all_scenarios()
        if set_name in SCENARIO_SETS:
            scenarios.extend(SCENARIO_SETS[set_name])
        else:
            log(f"ATTENTION: Set de scénarios inconnu: {set_name}")
    
    return scenarios


def sanitize_filename(name: str) -> str:
    """Nettoie un nom pour en faire un nom de fichier valide."""
    # Remplacer les caractères non alphanumériques
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    # Limiter la longueur
    if len(name) > 100:
        name = name[:100]
    return name


def cmd_record(
    base: str,
    dist_dir: Path,
    ignore_trailing_space: bool,
    scenario_sets: Optional[List[str]],
) -> None:
    """Mode RECORD: Capture les réponses de gwd et les sauvegarde comme golden masters."""
    log(f"=== MODE RECORD pour la base '{base}' ===")
    
    # Localiser gwd
    gwd = find_gwd(dist_dir)
    log(f"Utilisation de gwd: {gwd}")
    
    # Répertoires
    bases_dir = dist_dir / "bases"
    hd_dir = dist_dir / "gw"
    golden_dir = Path("test") / "golden" / "gwd" / base
    ensure_dir(golden_dir)
    
    # Vérifier que la base existe
    base_path = bases_dir / f"{base}.gwb"
    if not base_path.exists():
        raise SystemExit(
            f"La base {base_path} n'existe pas. "
            f"Créez-la d'abord avec gwc ou utilisez une base existante."
        )
    
    # Trouver un port libre
    port = find_free_port()
    
    # Démarrer le serveur
    server = GwdServer(gwd, bases_dir, hd_dir, port, predictable_mode=True)
    try:
        server.start()
        
        # Récupérer les scénarios à tester
        scenarios = get_scenarios(scenario_sets)
        log(f"Enregistrement de {len(scenarios)} scénarios...")
        
        # Exécuter chaque scénario
        for i, scenario in enumerate(scenarios, 1):
            name = scenario["name"]
            params = scenario["params"]
            description = scenario.get("description", "")
            
            log(f"[{i}/{len(scenarios)}] {name}: {description}")
            
            # Récupérer la réponse
            content, status = server.fetch(base, params)
            
            # Normaliser le contenu
            content = normalize_html(content)
            
            # Sauvegarder
            filename = sanitize_filename(name) + ".html"
            output_path = golden_dir / filename
            with output_path.open("w", encoding="utf-8") as f:
                f.write(content)
            
            log(f"  → Sauvegardé dans {output_path} (status={status})")
        
        log(f"✓ Golden masters enregistrés dans {golden_dir}")
        
    finally:
        server.stop()


def cmd_verify(
    base: str,
    dist_dir: Path,
    ignore_trailing_space: bool,
    scenario_sets: Optional[List[str]],
) -> int:
    """Mode VERIFY: Compare les réponses actuelles avec les golden masters."""
    log(f"=== MODE VERIFY pour la base '{base}' ===")
    
    # Localiser gwd
    gwd = find_gwd(dist_dir)
    log(f"Utilisation de gwd: {gwd}")
    
    # Répertoires
    bases_dir = dist_dir / "bases"
    hd_dir = dist_dir / "gw"
    golden_dir = Path("test") / "golden" / "gwd" / base
    
    if not golden_dir.exists():
        raise SystemExit(
            f"Aucun golden master trouvé dans {golden_dir}. "
            f"Exécutez d'abord 'record' pour créer les golden masters."
        )
    
    # Vérifier que la base existe
    base_path = bases_dir / f"{base}.gwb"
    if not base_path.exists():
        raise SystemExit(f"La base {base_path} n'existe pas.")
    
    # Répertoire temporaire pour les réponses courantes
    current_dir = Path("/tmp") / f"gwd_golden_verify_{base}"
    if current_dir.exists():
        shutil.rmtree(current_dir)
    ensure_dir(current_dir)
    
    # Trouver un port libre
    port = find_free_port()
    
    # Démarrer le serveur
    server = GwdServer(gwd, bases_dir, hd_dir, port, predictable_mode=True)
    exit_code = 0
    
    try:
        server.start()
        
        # Récupérer les scénarios à tester
        scenarios = get_scenarios(scenario_sets)
        log(f"Vérification de {len(scenarios)} scénarios...")
        
        # Exécuter chaque scénario
        for i, scenario in enumerate(scenarios, 1):
            name = scenario["name"]
            params = scenario["params"]
            description = scenario.get("description", "")
            
            log(f"[{i}/{len(scenarios)}] {name}: {description}")
            
            # Récupérer la réponse actuelle
            content, status = server.fetch(base, params)
            content = normalize_html(content)
            
            # Sauvegarder dans le répertoire temporaire
            filename = sanitize_filename(name) + ".html"
            current_path = current_dir / filename
            with current_path.open("w", encoding="utf-8") as f:
                f.write(content)
            
            # Comparer avec le golden master
            golden_path = golden_dir / filename
            if not golden_path.exists():
                log(f"  ⚠️  Golden master manquant: {golden_path}")
                exit_code = 1
                continue
            
            # Générer le diff
            diff = unified_diff(golden_path, current_path, ignore_trailing_space)
            
            if diff:
                log(f"  ❌ DIFFÉRENCE détectée!")
                print("\n" + "="*80)
                print(f"DIFF pour {name}:")
                print("="*80)
                print(diff)
                print("="*80 + "\n")
                exit_code = 1
            else:
                log(f"  ✓ OK (conforme au golden)")
        
        if exit_code == 0:
            log("✓ Tous les scénarios sont conformes aux golden masters!")
        else:
            log("❌ Des différences ont été détectées.")
        
    finally:
        server.stop()
    
    return exit_code


def main(argv: List[str]) -> int:
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Golden master testing pour gwd (GeneWeb Web Server)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Enregistrer les golden masters pour la base galichet (scénarios de base)
  ./gwd_golden.py record --base galichet --scenarios basic
  
  # Enregistrer tous les scénarios
  ./gwd_golden.py record --base galichet --scenarios all
  
  # Vérifier la conformité
  ./gwd_golden.py verify --base galichet --scenarios basic
  
  # Scénarios disponibles: basic, trees, person, lists, admin, all
        """,
    )
    
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    
    # Arguments communs
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--base",
        required=True,
        help="Nom de la base de données (sans extension .gwb)",
    )
    common.add_argument(
        "--dist",
        default="./distribution",
        help="Répertoire distribution (défaut: ./distribution)",
    )
    common.add_argument(
        "--no-ignore-trailing-space",
        action="store_true",
        help="Ne pas ignorer les espaces de fin de ligne dans les diffs",
    )
    common.add_argument(
        "--scenarios",
        nargs="+",
        choices=["basic", "trees", "person", "lists", "admin", "all"],
        default=["basic"],
        help="Sets de scénarios à tester (défaut: basic)",
    )
    
    # Commande record
    subparsers.add_parser(
        "record",
        parents=[common],
        help="Enregistrer les golden masters",
    )
    
    # Commande verify
    subparsers.add_parser(
        "verify",
        parents=[common],
        help="Vérifier contre les golden masters",
    )
    
    args = parser.parse_args(argv)
    
    dist_dir = Path(args.dist)
    ignore_trailing_space = not args.no_ignore_trailing_space
    
    if args.cmd == "record":
        cmd_record(args.base, dist_dir, ignore_trailing_space, args.scenarios)
        return 0
    elif args.cmd == "verify":
        return cmd_verify(args.base, dist_dir, ignore_trailing_space, args.scenarios)
    
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

