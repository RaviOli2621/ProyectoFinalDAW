let calendar = null;
let diasSeleccionados = []; // Array para almacenar los días seleccionados
let currentAbortController = null;
let dayCellsSeleccionadas = []; // Array para almacenar las celdas seleccionadas
let colorSeleccionado = "";
let lastId = 0;

function showCalendarModal(id) {
    showConfirmModal(10, idModal = "CalendarioMD");
    diasSeleccionados = [];
    dayCellsSeleccionadas = [];
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
                if (backgroundColor.startsWith('rgb')) {
                    if (backgroundColor.includes('128, 128, 128')) backgroundColor = "gray";
                }
                colorSeleccionado = backgroundColor;

                let color = colorSeleccionado;
                if (color.startsWith('#')) {
                    if (color.toLowerCase() === "#4caf50") color = "green";
                    else if (color.toLowerCase() === "#ff9800") color = "orange";
                    else if (color.toLowerCase() === "#f44336") color = "red";
                    else if (color.toLowerCase() === "#2196f3") color = "blue";
                }
                if (color.startsWith('rgb')) {
                    if (color.replace(/ /g,'').includes('76,175,80')) color = "green";
                    else if (color.replace(/ /g,'').includes('255,152,0')) color = "orange";
                    else if (color.replace(/ /g,'').includes('244,67,54')) color = "red";
                    else if (color.replace(/ /g,'').includes('33,150,243')) color = "blue";
                    else if (color.replace(/ /g,'').includes('128,128,128')) color = "gray";
                }
                color = color.toLowerCase();

                if (color === "gray") {
                    showToast("Dia completo/festivo", "error", 5000);
                    return;
                }


                let fechaSeleccionada = info.dateStr + "T00:00";
                let index = diasSeleccionados.indexOf(fechaSeleccionada);
                if (index !== -1) {
                    diasSeleccionados.splice(index, 1);
                    info.dayEl.style.filter = "";
                    dayCellsSeleccionadas = dayCellsSeleccionadas.filter(cell => cell !== info.dayEl);
                } else {
                    diasSeleccionados.push(fechaSeleccionada);
                    info.dayEl.style.filter = "opacity(50%)";
                    dayCellsSeleccionadas.push(info.dayEl);
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

    calendar.on('datesSet', function(info) {
        document.querySelectorAll('.fc-daygrid-day').forEach(cell => {
            cell.style.filter = "";
        });
        diasSeleccionados.forEach(dia => {
            const fechaSinHora = dia.split('T')[0];
            const celda = Array.from(document.querySelectorAll('.fc-daygrid-day')).find(
                cell => cell.getAttribute('data-date') === fechaSinHora
            );
            if (celda) {
                celda.style.filter = "opacity(50%)";
                if (!dayCellsSeleccionadas.includes(celda)) {
                    dayCellsSeleccionadas.push(celda);
                }
            }
        });
    });
}

$('#modalConfirmCalendario').off('click').on('click', function() {
    if (diasSeleccionados.length === 0) {
        showToast("Selecciona al menos un día válido", "error", 4000);
        return;
    }

    let hayRojo = false;
    let diasRojos = [];
    diasSeleccionados.forEach(dia => {
        const fechaSinHora = dia.split('T')[0];
        const celda = Array.from(document.querySelectorAll('.fc-daygrid-day')).find(
            cell => cell.getAttribute('data-date') === fechaSinHora
        );
        let backgroundColor = "";
        if (celda) {
            const event = calendar.getEvents().find(e => e.startStr.startsWith(fechaSinHora));
            backgroundColor = event ? event.backgroundColor : "";
        }
        let color = backgroundColor.toLowerCase();
        if (color === "#f44336" || color === "rgb(244, 67, 54)" || color === "red") {
            hayRojo = true;
            diasRojos.push(dia);
        }
    });

    if (hayRojo) {
        showConfirmModal(10, "WarningWorkerMD");
        setTimeout(() => {
            const confirmBtn = document.getElementById("modalConfirmWarningWorker");
            if (confirmBtn) {
                confirmBtn.onclick = function() {
                    $('#WarningWorkerMD').hide();
                    $('.custom-modal').hide();
                    procesarDiasSeleccionados();
                };
            }
        }, 100);
    } else {
        procesarDiasSeleccionados();
    }
});

function procesarDiasSeleccionados() {
    diasSeleccionados.forEach((dia, idx) => {
        let fechaFormateada = dia.split('T')[0];
        let partesFecha = fechaFormateada.split('-');
        fechaFormateada = `${partesFecha[0]}-${partesFecha[1]}-${partesFecha[2]}`;
        changeWorkerFestivity(
            fechaFormateada,
            lastId,
            {
                message: "¡Se ha dado o quitado la fiesta al trabajador!",
                status: "success",
                time: 4000
            }
        );
    });
    dayCellsSeleccionadas.forEach(cell => cell.style.filter = "");
    dayCellsSeleccionadas = [];
    diasSeleccionados = [];
}

function changeWorkerFestivity(fecha, id, toast) {
    fetch(`/api/calendari/fiestas/trabajador/${id}/?fecha=${fecha}`)
    .then(response => response.json())
    .then(data => {
        removeToasts(true);
        showToast(toast.message, toast.status, toast.time);
        $('.custom-modal').hide();
    })
    .catch(err => {
        showToast("Error al cambiar la festividad: " + err, "error", 5000);
    });
}