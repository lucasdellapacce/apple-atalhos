# Apple Shortcuts E2E Factory 🍏

Automação ponta a ponta para desenvolvimento, compilação, validação estrutural e assinatura criptográfica oficial de **Apple Shortcuts** para iOS / iPadOS / macOS.

## Funcionalidades
- **Compilador Cherri & Gerador Plist**: Suporte a código declarativo de alto nível e manipulação direta de nós XML/plist nativos da Apple.
- **Assinatura Oficial Criptográfica (`AEA1`)**: Pipeline em nuvem via GitHub Actions rodando em runner `macos-latest` com o utilitário nativo da Apple `shortcuts sign --mode anyone`.
- **Exportação Automática**: Integração com Google Drive e publicação imediata em Releases para download direto e importação com 1 toque no iPhone (iOS).
- **Integração com Scriptable**: Suporte a fluxos avançados de automação combinando Shortcuts + JavaScript.
