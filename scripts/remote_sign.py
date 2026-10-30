import urllib.request
import urllib.parse
import json
import base64
import uuid
from pathlib import Path

def sign_via_shortcuty(shortcut_path: Path, output_path: Path):
    url = "https://sign.shortcuty.app/api/v1/sign?response=json"
    file_bytes = shortcut_path.read_bytes()
    filename = shortcut_path.name

    # Gerar multipart/form-data boundary
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
    print(f"[*] Enviando {filename} ({len(file_bytes)} bytes) para sign.shortcuty.app...")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw_resp = resp.read().decode('utf-8')
            res_json = json.loads(raw_resp)
            
            # Verificar se tem erro
            if "error" in res_json:
                print(f"[Erro] Shortcuty retornou erro: {res_json['error']}")
                return False
            
            # Extrair file.content_base64
            # O retorno pode ter chave "file": {"content_base64": "..."}
            b64_content = None
            if "file" in res_json and "content_base64" in res_json["file"]:
                b64_content = res_json["file"]["content_base64"]
            elif "content_base64" in res_json:
                b64_content = res_json["content_base64"]

            if not b64_content:
                print(f"[Erro] Resposta inesperada:\n{raw_resp[:500]}")
                return False

            signed_bytes = base64.b64decode(b64_content)
            header = signed_bytes[:4]
            print(f"[*] Header do arquivo assinado: {header}")
            
            output_path.write_bytes(signed_bytes)
            print(f"[SUCESSO] Arquivo assinado com sucesso! Salvo em: {output_path}")
            print(f"    Tamanho assinado: {len(signed_bytes)} bytes")
            print(f"    Formato Apple AEA: {'SIM (AEA1)' if header == b'AEA1' else 'NAO'}")
            return True

    except Exception as e:
        print(f"[Erro na requisicao]: {e}")
        return False

if __name__ == "__main__":
    src = Path("shortcuts/Salvar_no_Google_Keep.shortcut")
    dst = Path("shortcuts/Salvar_no_Google_Keep_Assinado.shortcut")
    sign_via_shortcuty(src, dst)
