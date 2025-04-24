let calendar = null;
let diaSeleccionado = ""; // Variable para almacenar el día numerico seleccionado
let currentAbortController = null;  // Variable para almacenar el controlador de la última solicitud
let dayCellG = null; // Variable para almacenar la celda del día seleccionado
let lastClickedDate = null; // Variable para almacenar la última fecha clicada
let lastClickTime = 0; // Variable para almacenar el tiempo del último clic
let isUserInitiatedRefresh = false; // Variable para controlar si la actualización es iniciada por el usuario
let canInteract = true;

// Función para obtener parámetros de URL
function getUrlParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

(() => {
    diaSeleccionado = "";
    const calendarEl = document.getElementById('calendar');

    if (!calendar) {
        // Comprobar si hay parámetros de año y mes en la URL
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
                // Only show loading toast if not a user-initiated refresh
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
                        // Reset the flag after events are loaded
                        isUserInitiatedRefresh = false;
                        canInteract = true; 
                        
                        // Si había una selección anterior, restaurarla visualmente
                        if (dayCellG && diaSeleccionado) {
                            try {
                                const fechaSeleccionada = diaSeleccionado.split('T')[0];
                                const celdas = document.querySelectorAll('.fc-daygrid-day');
                                for (let celda of celdas) {
                                    const dataDate = celda.getAttribute('data-date');
                                    if (dataDate === fechaSeleccionada) {
                                        celda.classList.add('calendario-dia-seleccionado');
                                        dayCellG = celda;
                                        break;
                                    }
                                }
                            } catch (e) {
                                console.error("Error al restaurar la selección:", e);
                            }
                        }
                    })
                    .catch(err => {
                        // Ignore AbortError as it's expected when requests are canceled
                        if (err.name !== 'AbortError') {
                            failureCallback(err);
                        }
                        // Reset the flag even if there's an error
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
                else if (info.dateStr) {
                    const selectedDate = new Date(info.dateStr);
                    const dayOfWeek = selectedDate.getDay(); // 0 = Sunday, 6 = Saturday

                    if (dayOfWeek === 0 || dayOfWeek === 6) {
                        showToast("No se pueden seleccionar días de fin de semana", "info", 5000);
                        return;
                    }
                }
                // Obtener el color de fondo del evento (si existe)
                const event = info.view.calendar.getEvents().find(e => e.startStr === info.dateStr);
                const backgroundColor = event ? event.backgroundColor : ""; // Color por defecto si no hay evento

                // Verificar si el día está completamente reservado
                if (backgroundColor === "red") {
                    showToast("Día completo", "error", 5000);
                    return;
                }

                // Comprobar si es un doble clic
                const currentTime = new Date().getTime();
                const isDoubleClick = (info.dateStr === lastClickedDate && currentTime - lastClickTime < 300);
                
                // Actualizar las variables de seguimiento
                lastClickedDate = info.dateStr;
                lastClickTime = currentTime;

                // Añadir un atributo data-date para facilitar la comparación
                const clickedDate = info.dateStr;
                const previousSelectedDate = diaSeleccionado ? diaSeleccionado.split('T')[0] : null;
                
                // Limpiar la selección anterior
                document.querySelectorAll('.calendario-dia-seleccionado').forEach(el => {
                    el.classList.remove('calendario-dia-seleccionado');
                    el.style.filter = "";
                });

                // Si se hace clic en el mismo día que ya estaba seleccionado, quitar la selección
                if (previousSelectedDate === clickedDate && !isDoubleClick) {
                    diaSeleccionado = "";
                    dayCellG = null;
                } else {
                    // Seleccionar el nuevo día
                    diaSeleccionado = clickedDate + "T00:00";
                    dayCellG = info.dayEl;
                    
                    // Marcar visualmente con una clase y filtro de brillo
                    dayCellG.classList.add('calendario-dia-seleccionado');
                    dayCellG.style.filter = "opacity(50%)";
                
                    // Si es un doble clic, mostrar el modal directamente
                    if (isDoubleClick) {
                        const fiesta = backgroundColor === "gray";
                        confirmCalendar(diaSeleccionado, fiesta, backgroundColor);
                    }
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
        // Limpiar cualquier toast existente antes de mostrar el modal
        removeToasts(true);
        
        // Primero mostrar el modal para que esté accesible en el DOM
        showConfirmModal(10,"HorasMD");
        
        // Ahora configurar el título y los botones
        setTimeout(() => {
            const modalTitle = document.querySelector('#HorasMD #modalConfirmHoras');
            if (!modalTitle) {
                console.error("No se encontró el botón de confirmación");
                return;
            }
            
            // Eliminar todos los event listeners previos
            modalTitle.onclick = null;
            
            if (fiesta) {
                modalTitle.textContent = "Quitar fiesta";
                modalTitle.classList.remove('custom-btn-primary');
                modalTitle.classList.add('custom-btn-danger');
                
                // Reemplazar con un nuevo event listener
                modalTitle.onclick = function() {
                    changeFest(dia, "DELETE");
                };
            } else {
                modalTitle.textContent = "Añadir fiesta";
                modalTitle.classList.remove('custom-btn-danger');
                modalTitle.classList.add('custom-btn-primary');
                
                // Reemplazar con un nuevo event listener
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
                        removeToasts(true);
                        showToast("Error al mostrar las horas - contenedor no encontrado", "error", 5000);
                    }
                })
                .catch(err => {
                    console.error("Error al cargar las horas:", err);
                    removeToasts(true);
                    showToast("Error al cargar las horas", "error", 5000);
                });
        }, 100); // Un pequeño retraso para asegurar que el modal está visible
    } else {
        removeToasts(true);
        showToast("No hay día seleccionado", "error", 5000);
    }
}

// Función para limpiar event listeners de un modal específico
function cleanupModalListeners(modalId) {
    // Buscar elementos con event listeners en el modal
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    // Limpiar posibles event listeners en botones y elementos del modal
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
    // Para todos los botones que cierran modales (X, botones de cancelar, etc.)
    document.querySelectorAll('.modal-close, .btn-cancel, .custom-modal-close').forEach(btn => {
        // Eliminar listeners previos clonando el elemento
        const newBtn = btn.cloneNode(true);
        if (btn.parentNode) {
            btn.parentNode.replaceChild(newBtn, btn);
        }
        
        // Añadir el nuevo listener
        newBtn.addEventListener('click', function() {
            // Limpiar todos los toasts cuando se cierra un modal
            removeToasts(true);
        });
    });
    
    // Para clicks fuera del modal (si se cierra así)
    document.querySelectorAll('.custom-modal, .modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            // Si el click es directamente en el fondo del modal (no en su contenido)
            if (e.target === modal) {
                removeToasts(true);
            }
        });
    });
}

// Añadir este evento cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Código existente para DOMContentLoaded...
    
    // Configurar manejadores para cerrar modales
    setupModalCloseHandlers();
    
    // También añadir un manejador para la tecla ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Si se presiona ESC, comprobar si hay algún modal abierto y limpiar toasts
            const modalVisible = document.querySelector('.custom-modal:visible, .modal:visible');
            if (modalVisible) {
                removeToasts(true);
            }
        }
    });
});

function changeFest(dia, metodo) {
    // Desactivar interacción mientras se procesa
    canInteract = false;
    
    fetch(`/api/calendari/fiestas/?fecha=${dia}`, {
        method: metodo,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
    })
    .then(response => {
        if (response.ok) {
            $('.custom-modal').hide();
            
            // Obtener el año y mes actuales del calendario
            const currentDate = calendar.getDate();
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth() + 1; // +1 porque getMonth() devuelve 0-11
            
            // Mostrar toast de éxito antes de recargar
            showToast("Cambio realizado con éxito. Actualizando...", "success", 2000);
            
            // Esperar un momento para que el usuario vea el mensaje
            setTimeout(() => {
                // Recargar la página manteniendo el mes actual
                window.location.href = `${window.location.pathname}?year=${year}&month=${month}`;
            }, 1000);
        } else {
            showToast("Error al modificar", "error", 5000);
            $('.custom-modal').hide();
            canInteract = true; // Reactivar interacción en caso de error
        }
    })
    .catch(err => {
        console.error("Error al modificar:", err);
        showToast("Error al modificar", "error", 5000);
        canInteract = true; // Reactivar interacción en caso de error
    });
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
        
        // if(hora.color !== 'red') {
        //     horaElement.addEventListener('click', () => {
        //         selectHour(hora.fecha);
        //     });
        // }
        
        hoursContainer.appendChild(horaElement);
    });
    return hoursContainer;
}

function confirmCalendar(dia, fiesta, backgroundColor){ 
    const datePart = dia.split('T')[0];
    showHourModal(datePart, fiesta, backgroundColor);
    
    // Limpiar la selección después de confirmar
    diaSeleccionado = "";
    document.querySelectorAll('.calendario-dia-seleccionado').forEach(el => {
        el.classList.remove('calendario-dia-seleccionado');
        el.style.filter = "";
    });
    dayCellG = null;
}

function warningModal(dia){
    // Verificar primero si se puede interactuar
    if (!canInteract) {
        removeToasts(true);
        showToast("Espera mientras se actualiza el calendario...", "info", 3000);
        return;
    }
    
    // Limpiar los toasts
    removeToasts(true);
    
    // Mostrar el modal de advertencia
    showConfirmModal(10,"WarningMD");
    
    // Configurar el botón de confirmación después de que el modal esté visible
    setTimeout(() => {
        const confirmBtn = document.getElementById("modalConfirmWarning");
        if (confirmBtn) {
            // Eliminar event listeners previos
            confirmBtn.onclick = null;
            
            // Añadir el nuevo event listener
            confirmBtn.onclick = function() {
                // Cerrar el modal primero
                $('#WarningMD').hide();
                $('.custom-modal').hide();
                
                // Luego ejecutar la acción
                changeFest(dia, "PUT");
            };
        }
    }, 100);
}

// Agregar un estilo CSS al encabezado del documento para la clase personalizada
(function() {
    const style = document.createElement('style');
    style.textContent = `
        .calendario-dia-seleccionado {
            filter: opacity(50%) !important;
            outline: 2px solid #5c7cfa !important;
            position: relative;
            z-index: 1;
        }
    `;
    document.head.appendChild(style);
})();

// Agregar evento para actualizar la URL cuando cambie el mes
document.addEventListener('DOMContentLoaded', function() {
    if (calendar) {
        calendar.on('datesSet', function(info) {
            // No modificar la URL durante la carga inicial
            if (calendar._isFirstRender) return;
            
            const currentDate = calendar.getDate();
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth() + 1;
            
            // Actualizar la URL sin recargar la página
            const newUrl = `${window.location.pathname}?year=${year}&month=${month}`;
            window.history.replaceState({}, '', newUrl);
        });
    }
});

