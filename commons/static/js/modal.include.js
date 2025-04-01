
let currentReservationId = null;  // Para guardar el id de la reserva que se quiere borrar

// Mostrar el modal de confirmación con la reserva seleccionada
function showConfirmModal(reservaId) {
    currentReservationId = reservaId;  // Guardamos el id de la reserva que vamos a borrar
    $('#myModal').show();  // Mostrar el modal
}

// Cerrar el modal
$('#modalClose, #modalCloseBtn').click(function() {
    $('#myModal').hide();  // Ocultar el modal
    currentReservationId = null;  // Limpiar el id de la reserva
});

// Prevenir que el modal se cierre cuando se hace clic dentro del contenido
$('.custom-modal-content').click(function(e) {
    e.stopPropagation();
});

// Cerrar el modal cuando se hace clic fuera del contenido
$('.custom-modal').click(function() {
    $('#myModal').hide();  // Ocultar el modal
    currentReservationId = null;  // Limpiar el id de la reserva
});

// Función para confirmar la eliminación
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
                alert('Reserva eliminada con éxito');
                $('#myModal').hide();  // Ocultar el modal
                location.reload();  // Recargar la página (o actualizar el listado)
            },
            error: function(xhr, status, error) {
                alert('Hubo un error al eliminar la reserva: ' + error);
                console.error('Error details:', xhr.responseText);
            }
        });
    }
});
