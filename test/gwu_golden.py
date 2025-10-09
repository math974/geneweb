#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import difflib


def run(cmd: List[str], cwd: Path | None = None) -> None:
    result = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    if result.returncode != 0:
        raise SystemExit(f"Commande échouée ({result.returncode}): {' '.join(cmd)}")


def find_bins(dist_dir: Path) -> Tuple[Path, Path]:
    gw_dir = dist_dir / "gw"
    gwu = gw_dir / "gwu"
    gwc = gw_dir / "gwc"
    if gwu.exists() and gwc.exists():
        return gwu, gwc
    # Fallback: essayer les binaires installés dans le switch OPAM
    # geneweb.gwu / geneweb.gwc
    gwu_path = shutil.which("geneweb.gwu")
    gwc_path = shutil.which("geneweb.gwc")
    if gwu_path and gwc_path:
        return Path(gwu_path), Path(gwc_path)
    raise SystemExit("Impossible de localiser gwu/gwc. Construisez la distribution (make distrib) ou installez via OPAM.")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def read_text_lines(path: Path, ignore_trailing_space: bool) -> List[str]:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    if ignore_trailing_space:
        return [ln.rstrip().rstrip("\r") + "\n" for ln in lines]
    return lines


def unified_diff(a_path: Path, b_path: Path, ignore_trailing_space: bool) -> str:
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


def build_gwb_if_needed(gwc: Path, bases_dir: Path, base: str, source_gw: Path | None) -> None:
    gw_path = bases_dir / f"{base}.gw"
    if source_gw and source_gw.exists() and not gw_path.exists():
        ensure_dir(bases_dir)
        shutil.copy2(source_gw, gw_path)
    # Construire la base .gwb si on a un .gw
    if gw_path.exists():
        log_path = bases_dir / f"{base}.log"
        cmd = [
            str(gwc),
            "-v",
            "-f",
            "-cg",
            "-bd",
            str(bases_dir),
            "-o",
            base,
            str(gw_path),
        ]
        with log_path.open("w", encoding="utf-8") as logf:
            proc = subprocess.run(cmd, stdout=logf, stderr=subprocess.STDOUT)
            if proc.returncode != 0:
                raise SystemExit(f"Échec gwc, voir {log_path}")


def run_gwu(
    gwu: Path,
    bases_dir: Path,
    base: str,
    out_file: Path,
    out_dir: Path | None,
    extra_args: Optional[List[str]] = None,
) -> Tuple[Path, Path | None, Path]:
    stderr_path = bases_dir / f"{base}.gwu.stderr"
    cmd = [str(gwu), str(bases_dir / base), "-v", "-o", str(out_file)]
    if out_dir is not None:
        # Nettoyage du répertoire de sortie
        if out_dir.exists():
            shutil.rmtree(out_dir)
        ensure_dir(out_dir)
        cmd += ["-odir", str(out_dir)]
    if extra_args:
        cmd += extra_args
    # Afficher la commande exacte pour traçabilité
    print("RUN:", " ".join(cmd))
    with stderr_path.open("w", encoding="utf-8") as errf:
        proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=errf)
    if proc.returncode != 0:
        raise SystemExit(f"Échec gwu, voir {stderr_path}")
    return out_file, out_dir, stderr_path


def build_scenario_suffix(
    charset: Optional[str],
    raw: bool,
    surnames: Optional[List[str]],
    keys: Optional[List[str]],
    asc: Optional[int],
    desc: Optional[int],
    asc_desc: Optional[int],
    parentship: bool,
    isolated: bool,
    nn: bool,
    nnn: bool,
    all_files: bool,
    nopicture: bool,
    picture_path: bool,
    source: Optional[str],
    censor: Optional[int],
    sep: Optional[List[str]],
    sep_limit: Optional[int],
    sep_only_file: Optional[str],
    old_gw: bool,
    mem: bool,
) -> str:
    parts: List[str] = []
    if charset:
        parts.append(f"charset-{charset}")
    if raw:
        parts.append("raw")
    if surnames:
        parts.append(f"s-{'-'.join(s.replace(' ', '_') for s in surnames)}")
    if keys:
        parts.append(f"key-{len(keys)}")
    if asc is not None:
        parts.append(f"a{asc}")
    if desc is not None:
        parts.append(f"d{desc}")
    if asc_desc is not None:
        parts.append(f"ad{asc_desc}")
    if parentship:
        parts.append("parentship")
    if isolated:
        parts.append("isolated")
    if nn:
        parts.append("nn")
    if nnn:
        parts.append("nnn")
    if all_files:
        parts.append("all_files")
    if nopicture:
        parts.append("nopicture")
    if picture_path:
        parts.append("picture_path")
    if source:
        parts.append(f"source-{source.replace(' ', '_')}")
    if censor is not None:
        parts.append(f"c{censor}")
    if sep:
        parts.append(f"sep-{len(sep)}")
    if sep_limit is not None:
        parts.append(f"seplimit{sep_limit}")
    if sep_only_file:
        parts.append(f"sepfile")
    if old_gw:
        parts.append("old_gw")
    if mem:
        parts.append("mem")
    return ("." + ".".join(parts)) if parts else ""


def gwu_extra_args(
    charset: Optional[str],
    raw: bool,
    surnames: Optional[List[str]],
    keys: Optional[List[str]],
    asc: Optional[int],
    desc: Optional[int],
    asc_desc: Optional[int],
    parentship: bool,
    isolated: bool,
    nn: bool,
    nnn: bool,
    all_files: bool,
    nopicture: bool,
    picture_path: bool,
    source: Optional[str],
    censor: Optional[int],
    sep: Optional[List[str]],
    sep_limit: Optional[int],
    sep_only_file: Optional[str],
    old_gw: bool,
    mem: bool,
) -> List[str]:
    args: List[str] = []
    if charset:
        args += ["-charset", charset]
    if raw:
        args += ["-raw"]
    if surnames:
        for s in surnames:
            args += ["-s", s]
    if keys:
        for k in keys:
            args += ["-key", k]
    if asc is not None:
        args += ["-a", str(asc)]
    if desc is not None:
        args += ["-d", str(desc)]
    if asc_desc is not None:
        args += ["-ad", str(asc_desc)]
    if parentship:
        args += ["-parentship"]
    if isolated:
        args += ["-isolated"]
    if nn:
        args += ["-nn"]
    if nnn:
        args += ["-nnn"]
    if all_files:
        args += ["-all_files"]
    if nopicture:
        args += ["-nopicture"]
    if picture_path:
        args += ["-picture-path"]
    if source:
        args += ["-source", source]
    if censor is not None:
        args += ["-c", str(censor)]
    if sep:
        for s in sep:
            args += ["-sep", s]
    if sep_limit is not None:
        args += ["-sep_limit", str(sep_limit)]
    if sep_only_file:
        args += ["-sep_only_file", sep_only_file]
    if old_gw:
        args += ["-old_gw"]
    if mem:
        args += ["-mem"]
    return args


def cmd_record(
    base: str,
    dist_dir: Path,
    ignore_trailing_space: bool,
    charset: Optional[str],
    raw: bool,
    surnames: Optional[List[str]],
    keys: Optional[List[str]],
    asc: Optional[int],
    desc: Optional[int],
    asc_desc: Optional[int],
    parentship: bool,
    isolated: bool,
    nn: bool,
    nnn: bool,
    all_files: bool,
    nopicture: bool,
    picture_path: bool,
    source: Optional[str],
    censor: Optional[int],
    sep: Optional[List[str]],
    sep_limit: Optional[int],
    sep_only_file: Optional[str],
    old_gw: bool,
    mem: bool,
) -> None:
    gwu, gwc = find_bins(dist_dir)
    bases_dir = dist_dir / "bases"
    golden_dir = Path("test") / "golden" / base
    ensure_dir(golden_dir)

    # Tenter de récupérer une source .gw dans test/BASE.gw
    source_gw = Path("test") / f"{base}.gw"
    build_gwb_if_needed(gwc, bases_dir, base, source_gw if source_gw.exists() else None)

    # Lancer deux exports: standard et avec -odir
    suffix = build_scenario_suffix(charset, raw, surnames, keys, asc, desc, asc_desc, parentship, isolated, nn, nnn, all_files, nopicture, picture_path, source, censor, sep, sep_limit, sep_only_file, old_gw, mem)
    std_out = bases_dir / f"{base}{suffix}.golden.gw"
    dir_out = bases_dir / f"{base}{suffix}.dir.golden.gw"
    outdir = bases_dir / f"outdir.{base}{suffix}.golden"

    extra = gwu_extra_args(charset, raw, surnames, keys, asc, desc, asc_desc, parentship, isolated, nn, nnn, all_files, nopicture, picture_path, source, censor, sep, sep_limit, sep_only_file, old_gw, mem)

    # Contexte scénario
    print(f"Scenario: base={base} source={source} c={censor} sep={sep} sep_limit={sep_limit} sep_only_file={sep_only_file} old_gw={old_gw} mem={mem}")

    # Export standard (+ capture logs)
    _, _, std_stderr = run_gwu(gwu, bases_dir, base, std_out, None, extra)
    # Sauvegarder les logs en golden
    std_log_golden = golden_dir / f"{base}{suffix}.golden.stderr"
    if std_stderr.exists():
        shutil.copy2(std_stderr, std_log_golden)

    # Export avec -odir (+ capture logs)
    _, outdir_path, dir_stderr = run_gwu(gwu, bases_dir, base, dir_out, outdir, extra)

    # Copier vers test/golden/BASE
    shutil.copy2(std_out, golden_dir / f"{base}{suffix}.golden.gw")
    if outdir_path and (outdir_path / f"{base}.gw").exists():
        shutil.copy2(outdir_path / f"{base}.gw", golden_dir / f"{base}{suffix}.dir.golden.gw")
    # Logs -odir
    dir_log_golden = golden_dir / f"{base}{suffix}.dir.golden.stderr"
    if dir_stderr.exists():
        shutil.copy2(dir_stderr, dir_log_golden)

    print(f"Golden enregistré dans {golden_dir}")


def cmd_verify(
    base: str,
    dist_dir: Path,
    ignore_trailing_space: bool,
    charset: Optional[str],
    raw: bool,
    surnames: Optional[List[str]],
    keys: Optional[List[str]],
    asc: Optional[int],
    desc: Optional[int],
    asc_desc: Optional[int],
    parentship: bool,
    isolated: bool,
    nn: bool,
    nnn: bool,
    all_files: bool,
    nopicture: bool,
    picture_path: bool,
    source: Optional[str],
    censor: Optional[int],
    sep: Optional[List[str]],
    sep_limit: Optional[int],
    sep_only_file: Optional[str],
    old_gw: bool,
    mem: bool,
) -> int:
    gwu, gwc = find_bins(dist_dir)
    bases_dir = dist_dir / "bases"
    golden_dir = Path("test") / "golden" / base
    suffix = build_scenario_suffix(charset, raw, surnames, keys, asc, desc, asc_desc, parentship, isolated, nn, nnn, all_files, nopicture, picture_path, source, censor, sep, sep_limit, sep_only_file, old_gw, mem)
    golden_std = golden_dir / f"{base}{suffix}.golden.gw"
    golden_dirfile = golden_dir / f"{base}{suffix}.dir.golden.gw"
    golden_std_log = golden_dir / f"{base}{suffix}.golden.stderr"
    golden_dir_log = golden_dir / f"{base}{suffix}.dir.golden.stderr"
    if not golden_std.exists():
        raise SystemExit(f"Golden manquant: {golden_std}")

    # Reconstruire si possible
    source_gw = Path("test") / f"{base}.gw"
    build_gwb_if_needed(gwc, bases_dir, base, source_gw if source_gw.exists() else None)

    # Générer des sorties courantes
    cur_std = bases_dir / f"{base}{suffix}.current.gw"
    cur_dir_marker = bases_dir / f"{base}{suffix}.dir.current.gw"
    cur_outdir = bases_dir / f"outdir.{base}{suffix}.current"
    extra = gwu_extra_args(charset, raw, surnames, keys, asc, desc, asc_desc, parentship, isolated, nn, nnn, all_files, nopicture, picture_path, source, censor, sep, sep_limit, sep_only_file, old_gw, mem)
    print(f"Scenario: base={base} source={source} c={censor} sep={sep} sep_limit={sep_limit} sep_only_file={sep_only_file} old_gw={old_gw} mem={mem}")
    _, _, cur_std_stderr = run_gwu(gwu, bases_dir, base, cur_std, None, extra)
    # Sauvegarder une copie distincte des logs courants (standard)
    cur_std_log = bases_dir / f"{base}{suffix}.golden_verify.stderr"
    if cur_std_stderr.exists():
        shutil.copy2(cur_std_stderr, cur_std_log)

    _, cur_outdir, cur_dir_stderr = run_gwu(gwu, bases_dir, base, cur_dir_marker, cur_outdir, extra)
    # Sauvegarder logs -odir
    cur_dir_log = bases_dir / f"{base}{suffix}.dir.golden_verify.stderr"
    if cur_dir_stderr.exists():
        shutil.copy2(cur_dir_stderr, cur_dir_log)

    # Comparer
    exit_code = 0
    std_diff = unified_diff(golden_std, cur_std, ignore_trailing_space)
    if std_diff:
        print("Diff sur export standard:")
        print(std_diff)
        exit_code = 1
    else:
        print("OK: export standard conforme au golden.")

    if golden_dirfile.exists():
        cur_dirfile = (cur_outdir or Path(".")) / f"{base}.gw"
        if not cur_dirfile.exists():
            print(f"ATTENTION: fichier attendu absent: {cur_dirfile}")
            exit_code = 1
        else:
            dir_diff = unified_diff(golden_dirfile, cur_dirfile, ignore_trailing_space)
            if dir_diff:
                print("Diff sur export -odir:")
                print(dir_diff)
                exit_code = 1
            else:
                print("OK: export -odir conforme au golden.")
    else:
        print(f"Golden -odir absent ({golden_dirfile}), vérification sautée.")

    # Comparaison des logs si présents
    if golden_std_log.exists() and cur_std_log.exists():
        log_diff = unified_diff(golden_std_log, cur_std_log, ignore_trailing_space)
        if log_diff:
            print("Diff sur logs standard (-v):")
            print(log_diff)
            exit_code = 1
        else:
            print("OK: logs standard (-v) conformes au golden.")
    else:
        print("Logs standard non comparés (golden ou courant manquant).")

    if golden_dir_log.exists() and cur_dir_log.exists():
        dlog_diff = unified_diff(golden_dir_log, cur_dir_log, ignore_trailing_space)
        if dlog_diff:
            print("Diff sur logs -odir (-v):")
            print(dlog_diff)
            exit_code = 1
        else:
            print("OK: logs -odir (-v) conformes au golden.")
    else:
        print("Logs -odir non comparés (golden ou courant manquant).")

    return exit_code


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Golden master pour gwu (record/verify)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--base", required=True, help="Nom de la base (sans extension)")
    common.add_argument("--dist", default="./distribution", help="Répertoire distribution (par défaut ./distribution)")
    common.add_argument(
        "--no-ignore-trailing-space",
        action="store_true",
        help="Ne pas ignorer les espaces de fin de ligne dans les diff",
    )
    common.add_argument("--charset", choices=["ASCII", "ANSEL", "ANSI", "UTF-8"], help="Forcer l'encodage de sortie")
    common.add_argument("--raw", action="store_true", help="Sortie brute (sans conversion UTF-8)")
    common.add_argument("-s", "--surname", action="append", dest="surnames", help="Sélectionner un patronyme (répétable)")
    common.add_argument("-k", "--key", action="append", dest="keys", help="Clé de personne (répétable)")
    common.add_argument("-a", "--asc", type=int, help="Profondeur ascendance")
    common.add_argument("-d", "--desc", type=int, help="Profondeur descendance")
    common.add_argument("-ad", type=int, dest="ad", help="Profondeur ascendance+descendance")
    common.add_argument("--parentship", action="store_true", help="Sélection par liens de parenté (avec paires de -k)")
    common.add_argument("--isolated", action="store_true", help="Inclure personnes isolées")
    common.add_argument("--nn", action="store_true", help="Pas de notes de base")
    common.add_argument("--nnn", action="store_true", help="Aucune note")
    common.add_argument("--all-files", action="store_true", dest="all_files", help="Tout le contenu notes_d")
    common.add_argument("--nopicture", action="store_true", help="Ne pas extraire les images")
    common.add_argument("--picture-path", action="store_true", dest="picture_path", help="Extraire chemins d'images")
    common.add_argument("--source", help="Remplacer sources individus/familles")
    common.add_argument("-c", "--censor", type=int, help="Censure par âge (années)")
    common.add_argument("--sep", action="append", help="Séparer une personne (avec -odir, répétable)")
    common.add_argument("--sep-limit", type=int, dest="sep_limit", help="Seuil de regroupement pour -sep")
    common.add_argument("--sep-only-file", dest="sep_only_file", help="Fichier cible pour -sep")
    common.add_argument("--old-gw", action="store_true", dest="old_gw", help="Format ancien (< 7.00)")
    common.add_argument("--mem", action="store_true", help="Mode économie mémoire")

    rec = sub.add_parser("record", parents=[common], help="Enregistrer un golden pour la base")
    ver = sub.add_parser("verify", parents=[common], help="Vérifier la base contre le golden")

    args = parser.parse_args(argv)
    dist_dir = Path(args.dist)
    ignore_trailing_space = not args.no_ignore_trailing_space

    if args.cmd == "record":
        cmd_record(
            args.base,
            dist_dir,
            ignore_trailing_space,
            args.charset,
            args.raw,
            args.surnames,
            args.keys,
            args.asc,
            args.desc,
            args.ad,
            args.parentship,
            args.isolated,
            args.nn,
            args.nnn,
            args.all_files,
            args.nopicture,
            args.picture_path,
            args.source,
            args.censor,
            args.sep,
            args.sep_limit,
            args.sep_only_file,
            args.old_gw,
            args.mem,
        )
        return 0
    if args.cmd == "verify":
        return cmd_verify(
            args.base,
            dist_dir,
            ignore_trailing_space,
            args.charset,
            args.raw,
            args.surnames,
            args.keys,
            args.asc,
            args.desc,
            args.ad,
            args.parentship,
            args.isolated,
            args.nn,
            args.nnn,
            args.all_files,
            args.nopicture,
            args.picture_path,
            args.source,
            args.censor,
            args.sep,
            args.sep_limit,
            args.sep_only_file,
            args.old_gw,
            args.mem,
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


