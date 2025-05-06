
let currentReservationId = null;  // Para guardar el id de la reserva que se quiere borrar
// Mostrar el modal de confirmación con la reserva seleccionada
function showConfirmModal(reservaId,idModal="myModal") {
    currentReservationId = reservaId;  // Guardamos el id de la reserva que vamos a borrar
    $('#'+idModal).show();  // Mostrar el modal
}

// Todo: Hacer bien el cerrar el modal(que mire el id del padre y cierre el que toca, no todos los modales)   
// Cerrar el modal
$('#modalClose, #modalCloseBtn').click(function() {
    $('.custom-modal').hide();  // Ocultar el modal
    currentReservationId = null;  // Limpiar el id de la reserva
});

// Prevenir que el modal se cierre cuando se hace clic dentro del contenido
$('.custom-modal-content').click(function(e) {
    e.stopPropagation();
});

// Cerrar el modal cuando se hace clic fuera del contenido
$('.custom-modal').click(function() {
    $('.custom-modal').hide();  // Ocultar el modal
    currentReservationId = null;  // Limpiar el id de la reserva
});

//! Acciones

// Función para confirmar la eliminación de una reserva
$('#modalConfirmDeleteResBtn').click(function() { 
    if (currentReservationId !== null) {
        // Hacer la solicitud AJAX para eliminar la reserva
        $.ajax({
            url: '/borrar_reserva/' + currentReservationId + '/',  // URL de tu vista para borrar
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,  // Añadir el token CSRF en el encabezado
            },
            success: function(response) {
                sessionStorage.setItem("toastMessage", "Reserva eliminada con éxito");
                sessionStorage.setItem("toastType", "success");
                location.reload();  // Recargar la página (o actualizar el listado)
            },
            error: function(xhr, status, error) {
                console.error('Error details:', xhr.responseText);
                sessionStorage.setItem("toastMessage", "Hubo un error al eliminar la reserva: " + error);
                sessionStorage.setItem("toastType", "error");
                location.reload(); // Recargar la página
            }
        });
    }
});

// Función para confirmar la eliminación de un trabajador
$('#modalConfirmDeleteWorkBtn').click(function() { 
    if (currentReservationId !== null) {
        showToast("Borrando trabajador...","info",999999999); // Mostrar un toast de información
        $.ajax({
            url: '/borrar_worker/' + currentReservationId + '/',
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            success: function(response) {
                sessionStorage.setItem("toastMessage", "Trabajador eliminado con éxito");
                sessionStorage.setItem("toastType", "success");
                location.reload(); // Recargar la página
            },
            error: function(xhr, status, error) {
                console.error('Error details:', xhr.responseText);  
                sessionStorage.setItem("toastMessage", "Hubo un error al eliminar al trabajador: " + error);
                sessionStorage.setItem("toastType", "error");
                location.reload(); // Recargar la página
            }
        });
    }
});
//Modal para confirmar la importación de trabajadores
$('#modalConfirmImportWork').click(function() { 
    if (currentReservationId !== null) {
        const formData = new FormData();
        formData.append('file', currentReservationId); // currentReservationId es el archivo que se va a importar
        showToast("Importando trabajadores...","info",999999999); // Mostrar un toast de información
        fetch('/importar-workers/', {
            method: 'POST',
            body: formData,
        })
        .then(res => res.json())
        .then(data => {
            sessionStorage.setItem("toastMessage", "Trabajador importados con éxito");
            sessionStorage.setItem("toastType", "success");
            location.reload(); // Recargar la página
        })
        .catch(err => {
            console.error('Error details:', err);  
            sessionStorage.setItem("toastMessage", "Hubo un error al importar los trabajadores: " + err);
            sessionStorage.setItem("toastType", "error");
            location.reload(); // Recargar la página
        });
    }
});
//Modal para confirmar la importación de trabajadores
$('#modalConfirmRecoverWork').click(function() { 
    if (currentReservationId !== null) {
        const formData = new FormData();
        formData.append('file', currentReservationId); // currentReservationId es el archivo que se va a importar
        showToast("Importando trabajadores...","info",999999999); // Mostrar un toast de información
        fetch('/restore_worker/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData,
        })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            if (data.error) {
                showToast(data.error,"error",5000); // Mostrar un toast de error
                $('.custom-modal').hide();
                return;
            }
            sessionStorage.setItem("toastMessage", "Ultimo trabajador eliminado restaurado con éxito");
            sessionStorage.setItem("toastType", "success");
            location.reload(); // Recargar la página
        })
        .catch(err => {
            console.error('Error details:', err);  
            sessionStorage.setItem("toastMessage", "Hubo un error al restaurar el trabajador: " + err);
            sessionStorage.setItem("toastType", "error");
            location.reload(); // Recargar la página
        });
    }
});