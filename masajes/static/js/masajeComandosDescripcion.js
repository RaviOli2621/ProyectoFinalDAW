document.addEventListener('DOMContentLoaded', function() {
    // Selecciona el primer elemento con clase 'textarea'
    const textareaDiv = document.querySelector('.textarea');
    if (textareaDiv) {
        // Reemplaza \n por salto de línea y \t por tabulación visual
        let html = textareaDiv.innerHTML
            .replace(/\\n/g, '<br>')
            .replace(/\\t/g, '&emsp;');
        textareaDiv.innerHTML = html;
    }
});