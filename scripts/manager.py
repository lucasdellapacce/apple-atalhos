#!/usr/bin/env python3
"""
Apple Shortcuts E2E Manager
Compila, valida, assina na nuvem (GitHub Actions macOS) e exporta para o Google Drive e links diretos.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
CHERRI_BIN = Path(r"C:\Users\lucas\.codex\skills\apple-shortcuts-master\tools\cherri.exe")
SHORTCUTS_TO_SIGN = WORKSPACE / "shortcuts-to-sign"
SIGNED_DIR = WORKSPACE / "signed"
GDRIVE_DIR = Path(r"G:\Meu Drive\03_PROJETOS_E_AUTOMACOES\Atalhos_Apple")

def ensure_dirs():
    SHORTCUTS_TO_SIGN.mkdir(parents=True, exist_ok=True)
    SIGNED_DIR.mkdir(parents=True, exist_ok=True)
    try:
        GDRIVE_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[Aviso] Nao foi possivel acessar a pasta do Google Drive: {e}")

def compile_cherri(source_file: Path, output_file: Path) -> bool:
    print(f"[*] Compilando arquivo Cherri: {source_file}...")
    cmd = [
        str(CHERRI_BIN),
        str(source_file),
        "-o", str(output_file),
        "--skip-sign"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[Erro] Falha ao compilar Cherri:\n{res.stderr}\n{res.stdout}")
        return False
    print("[OK] Compilacao Cherri concluida com sucesso!")
    return True

def trigger_cloud_signing():
    print("[*] Sincronizando com GitHub para assinatura remota via macOS Runner...")
    subprocess.run(["git", "add", "."], cwd=str(WORKSPACE), check=True)
    
    status = subprocess.run(["git", "status", "--porcelain"], cwd=str(WORKSPACE), capture_output=True, text=True)
    if status.stdout.strip():
        subprocess.run(["git", "commit", "-m", "chore: solicitar assinatura de atalhos"], cwd=str(WORKSPACE), check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=str(WORKSPACE), check=True)
    else:
        print("[*] Sem mudancas para commit. Disparando workflow manualmente...")
        subprocess.run(["gh", "workflow", "run", "sign.yml"], cwd=str(WORKSPACE), check=True)

    print("[*] Aguardando execucao do runner macOS no GitHub Actions...")
    time.sleep(5)
    
    # Obter o último run id
    for attempt in range(60):
        runs = subprocess.run(
            ["gh", "run", "list", "--workflow=sign.yml", "--limit", "1", "--json", "databaseId,status,conclusion"],
            cwd=str(WORKSPACE), capture_output=True, text=True
        )
        import json
        data = json.loads(runs.stdout)
        if data:
            run = data[0]
            status = run.get("status")
            conclusion = run.get("conclusion")
            print(f"    Status da assinatura: {status} ({conclusion or 'em andamento'})...")
            if status == "completed":
                if conclusion == "success":
                    print("[OK] Assinatura no macOS concluida com sucesso!")
                    break
                else:
                    print(f"[Erro] Workflow finalizou com erro: {conclusion}")
                    return False
        time.sleep(10)
    
    # Baixar artefatos assinados
    print("[*] Baixando atalhos assinados...")
    subprocess.run(["gh", "run", "download", "--name", "signed-shortcuts", "--dir", str(SIGNED_DIR)], cwd=str(WORKSPACE), check=True)
    return True

def export_to_destinations(shortcut_name: str):
    signed_file = SIGNED_DIR / f"{shortcut_name}.shortcut"
    if not signed_file.exists():
        signed_file = SIGNED_DIR / shortcut_name
    
    if not signed_file.exists():
        print(f"[Erro] Arquivo assinado {signed_file} nao encontrado!")
        return

    # Verificar se é AEA1
    header = signed_file.read_bytes()[:4]
    print(f"[*] Verificacao de envelope AEA: {header}")
    if header != b'AEA1':
        print("[Aviso] O arquivo nao possui o header binario oficial AEA1 da Apple!")

    # Copiar para Google Drive
    if GDRIVE_DIR.exists():
        dest = GDRIVE_DIR / signed_file.name
        shutil.copy2(signed_file, dest)
        print(f"[OK] Salvo no Google Drive: {dest}")

    # Obter URL do GitHub Release
    repo_url = subprocess.run(["gh", "repo", "view", "--json", "url", "-q", ".url"], cwd=str(WORKSPACE), capture_output=True, text=True).stdout.strip()
    download_url = f"{repo_url}/releases/download/latest/{signed_file.name}"
    print(f"\n=======================================================")
    print(f" ATALHO PRONTO E ASSINADO PARA O iOS:")
    print(f" Nome: {signed_file.name}")
    print(f" Link Direto (Safari / iPhone): {download_url}")
    print(f" Google Drive: {GDRIVE_DIR / signed_file.name}")
    print(f"=======================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Apple Shortcuts E2E Manager")
    parser.add_argument("--compile", type=Path, help="Caminho do arquivo .cherri")
    parser.add_argument("--sign", action="store_true", help="Disparar assinatura na nuvem")
    parser.add_argument("--name", type=str, help="Nome do atalho")
    args = parser.parse_args()

    ensure_dirs()

    if args.compile:
        name = args.name or args.compile.stem
        out = SHORTCUTS_TO_SIGN / f"{name}.shortcut"
        if not compile_cherri(args.compile, out):
            sys.exit(1)

    if args.sign:
        if not trigger_cloud_signing():
            sys.exit(1)
        if args.name:
            export_to_destinations(args.name)
        else:
            for f in SHORTCUTS_TO_SIGN.glob("*.shortcut"):
                export_to_destinations(f.name)

if __name__ == "__main__":
    main()
