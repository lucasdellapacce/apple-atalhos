import urllib.request
import plistlib
import json

req = urllib.request.Request('https://www.icloud.com/shortcuts/api/records/4cd1f1d774eb460e8f24749eaa7b6b4b', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())

dl = data['fields']['shortcut']['value']['downloadURL'].replace('${f}', 'shortcut.shortcut')
req_dl = urllib.request.Request(dl, headers={'User-Agent': 'Mozilla/5.0'})
data = urllib.request.urlopen(req_dl).read()

plist = plistlib.loads(data)
a29 = plist['WFWorkflowActions'][29]
print("ACTION 29:")
print(json.dumps(a29, indent=2))

# Salvar o shortcut do tojioo localmente para guardar
with open('shortcuts/Sign_Shortcut_File_by_tojioo.shortcut', 'wb') as f:
    f.write(data)
print("Salvo em shortcuts/Sign_Shortcut_File_by_tojioo.shortcut")
