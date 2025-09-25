#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple
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


def run_gwu(gwu: Path, bases_dir: Path, base: str, out_file: Path, out_dir: Path | None) -> Tuple[Path, Path | None, Path]:
    stderr_path = bases_dir / f"{base}.gwu.stderr"
    cmd = [str(gwu), str(bases_dir / base), "-v", "-o", str(out_file)]
    if out_dir is not None:
        # Nettoyage du répertoire de sortie
        if out_dir.exists():
            shutil.rmtree(out_dir)
        ensure_dir(out_dir)
        cmd += ["-odir", str(out_dir)]
    with stderr_path.open("w", encoding="utf-8") as errf:
        proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=errf)
    if proc.returncode != 0:
        raise SystemExit(f"Échec gwu, voir {stderr_path}")
    return out_file, out_dir, stderr_path


def cmd_record(base: str, dist_dir: Path, ignore_trailing_space: bool) -> None:
    gwu, gwc = find_bins(dist_dir)
    bases_dir = dist_dir / "bases"
    golden_dir = Path("test") / "golden" / base
    ensure_dir(golden_dir)

    # Tenter de récupérer une source .gw dans test/BASE.gw
    source_gw = Path("test") / f"{base}.gw"
    build_gwb_if_needed(gwc, bases_dir, base, source_gw if source_gw.exists() else None)

    # Lancer deux exports: standard et avec -odir
    std_out = bases_dir / f"{base}.golden.gw"
    dir_out = bases_dir / f"{base}.dir.golden.gw"
    outdir = bases_dir / f"outdir.{base}.golden"

    # Export standard (+ capture logs)
    _, _, std_stderr = run_gwu(gwu, bases_dir, base, std_out, None)
    # Sauvegarder les logs en golden
    std_log_golden = golden_dir / f"{base}.golden.stderr"
    if std_stderr.exists():
        shutil.copy2(std_stderr, std_log_golden)

    # Export avec -odir (+ capture logs)
    _, outdir_path, dir_stderr = run_gwu(gwu, bases_dir, base, dir_out, outdir)

    # Copier vers test/golden/BASE
    shutil.copy2(std_out, golden_dir / f"{base}.golden.gw")
    if outdir_path and (outdir_path / f"{base}.gw").exists():
        shutil.copy2(outdir_path / f"{base}.gw", golden_dir / f"{base}.dir.golden.gw")
    # Logs -odir
    dir_log_golden = golden_dir / f"{base}.dir.golden.stderr"
    if dir_stderr.exists():
        shutil.copy2(dir_stderr, dir_log_golden)

    print(f"Golden enregistré dans {golden_dir}")


def cmd_verify(base: str, dist_dir: Path, ignore_trailing_space: bool) -> int:
    gwu, gwc = find_bins(dist_dir)
    bases_dir = dist_dir / "bases"
    golden_dir = Path("test") / "golden" / base
    golden_std = golden_dir / f"{base}.golden.gw"
    golden_dirfile = golden_dir / f"{base}.dir.golden.gw"
    golden_std_log = golden_dir / f"{base}.golden.stderr"
    golden_dir_log = golden_dir / f"{base}.dir.golden.stderr"
    if not golden_std.exists():
        raise SystemExit(f"Golden manquant: {golden_std}")

    # Reconstruire si possible
    source_gw = Path("test") / f"{base}.gw"
    build_gwb_if_needed(gwc, bases_dir, base, source_gw if source_gw.exists() else None)

    # Générer des sorties courantes
    cur_std = bases_dir / f"{base}.current.gw"
    cur_dir_marker = bases_dir / f"{base}.dir.current.gw"
    cur_outdir = bases_dir / f"outdir.{base}.current"
    _, _, cur_std_stderr = run_gwu(gwu, bases_dir, base, cur_std, None)
    # Sauvegarder une copie distincte des logs courants (standard)
    cur_std_log = bases_dir / f"{base}.golden_verify.stderr"
    if cur_std_stderr.exists():
        shutil.copy2(cur_std_stderr, cur_std_log)

    _, cur_outdir, cur_dir_stderr = run_gwu(gwu, bases_dir, base, cur_dir_marker, cur_outdir)
    # Sauvegarder logs -odir
    cur_dir_log = bases_dir / f"{base}.dir.golden_verify.stderr"
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

    rec = sub.add_parser("record", parents=[common], help="Enregistrer un golden pour la base")
    ver = sub.add_parser("verify", parents=[common], help="Vérifier la base contre le golden")

    args = parser.parse_args(argv)
    dist_dir = Path(args.dist)
    ignore_trailing_space = not args.no_ignore_trailing_space

    if args.cmd == "record":
        cmd_record(args.base, dist_dir, ignore_trailing_space)
        return 0
    if args.cmd == "verify":
        return cmd_verify(args.base, dist_dir, ignore_trailing_space)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


