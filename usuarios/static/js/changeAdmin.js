function cambiarPriv(currentUserId,elemento){
    if (currentUserId !== null) {
    showToast('Cargando...', 'info', 3000);

        $.ajax({
            url: '/userChangePriv/' + currentUserId + '/',  
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,  
            },
            success: function(response) {
                showToast('Acción ejecutada con éxito', 'succes', 3000);
                location.reload();  
            },
            error: function(xhr, status, error) {
                showToast('Hubo un error al realizar la acción: ' + error, 'error', 5000);
                console.log('Error details:', xhr.responseText);
            }
        });
    }
}
// Codigo para cambiar el estado de un usuario a admin o no admin