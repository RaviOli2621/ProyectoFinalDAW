function minutosAHHMMSS(minutos) {
    minutos = parseInt(minutos);
    if (isNaN(minutos)) return minutos; 
    const h = Math.floor(minutos / 60);
    const m = Math.floor(minutos % 60);
    return (h < 10 ? "0" : "") + h + ":" +
        (m < 10 ? "0" : "") + m + ":00";
}

document.addEventListener('DOMContentLoaded', function() {
    const inputDuracion = document.getElementById('id_duracion');
    if (inputDuracion && inputDuracion.value && !inputDuracion.value.includes(':')) {
        inputDuracion.value = minutosAHHMMSS(inputDuracion.value);
    }
});