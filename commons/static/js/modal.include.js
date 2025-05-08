
let currentReservationId = null;  // Variable usada para lo que necesite el modal en concreto
// Mostrar el modal de confirmación con la reserva seleccionada
function showConfirmModal(reservaId,idModal="myModal") {
    currentReservationId = reservaId;  
    $('#'+idModal).show();  
}

$('#modalClose, #modalCloseBtn').click(function() {
    $('.custom-modal').hide();  
    currentReservationId = null;  
});

// Prevenir que el modal se cierre cuando se hace clic dentro del contenido
$('.custom-modal-content').click(function(e) {
    e.stopPropagation();
});

// Cerrar el modal cuando se hace clic fuera del contenido
$('.custom-modal').click(function() {
    $('.custom-modal').hide();  
    currentReservationId = null;  
});

//! Acciones

// Función para confirmar la eliminación de una reserva
$('#modalConfirmDeleteResBtn').click(function() { 
    if (currentReservationId !== null) {
        $.ajax({
            url: '/borrar_reserva/' + currentReservationId + '/',  
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken, 
            },
            success: function(response) {
                sessionStorage.setItem("toastMessage", "Reserva eliminada con éxito");
                sessionStorage.setItem("toastType", "success");
                location.reload();  
            },
            error: function(xhr, status, error) {
                console.error('Error details:', xhr.responseText);
                sessionStorage.setItem("toastMessage", "Hubo un error al eliminar la reserva: " + error);
                sessionStorage.setItem("toastType", "error");
                location.reload(); 
            }
        });
    }
});

// Función para confirmar la eliminación de un trabajador
$('#modalConfirmDeleteWorkBtn').click(function() { 
    if (currentReservationId !== null) {
        showToast("Borrando trabajador...","info",999999999); 
        $.ajax({
            url: '/borrar_worker/' + currentReservationId + '/',
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            success: function(response) {
                sessionStorage.setItem("toastMessage", "Trabajador eliminado con éxito");
                sessionStorage.setItem("toastType", "success");
                location.reload(); 
            },
            error: function(xhr, status, error) {
                console.error('Error details:', xhr.responseText);  
                sessionStorage.setItem("toastMessage", "Hubo un error al eliminar al trabajador: " + error);
                sessionStorage.setItem("toastType", "error");
                location.reload(); 
            }
        });
    }
});
//Modal para confirmar la importación de trabajadores
$('#modalConfirmImportWork').click(function() { 
    if (currentReservationId !== null) {
        const formData = new FormData();
        formData.append('file', currentReservationId); 
        showToast("Importando trabajadores...","info",999999999); 
        fetch('/importar-workers/', {
            method: 'POST',
            body: formData,
        })
        .then(res => res.json())
        .then(data => {
            sessionStorage.setItem("toastMessage", "Trabajador importados con éxito");
            sessionStorage.setItem("toastType", "success");
            location.reload(); 
        })
        .catch(err => {
            console.error('Error details:', err);  
            sessionStorage.setItem("toastMessage", "Hubo un error al importar los trabajadores: " + err);
            sessionStorage.setItem("toastType", "error");
            location.reload(); 
        });
    }
});
$('#modalConfirmRecoverWork').click(function() { 
    if (currentReservationId !== null) {
        const formData = new FormData();
        formData.append('file', currentReservationId); 
        showToast("Importando trabajadores...","info",999999999); 
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
                showToast(data.error,"error",5000); 
                $('.custom-modal').hide();
                return;
            }
            sessionStorage.setItem("toastMessage", "Ultimo trabajador eliminado restaurado con éxito");
            sessionStorage.setItem("toastType", "success");
            location.reload(); 
        })
        .catch(err => {
            console.error('Error details:', err);  
            sessionStorage.setItem("toastMessage", "Hubo un error al restaurar el trabajador: " + err);
            sessionStorage.setItem("toastType", "error");
            location.reload(); 
        });
    }
});