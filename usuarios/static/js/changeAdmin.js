function cambiarPriv(currentUserId,elemento){
    if (currentUserId !== null) {
    // Hacer la solicitud AJAX para eliminar la reserva
        $.ajax({
            url: '/userChangePriv/' + currentUserId + '/',  // URL de tu vista para borrar
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,  // Añadir el token CSRF en el encabezado
            },
            success: function(response) {
                alert('Accion ejecutada con éxito');
                location.reload();  // Recargar la página (o actualizar el listado)
            },
            error: function(xhr, status, error) {
                alert('Hubo un error al realizar la accion: ' + error);
                console.error('Error details:', xhr.responseText);
            }
        });
    }
}
