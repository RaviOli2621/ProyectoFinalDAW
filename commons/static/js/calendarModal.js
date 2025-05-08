let calendar = null;
let diaSeleccionado = ""; // Variable para almacenar el día numerico seleccionado
let currentAbortController = null;  // Variable para almacenar el controlador de la última solicitud
let dayCellG; // Variable para almacenar la celda del día seleccionado

function showCalendarModal() {
    showConfirmModal(10, idModal = "CalendarioMD");
    diaSeleccionado = "";
    const calendarEl = document.getElementById('calendar');

    if (!calendar) {
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
                duracion = document.getElementById("id_duracion").value;
                fetch(`/api/calendario/?year=${year}&month=${month}&blue='False'&duracion=${duracion}`, { signal: abortController.signal })
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
                    showToast("No se pueden seleccionar días pasados o el día de hoy", "info", 5000);
                    return;
                }

                const event = info.view.calendar.getEvents().find(e => e.startStr === info.dateStr);
                const backgroundColor = event ? event.backgroundColor : window.getComputedStyle(dayCell).backgroundColor;
                console.log("Color de fondo del día seleccionado:", backgroundColor);

                if (backgroundColor != "red" && backgroundColor != "gray") {
                    diaSeleccionado = info.dateStr + "T00:00";
                    dayCell = info.dayEl;
                    dayCell.style.filter = "opacity(50%)";
                    if (dayCellG) dayCellG.style.filter = "";
                    if(dayCellG == dayCell) {
                        dayCellG = null;
                        diaSeleccionado = ""; 
                    }
                    else dayCellG = dayCell;
                } else {
                    showToast("Dia completo/festivo", "error", 5000);
                }
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
    dia = document.getElementById("id_fecha_date").value;
    duracion = document.getElementById("id_duracion").value;
    
    if(dia){
        showConfirmModal(10,"HorasMD");
        document.getElementById("modalConfirmHoras")?.remove();
        setTimeout(() => {
            fetch(`/api/horas/?fecha=${dia}&duracion=${duracion}`)
                .then(response => response.json())
                .then(data => {
                    console.log("Horas disponibles:", data);
                    
                    let modalBody = document.querySelector('#HorasMD .custom-modal-body');
                    if(!modalBody) modalBody = document.querySelector('#HorasMD .modal-body');
                    if(!modalBody) modalBody = document.getElementById('HorasMD').querySelector('div');
                    
                    if(modalBody) {
                        modalBody.innerHTML = "";
                        
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
        }, 200); 
    } else {
        showToast("No hay día seleccionado", "error", 5000);
    }
}

function selectHour(dateTime) {
    console.log('Selected datetime:', dateTime);
    
    let timePart = dateTime.split('T')[1];
    if (timePart) {
        timePart = timePart.substring(0, 5);
        
        const timeField = document.getElementById('id_fecha_time');
        timeField.value = timePart;
        console.log('Set time to:', timePart);
        
        syncDateTime();
    }
    
    $('.custom-modal').hide(); 
}

function createHours(data){
    const hoursContainer = document.createElement('div');
    hoursContainer.className = 'hours-container';
    hoursContainer.style.display = 'flex';
    hoursContainer.style.flexWrap = 'wrap';
    hoursContainer.style.justifyContent = 'center';
    hoursContainer.style.gap = '10px';
    hoursContainer.style.margin = '15px 0';
    
    data.forEach(hora => {
        const horaElement = document.createElement('div');
        horaElement.textContent = hora.fecha.split('T')[1].substring(0, 5); 
        
        horaElement.style.padding = '10px 15px';
        horaElement.style.borderRadius = '5px';
        horaElement.style.cursor = 'pointer';
        
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
        const datePart = diaSeleccionado.split('T')[0];
        
        document.getElementById('id_fecha_date').value = datePart;
        
        const currentTime = document.getElementById('id_fecha_time').value || "00:00";
        document.getElementById('id_fecha').value = `${datePart}T${currentTime}`;
        
        diaSeleccionado = "";
        dayCellG.style.filter = ""; 
        $('.custom-modal').hide(); 
        showHourModal();
    }
});

function syncDateTime() {
    const dateField = document.getElementById('id_fecha_date');
    const timeField = document.getElementById('id_fecha_time');
    const datetimeField = document.getElementById('id_fecha');
    
    if (dateField.value && timeField.value) {
        datetimeField.value = `${dateField.value}T${timeField.value}`;
        console.log('Synchronized datetime:', datetimeField.value);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const timeField = document.getElementById('id_fecha_time');
    const dateField = document.getElementById('id_fecha_date');
    const datetimeField = document.getElementById('id_fecha');
    
    if (dateField.value && !timeField.value && datetimeField.value) {
        const timePart = datetimeField.value.split('T')[1];
        if (timePart) {
            timeField.value = timePart.substring(0, 5);
        } else {
            timeField.value = '09:00';
        }
    }
    
    console.log('Initial date:', dateField.value);
    console.log('Initial time:', timeField.value);
    console.log('Initial datetime:', datetimeField.value);
});