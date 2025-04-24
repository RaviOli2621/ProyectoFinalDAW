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

function showHourModal() {
    // Use the date from the date field instead of datetime field
    dia = document.getElementById("id_fecha_date").value;
    if(dia){
        showConfirmModal(10,"HorasMD");
        document.getElementById("modalConfirmHoras")?.remove();
        // Give time for the modal to render in the DOM
        setTimeout(() => {
            fetch(`/api/horas/?fecha=${dia}`)
                .then(response => response.json())
                .then(data => {
                    console.log("Horas disponibles:", data);
                    
                    // Try different approaches to find modal container
                    let modalBody = document.querySelector('#HorasMD .custom-modal-body');
                    if(!modalBody) modalBody = document.querySelector('#HorasMD .modal-body');
                    if(!modalBody) modalBody = document.getElementById('HorasMD').querySelector('div');
                    
                    if(modalBody) {
                        // Clear previous content
                        modalBody.innerHTML = "";
                        
                        // Use the createHours function to generate the hours UI
                        const hoursContainer = createHours(data);
                        modalBody.appendChild(hoursContainer);
                    } else {
                        console.error("Modal container not found - HorasMD", document.getElementById('HorasMD'));
                        showToast("Error al mostrar las horas - contenedor no encontrado", "error", 5000);
                    }
                })
                .catch(err => {
                    console.error("Error al cargar las horas:", err);
                    showToast("Error al cargar las horas", "error", 5000);
                });
        }, 200); // Increased delay to ensure modal is fully rendered
    } else {
        showToast("No hay día seleccionado", "error", 5000);
    }
}

function selectHour(dateTime) {
    console.log('Selected datetime:', dateTime);
    
    // Extract time portion from the datetime string
    let timePart = dateTime.split('T')[1];
    if (timePart) {
        // Remove seconds if present
        timePart = timePart.substring(0, 5);
        
        // Update the time field
        const timeField = document.getElementById('id_fecha_time');
        timeField.value = timePart;
        console.log('Set time to:', timePart);
        
        // Sync with the hidden datetime field
        syncDateTime();
    }
    
    $('.custom-modal').hide();  // Hide the modal
}

function createHours(data){
    // Create a container for the hours with styling
    const hoursContainer = document.createElement('div');
    hoursContainer.className = 'hours-container';
    hoursContainer.style.display = 'flex';
    hoursContainer.style.flexWrap = 'wrap';
    hoursContainer.style.justifyContent = 'center';
    hoursContainer.style.gap = '10px';
    hoursContainer.style.margin = '15px 0';
    
    data.forEach(hora => {
        const horaElement = document.createElement('div');
        horaElement.textContent = hora.fecha.split('T')[1].substring(0, 5); // Extraer solo la hora HH:MM
        
        // Add explicit styles to make hours visible
        horaElement.style.padding = '10px 15px';
        horaElement.style.borderRadius = '5px';
        horaElement.style.cursor = 'pointer';
        
        // Set background color based on availability
        if(hora.color === 'green') {
            horaElement.style.backgroundColor = '#4CAF50';
            horaElement.style.color = 'white';
        } else if(hora.color === 'orange') {
            horaElement.style.backgroundColor = '#FF9800';
            horaElement.style.color = 'black';
        } else if(hora.color === 'red') {
            horaElement.style.backgroundColor = '#F44336';
            horaElement.style.color = 'white';
            horaElement.style.opacity = '0.6';
            horaElement.style.cursor = 'not-allowed';
        }
        
        if(hora.color !== 'red') {
            horaElement.addEventListener('click', () => {
                selectHour(hora.fecha);
            });
        }
        
        hoursContainer.appendChild(horaElement);
    });
    return hoursContainer;
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

        if (color === "green" || color === "orange") {
            showToast("¡Se ha dado fiesta al trabajador!", "success", 4000);
            $('.custom-modal').hide();
        } else if (color === "red") {
            showToast("Si le das fiesta, un cliente no podrá ser atendido", "error", 5000);
        } else if (color === "blue") {
            showToast("¡Se ha quitado la fiesta al trabajador!", "info", 4000);
            $('.custom-modal').hide();
        } else if (color === "gray") {
            showToast("Dia completo/festivo", "error", 5000);
        } else {
            showToast("Selecciona un día válido", "error", 4000);
        }
    }
});

function syncDateTime() {
    const dateField = document.getElementById('id_fecha_date');
    const timeField = document.getElementById('id_fecha_time');
    const datetimeField = document.getElementById('id_fecha');
    
    // Only proceed if both fields have values
    if (dateField.value && timeField.value) {
        datetimeField.value = `${dateField.value}T${timeField.value}`;
        console.log('Synchronized datetime:', datetimeField.value);
    }
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