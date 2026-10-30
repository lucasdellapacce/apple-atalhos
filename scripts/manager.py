#!/usr/bin/env python3
"""
Apple Shortcuts E2E Factory & Sync Manager
Gerador, Validador, Assinador Remoto (AEA1), Sincronizador com Google Drive e Link Direto no GitHub.
"""
import argparse
import base64
import json
import os
import plistlib
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
import urllib.request

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

def sign_shortcut(source_path: Path, signed_path: Path) -> bool:
    print(f"[*] Assinando criptograficamente ({source_path.name}) via motor oficial AEA...")
    url = "https://sign.shortcuty.app/api/v1/sign?response=json"
    file_bytes = source_path.read_bytes()
    filename = source_path.name

    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
    body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
    body.extend(file_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    headers = {
        "User-Agent": "Shortcuts/3107.0.8.2 CFNetwork/1498.700.2 Darwin/23.6.0",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept": "application/json"
    }

    req = urllib.request.Request(url, data=bytes(body), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            if "error" in res_json:
                print(f"[Erro] Falha na assinatura: {res_json['error']}")
                return False
            
            b64_content = None
            if "file" in res_json and "content_base64" in res_json["file"]:
                b64_content = res_json["file"]["content_base64"]
            elif "content_base64" in res_json:
                b64_content = res_json["content_base64"]

            if not b64_content:
                print(f"[Erro] Resposta invalida.")
                return False

            signed_bytes = base64.b64decode(b64_content)
            if not signed_bytes.startswith(b'AEA1'):
                print(f"[Aviso] O arquivo assinado nao possui o header AEA1.")
            
            signed_path.write_bytes(signed_bytes)
            print(f"[SUCESSO] Assinatura digital concluida: {len(signed_bytes)} bytes (AEA1)")
            return True
    except Exception as e:
        print(f"[Erro] Requisicao de assinatura falhou: {e}")
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
            subprocess.run(["git", "commit", "-m", f"feat(shortcut): atualizar/adicionar {name} assinado"], cwd=str(WORKSPACE), check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=str(WORKSPACE), check=True)
            print("[OK] Sincronizado com GitHub com sucesso.")
    except Exception as e:
        print(f"[Aviso] Erro no git sync: {e}")

    # 3. Exibir Links de Download
    raw_url = f"{REPO_RAW_BASE}/{name}"
    print("\n" + "="*60)
    print(f"  ATALHO ASSINADO PRONTO PARA IMPORTAR NO SEU IPHONE!")
    print(f"  Nome: {name}")
    print(f"  Link Direto (Safari): {raw_url}")
    print(f"  Google Drive: {gdrive_dest}")
    print("="*60 + "\n")
    return raw_url

def main():
    parser = argparse.ArgumentParser(description="Apple Shortcuts Factory")
    parser.add_argument("--shortcut", type=Path, help="Processar e assinar arquivo .shortcut existente")
    args = parser.parse_args()

    ensure_environment()

    if args.shortcut:
        base_name = args.shortcut.stem.replace("_Assinado", "")
        signed_file = SHORTCUTS_DIR / f"{base_name}.shortcut"
        
        # Assinar
        if sign_shortcut(args.shortcut, signed_file):
            sync_and_publish(signed_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
