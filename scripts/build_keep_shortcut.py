#!/usr/bin/env python3
"""
Gerador de Atalho Apple: Salvar no Google Keep
Gera o fluxo nativo: Ask for Input -> Set Clipboard -> Share Sheet -> Open Google Keep
"""
import plistlib
import uuid
from pathlib import Path

def create_keep_shortcut():
    ask_uuid = str(uuid.uuid4()).upper()
    
    actions = [
        # Acao 1: Solicitar entrada de texto (Ask for Input)
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.ask",
            "WFWorkflowActionParameters": {
                "UUID": ask_uuid,
                "WFAskActionPrompt": "O que você deseja anotar no Google Keep?",
                "WFInputType": "Text",
                "WFAllowsMultilineText": True
            }
        },
        # Acao 2: Copiar para a Area de Transferencia (Set Clipboard)
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.setclipboard",
            "WFWorkflowActionParameters": {
                "WFInput": {
                    "Value": {
                        "OutputName": "Entrada Fornecida",
                        "OutputUUID": ask_uuid,
                        "Type": "ActionOutput"
                    },
                    "WFSerializationType": "WFTextTokenAttachment"
                },
                "WFLocalOnly": False
            }
        },
        # Acao 3: Compartilhar com Google Keep via Folha de Compartilhamento (Share)
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.sharesheet",
            "WFWorkflowActionParameters": {
                "WFInput": {
                    "Value": {
                        "OutputName": "Entrada Fornecida",
                        "OutputUUID": ask_uuid,
                        "Type": "ActionOutput"
                    },
                    "WFSerializationType": "WFTextTokenAttachment"
                }
            }
        },
        # Acao 4: Notificacao amigavel de conclusao
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.notification",
            "WFWorkflowActionParameters": {
                "WFNotificationActionBody": "Texto copiado e compartilhado no Google Keep!",
                "WFNotificationActionTitle": "Google Keep"
            }
        }
    ]

    workflow = {
        "WFWorkflowActions": actions,
        "WFWorkflowName": "Salvar no Google Keep",
        "WFWorkflowClientRelease": "27.0",
        "WFWorkflowClientVersion": "5037.0.17",
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowTypes": ["ActionExtension", "QuickActions"],
        "WFWorkflowInputContentItemClasses": ["WFStringContentItem"],
        "WFWorkflowImportQuestions": [],
        "WFWorkflowIcon": {
            # Amarelo iconico do Google Keep
            "WFWorkflowIconStartColor": 4274264319,
            "WFWorkflowIconGlyphNumber": 59685
        }
    }

    return workflow

if __name__ == "__main__":
    wf = create_keep_shortcut()
    out_dir = Path(r"c:\Users\lucas\apple-atalhos\shortcuts")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "Salvar_no_Google_Keep.shortcut"
    
    with open(out_file, "wb") as f:
        plistlib.dump(wf, f, fmt=plistlib.FMT_XML)
    
    print(f"[OK] Atalho gerado em: {out_file}")
