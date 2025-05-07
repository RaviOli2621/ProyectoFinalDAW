function cambiarPriv(currentUserId,elemento){
    if (currentUserId !== null) {
    // Hacer la solicitud AJAX para eliminar la reserva
    showToast('Cargando...', 'info', 3000);

        $.ajax({
            url: '/userChangePriv/' + currentUserId + '/',  // URL de tu vista para borrar
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,  // Añadir el token CSRF en el encabezado
            },
            success: function(response) {
                showToast('Acción ejecutada con éxito', 'succes', 3000);
                location.reload();  // Recargar la página (o actualizar el listado)
            },
            error: function(xhr, status, error) {
                showToast('Hubo un error al realizar la acción: ' + error, 'error', 5000);
                console.log('Error details:', xhr.responseText);
            }
        });
    }
}
