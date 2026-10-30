#!/usr/bin/env python3
"""
Apple Shortcuts E2E Factory & Sync Manager
Gerador, Validador, Sincronizador com Google Drive e Link Direto no GitHub.
"""
import argparse
import hashlib
import json
import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
CHERRI_BIN = Path(r"C:\Users\lucas\.gemini\config\skills\apple-shortcuts-master\tools\cherri.exe")
SHORTCUTS_DIR = WORKSPACE / "shortcuts"
GDRIVE_DIR = Path(r"G:\Meu Drive\03_PROJETOS_E_AUTOMACOES\Atalhos_Apple")
REPO_RAW_BASE = "https://raw.githubusercontent.com/lucasdellapacce/apple-atalhos/main/shortcuts"

def ensure_environment():
    SHORTCUTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        GDRIVE_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[Aviso] Nao foi possivel criar pasta no Google Drive: {e}")

def compile_cherri(source_file: Path, output_file: Path) -> bool:
    print(f"[*] Compilando Cherri: {source_file} -> {output_file}...")
    cmd = [
        str(CHERRI_BIN),
        str(source_file),
        "-o", str(output_file),
        "--skip-sign"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[Erro] Falha na compilacao Cherri:\n{res.stderr}\n{res.stdout}")
        return False
    print("[OK] Compilacao concluida.")
    return True

def validate_shortcut(shortcut_path: Path) -> bool:
    print(f"[*] Validando estrutura de {shortcut_path.name}...")
    try:
        data = shortcut_path.read_bytes()
        plist = plistlib.loads(data)
        actions = plist.get("WFWorkflowActions", [])
        print(f"[OK] Valido! Contem {len(actions)} acoes.")
        return True
    except Exception as e:
        print(f"[Erro] Estrutura invalida: {e}")
        return False

def sync_and_publish(shortcut_path: Path):
    name = shortcut_path.name
    print(f"\n[*] Publicando e sincronizando {name}...")

    # 1. Copiar para o Google Drive
    gdrive_dest = GDRIVE_DIR / name
    try:
        shutil.copy2(shortcut_path, gdrive_dest)
        print(f"[OK] Salvo no Google Drive: {gdrive_dest}")
    except Exception as e:
        print(f"[Aviso] Falha ao copiar para Google Drive: {e}")

    # 2. Git Commit & Push
    try:
        subprocess.run(["git", "add", "."], cwd=str(WORKSPACE), check=True)
        status = subprocess.run(["git", "status", "--porcelain"], cwd=str(WORKSPACE), capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(["git", "commit", "-m", f"feat(shortcut): adicionar {name}"], cwd=str(WORKSPACE), check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=str(WORKSPACE), check=True)
            print("[OK] Sincronizado com GitHub com sucesso.")
    except Exception as e:
        print(f"[Aviso] Erro no git sync: {e}")

    # 3. Exibir Links de Download
    raw_url = f"{REPO_RAW_BASE}/{name}"
    print("\n" + "="*60)
    print(f"  ATALHO PRONTO PARA IMPORTAR NO SEU IPHONE!")
    print(f"  Nome: {name}")
    print(f"  Link Direto (Safari): {raw_url}")
    print(f"  Google Drive: {gdrive_dest}")
    print("="*60 + "\n")
    return raw_url

def main():
    parser = argparse.ArgumentParser(description="Apple Shortcuts Factory")
    parser.add_argument("--cherri", type=Path, help="Compilar fonte Cherri")
    parser.add_argument("--shortcut", type=Path, help="Processar arquivo .shortcut existente")
    parser.add_argument("--name", type=str, help="Nome do atalho de saida")
    args = parser.parse_args()

    ensure_environment()

    if args.cherri:
        name = args.name or args.cherri.stem
        out = SHORTCUTS_DIR / f"{name}.shortcut"
        if compile_cherri(args.cherri, out):
            validate_shortcut(out)
            sync_and_publish(out)
    elif args.shortcut:
        dest = SHORTCUTS_DIR / args.shortcut.name
        shutil.copy2(args.shortcut, dest)
        validate_shortcut(dest)
        sync_and_publish(dest)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
