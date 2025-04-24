let calendar = null;
let diaSeleccionado = ""; // Variable para almacenar el día numerico seleccionado
let currentAbortController = null;  // Variable para almacenar el controlador de la última solicitud
let dayCellG; // Variable para almacenar la celda del día seleccionado
let colorSeleccionado = ""; // Nuevo: para guardar el color del día seleccionado

let lastId = 0
function showCalendarModal(id) {
    showConfirmModal(10, idModal = "CalendarioMD");
    diaSeleccionado = "";
    colorSeleccionado = "";
    const calendarEl = document.getElementById('calendar');

    if (!calendar || lastId != id) {
        lastId = id;
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'es',
            height: 'auto',

            events: function(fetchInfo, successCallback, failureCallback) {
                const middleDate = new Date((fetchInfo.start.getTime() + fetchInfo.end.getTime()) / 2);
                const year = middleDate.getFullYear();
                const month = middleDate.getMonth() + 1;

                removeToasts();
                showToast("Cargando dias del mes...", "info", 99999);
                if (currentAbortController) {
                    currentAbortController.abort();
                }
                const abortController = new AbortController();
                currentAbortController = abortController;

                fetch(`/api/calendari/fiestas/trabajador/?year=${year}&month=${month}&idTrabajador=${id}`, { signal: abortController.signal })
                    .then(response => response.json())
                    .then(data => {
                        removeToasts(true);
                        successCallback(data);
                    })
                    .catch(err => {
                        console.error("Error al cargar eventos:", err);
                        failureCallback(err);
                    });
            },
            dateClick: function(info) {
                const today = new Date().toISOString().split('T')[0];
                if (info.dateStr <= today) {
                    showToast("No se pueden seleccionar días pasados o el día de hoy", "error", 5000);
                    return;
                }

                const event = info.view.calendar.getEvents().find(e => e.startStr === info.dateStr);
                let backgroundColor = event ? event.backgroundColor : window.getComputedStyle(info.dayEl).backgroundColor;
                // Convertir a rgb si es necesario
                if (backgroundColor.startsWith('rgb')) {
                    // Gris: rgb(128, 128, 128) o similar
                    if (backgroundColor.includes('128, 128, 128')) backgroundColor = "gray";
                }
                // Guardar el color seleccionado
                colorSeleccionado = backgroundColor;

                if (backgroundColor === "gray") {
                    showToast("Dia completo/festivo", "error", 5000);
                    return;
                }

                diaSeleccionado = info.dateStr + "T00:00";
                dayCell = info.dayEl;
                dayCell.style.filter = "opacity(50%)";
                if (dayCellG) dayCellG.style.filter = "";
                if(dayCellG == dayCell) {
                    dayCellG = null;
                    diaSeleccionado = ""; 
                    colorSeleccionado = "";
                }
                else dayCellG = dayCell;
            },
            eventContent: function(arg) {
                return { domNodes: [] };
            }
        });
        calendar.render();
    } else {
        calendar.removeAllEvents();
        calendar.refetchEvents();
    }
}


$('#modalConfirmCalendario').click(function() { 
    if (diaSeleccionado != "") {
        // Extraer color base (puede ser rgb, hex o nombre)
        let color = colorSeleccionado;
        // Normalizar colores
        if (color.startsWith('#')) {
            if (color.toLowerCase() === "#4caf50") color = "green";
            else if (color.toLowerCase() === "#ff9800") color = "orange";
            else if (color.toLowerCase() === "#f44336") color = "red";
            else if (color.toLowerCase() === "#2196f3") color = "blue";
        }
        // Si es rgb, convertir a nombre
        if (color.startsWith('rgb')) {
            if (color.replace(/ /g,'').includes('76,175,80')) color = "green";
            else if (color.replace(/ /g,'').includes('255,152,0')) color = "orange";
            else if (color.replace(/ /g,'').includes('244,67,54')) color = "red";
            else if (color.replace(/ /g,'').includes('33,150,243')) color = "blue";
            else if (color.replace(/ /g,'').includes('128,128,128')) color = "gray";
        }
        // También aceptar el nombre directamente
        color = color.toLowerCase();
        let fechaFormateada = diaSeleccionado.split('T')[0]; // Extract YYYY-MM-DD
        let partesFecha = fechaFormateada.split('-'); // Split into [YYYY, MM, DD]
        fechaFormateada = `${partesFecha[0]}-${partesFecha[1]}-${partesFecha[2]}`; // Rearrange to DD-MM-YYYY
        if (color === "green" || color === "orange") {
            changeWorkerFestivity(fechaFormateada, lastId, {message:"¡Se ha dado fiesta al trabajador!", status:"success", time:4000});
        } else if (color === "red") {
            showToast("Si le das fiesta, un cliente no podrá ser atendido", "error", 5000);
        } else if (color === "blue") {
            changeWorkerFestivity(fechaFormateada, lastId, {message:"¡Se ha quitado la fiesta al trabajador!", status:"info", time:4000});
        } else if (color === "gray") {
            showToast("Dia festivo", "error", 5000);
        } else {
            showToast("Selecciona un día válido", "error", 4000);
        }
    }
});
//Toast es un objeto que tiene que contener el mensaje, el tipo y la duración
function changeWorkerFestivity(fecha, id, toast) {
    fetch(`/api/calendari/fiestas/trabajador/${id}/?fecha=${fecha}`)
    .then(response => response.json())
    .then(data => {
        removeToasts(true);
        showToast(toast.message, toast.status, toast.time);
        $('.custom-modal').hide();
        dayCellG.style.filter = "";
        dayCellG = null;
        diaSeleccionado = "";
    })
    .catch(err => {
        showToast("Error al cambiar la festividad: " + err, "error", 5000);
    });
}
// Initialize fields on page load
document.addEventListener('DOMContentLoaded', function() {
    const timeField = document.getElementById('id_fecha_time');
    const dateField = document.getElementById('id_fecha_date');
    const datetimeField = document.getElementById('id_fecha');
    
    // If date field has value but time field is empty, extract time from datetime
    if (dateField.value && !timeField.value && datetimeField.value) {
        const timePart = datetimeField.value.split('T')[1];
        if (timePart) {
            timeField.value = timePart.substring(0, 5);
        } else {
            // Set default time
            timeField.value = '09:00';
        }
    }
    
    // Log initial values for debugging
    console.log('Initial date:', dateField.value);
    console.log('Initial time:', timeField.value);
    console.log('Initial datetime:', datetimeField.value);
});