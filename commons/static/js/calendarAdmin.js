let calendar = null;
let diasSeleccionados = [];
let dayCellsSeleccionadas = [];
let currentAbortController = null;  // Variable para almacenar el controlador de la última solicitud
let lastClickedDate = null; // Variable para almacenar la última fecha clicada
let lastClickTime = 0; // Variable para almacenar el tiempo del último clic
let isUserInitiatedRefresh = false; // Variable para controlar si la actualización es iniciada por el usuario
let canInteract = true;

function getUrlParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

(() => {
    diasSeleccionados = [];
    const calendarEl = document.getElementById('calendar');

    if (!calendar) {
        const urlYear = getUrlParam('year');
        const urlMonth = getUrlParam('month');
        
        let initialDate = null;
        if (urlYear && urlMonth) {
            initialDate = `${urlYear}-${urlMonth.padStart(2, '0')}-01`;
        }

        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'es',
            height: 'auto',
            initialDate: initialDate,

            events: function(fetchInfo, successCallback, failureCallback) {
                const middleDate = new Date((fetchInfo.start.getTime() + fetchInfo.end.getTime()) / 2);
                const year = middleDate.getFullYear();
                const month = middleDate.getMonth() + 1;
                if (!isUserInitiatedRefresh) {
                    showToast("Cargando dias del mes...", "info", 99999);
                }
                
                if (currentAbortController) {
                    currentAbortController.abort();
                }
                const abortController = new AbortController();
                currentAbortController = abortController;

                fetch(`/api/calendario/?year=${year}&month=${month}`, { signal: abortController.signal })
                    .then(response => response.json())
                    .then(data => {
                        removeToasts(true);
                        successCallback(data);
                        isUserInitiatedRefresh = false;
                        canInteract = true; 
                        
                        // Si había una selección anterior, restaurarla visualmente
                        if (dayCellsSeleccionadas.length > 0 && diasSeleccionados.length > 0) {
                            try {
                                const celdas = document.querySelectorAll('.fc-daygrid-day');
                                for (let celda of celdas) {
                                    const dataDate = celda.getAttribute('data-date');
                                    if (diasSeleccionados.includes(dataDate)) {
                                        celda.classList.add('calendario-dia-seleccionado');
                                    }
                                }
                            } catch (e) {
                                console.error("Error al restaurar la selección:", e);
                            }
                        }
                    })
                    .catch(err => {
                        if (err.name !== 'AbortError') {
                            failureCallback(err);
                        }
                        isUserInitiatedRefresh = false;
                    });                
            },
            dateClick: function(info) {
                if (!canInteract) {
                    showToast("Espera mientras se cargan los datos", "info", 3000);
                    return;
                }
                const today = new Date().toISOString().split('T')[0];
                if (info.dateStr <= today) {
                    showToast("No se pueden modificar días pasados o el día de hoy", "info", 5000);
                    return;
                }
                const selectedDate = new Date(info.dateStr);
                const dayOfWeek = selectedDate.getDay();
                if (dayOfWeek === 0 || dayOfWeek === 6) {
                    showToast("No se pueden seleccionar días de fin de semana", "info", 5000);
                    return;
                }
                const event = info.view.calendar.getEvents().find(e => e.startStr === info.dateStr);
                const backgroundColor = event ? event.backgroundColor : "";
                if (backgroundColor === "red") {
                    showToast("Día completo", "error", 5000);
                    return;
                }

                // Multi-selección: alternar
                let fechaSeleccionada = info.dateStr + "T00:00";
                let idx = diasSeleccionados.indexOf(fechaSeleccionada);
                if (idx !== -1) {
                    diasSeleccionados.splice(idx, 1);
                    info.dayEl.classList.remove('calendario-dia-seleccionado');
                    info.dayEl.style.filter = "";
                    dayCellsSeleccionadas = dayCellsSeleccionadas.filter(cell => cell !== info.dayEl);
                } else {
                    diasSeleccionados.push(fechaSeleccionada);
                    info.dayEl.classList.add('calendario-dia-seleccionado');
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
})();

function showHourModal(dia, fiesta, backgroundColor) {
    // Verificar primero si se puede interactuar
    if (!canInteract) {
        removeToasts(true);
        showToast("Espera mientras se actualiza el calendario...", "info", 3000);
        return;
    }
    
    if(dia){
        removeToasts(true);
        
        showConfirmModal(10,"HorasMD");
        
        setTimeout(() => {
            const modalTitle = document.querySelector('#HorasMD #modalConfirmHoras');
            if (!modalTitle) {
                console.error("No se encontró el botón de confirmación");
                return;
            }
            
            modalTitle.onclick = null;
            
            if (fiesta) {
                modalTitle.textContent = "Quitar fiesta";
                modalTitle.classList.remove('custom-btn-primary');
                modalTitle.classList.add('custom-btn-danger');
                
                modalTitle.onclick = function() {
                    changeFest(dia, "DELETE");
                };
            } else {
                modalTitle.textContent = "Añadir fiesta";
                modalTitle.classList.remove('custom-btn-danger');
                modalTitle.classList.add('custom-btn-primary');
                
                if(backgroundColor == "green") {
                    modalTitle.onclick = function() {
                        changeFest(dia, "PUT");
                    };
                } else {
                    modalTitle.onclick = function() {
                        warningModal(dia);
                    };
                }
            }
            
            // Cargar las horas
            fetch(`/api/horas/?fecha=${dia}`)
                .then(response => response.json())
                .then(data => {                    
                    let modalBody = document.querySelector('#HorasMD .custom-modal-body');
                    if(!modalBody) modalBody = document.querySelector('#HorasMD .modal-body');
                    if(!modalBody) modalBody = document.getElementById('HorasMD').querySelector('div');
                    
                    if(modalBody) {
                        modalBody.innerHTML = "";
                        
                        const hoursContainer = createHours(data);
                        modalBody.appendChild(hoursContainer);
                    } else {
                        console.error("Modal container not found - HorasMD", document.getElementById('HorasMD'));
                        removeToasts(true);
                        showToast("Error al mostrar las horas - contenedor no encontrado", "error", 5000);
                    }
                })
                .catch(err => {
                    console.error("Error al cargar las horas:", err);
                    removeToasts(true);
                    showToast("Error al cargar las horas", "error", 5000);
                });
        }, 100); 
    } else {
        removeToasts(true);
        showToast("No hay día seleccionado", "error", 5000);
    }
}

// Función para limpiar event listeners de un modal específico
function cleanupModalListeners(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    const elements = modal.querySelectorAll('button, .modal-close, .btn-cancel, .custom-modal-close');
    elements.forEach(el => {
        const newEl = el.cloneNode(true);
        if (el.parentNode) {
            el.parentNode.replaceChild(newEl, el);
        }
    });
}

// También debemos limpiar los toasts cuando se cierra el modal
function setupModalCloseHandlers() {
    document.querySelectorAll('.modal-close, .btn-cancel, .custom-modal-close').forEach(btn => {
        const newBtn = btn.cloneNode(true);
        if (btn.parentNode) {
            btn.parentNode.replaceChild(newBtn, btn);
        }
        
        newBtn.addEventListener('click', function() {
            removeToasts(true);
        });
    });
    
    document.querySelectorAll('.custom-modal, .modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                removeToasts(true);
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    
    setupModalCloseHandlers();
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modalVisible = document.querySelector('.custom-modal:visible, .modal:visible');
            if (modalVisible) {
                removeToasts(true);
            }
        }
    });
});

function changeFest(dia, metodo) {
    canInteract = false;
    let fechaFormateada = dia.split('T')[0];
    let partesFecha = fechaFormateada.split('-');
    fechaFormateada = `${partesFecha[0]}-${partesFecha[1]}-${partesFecha[2]}`;
    fetch(`/api/calendari/fiestas/?fecha=${fechaFormateada}`, {
        method: metodo,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
    })
    .then(response => {
        if (response.ok) {
            $('.custom-modal').hide();
            
            const currentDate = calendar.getDate();
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth() + 1; // +1 porque getMonth() devuelve 0-11
            
            showToast("Cambio realizado con éxito. Actualizando...", "success", 2000);
            
            setTimeout(() => {
                window.location.href = `${window.location.pathname}?year=${year}&month=${month}`;
            }, 1000);
        } else {
            showToast("Error al modificar", "error", 5000);
            $('.custom-modal').hide();
            canInteract = true; 
        }
    })
    .catch(err => {
        console.error("Error al modificar:", err);
        showToast("Error al modificar", "error", 5000);
        canInteract = true; 
    });
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
        
        hoursContainer.appendChild(horaElement);
    });
    return hoursContainer;
}

function confirmCalendar(dia, fiesta, backgroundColor){ 
    const datePart = dia.split('T')[0];
    showHourModal(datePart, fiesta, backgroundColor);
    
    diasSeleccionados = [];
    document.querySelectorAll('.calendario-dia-seleccionado').forEach(el => {
        el.classList.remove('calendario-dia-seleccionado');
        el.style.filter = "";
    });
    dayCellsSeleccionadas = [];
}

function warningModal(dia){
    if (!canInteract) {
        removeToasts(true);
        showToast("Espera mientras se actualiza el calendario...", "info", 3000);
        return;
    }
    
    removeToasts(true);
    
    showConfirmModal(10,"WarningMD");
    
    setTimeout(() => {
        const confirmBtn = document.getElementById("modalConfirmWarning");
        if (confirmBtn) {
            confirmBtn.onclick = null;
            
            confirmBtn.onclick = function() {
                $('#WarningMD').hide();
                $('.custom-modal').hide();
                
                changeFest(dia, "PUT");
            };
        }
    }, 100);
}

(function() {
    const style = document.createElement('style');
    style.textContent = `
        .calendario-dia-seleccionado {
            filter: opacity(50%) !important;
            position: relative;
            z-index: 1;
        }
    `;
    document.head.appendChild(style);
})();

document.addEventListener('DOMContentLoaded', function() {
    if (calendar) {
        calendar.on('datesSet', function(info) {
            if (calendar._isFirstRender) return;
            
            const currentDate = calendar.getDate();
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth() + 1;
            
            const newUrl = `${window.location.pathname}?year=${year}&month=${month}`;
            window.history.replaceState({}, '', newUrl);
        });
    }
});

document.getElementById('confirmarDiasSeleccionadosBtn').onclick = function() {
    if (diasSeleccionados.length === 0) {
        showToast("Selecciona al menos un día válido", "error", 4000);
        return;
    }

    for (let i = 0; i < diasSeleccionados.length; i++) {
        const dia = diasSeleccionados[i];
        const fechaSinHora = dia.split('T')[0];
        const celda = Array.from(document.querySelectorAll('.fc-daygrid-day')).find(
            cell => cell.getAttribute('data-date') === fechaSinHora
        );
        let metodo = "PUT"; 

        let backgroundColor = "";
        if (celda) {
            const event = calendar.getEvents().find(e => e.startStr.startsWith(fechaSinHora));
            backgroundColor = event ? event.backgroundColor : "";
        }

        let color = backgroundColor.toLowerCase();
        if (color === "#ff9800" || color === "rgb(255, 152, 0)" || color === "orange") {
            warningModal(dia);
            return;
        }
        if (color === "#f44336" || color === "rgb(244, 67, 54)" || color === "red") {
            warningModal(dia);
            return;
        }
        if (color === "#2196f3" || color === "rgb(33, 150, 243)" || color === "blue") {
            metodo = "DELETE"; 
        }

        changeFest(dia, metodo);
    }

    dayCellsSeleccionadas.forEach(cell => {
        cell.classList.remove('calendario-dia-seleccionado');
        cell.style.filter = "";
    });
    dayCellsSeleccionadas = [];
    diasSeleccionados = [];
};

