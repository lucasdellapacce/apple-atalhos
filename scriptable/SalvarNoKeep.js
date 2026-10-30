// Variables used by Scriptable.
// These must be at the very top of the file. Do not edit.
// icon-color: yellow; icon-glyph: sticky-note;

/**
 * Scriptable Helper: Salvar Nota
 * Recebe o texto do atalho, formata e aciona a partilha com o Google Keep
 */
let texto = args.shortcutParameter;

if (!texto) {
    let alert = new Alert();
    alert.title = "Nova Nota";
    alert.message = "Digite o conteúdo da sua nota:";
    alert.addTextField("Nota...");
    alert.addAction("Salvar");
    alert.addCancelAction("Cancelar");
    await alert.presentAlert();
    texto = alert.textFieldValue(0);
}

if (texto && texto.trim().length > 0) {
    // Formata a data atual
    let agora = new Date();
    let dataStr = agora.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    let notaFinal = `[${dataStr}]\n${texto}`;

    // Copia para a area de transferencia
    Pasteboard.copy(notaFinal);

    // Compartilha diretamente com a folha nativa (onde o Google Keep fica disponivel)
    await ShareSheet.present([notaFinal]);

    Script.setShortcutOutput(notaFinal);
}

Script.complete();
