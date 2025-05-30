document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.search-bar');
    const input = form.querySelector('input[name="q"]');
    const reservasList = document.getElementById('contentList');
    const reservas = reservasList ? reservasList.getElementsByClassName('reserva') : [];

    // --- Filtrado solo por ID de reserva (coincidencia exacta) ---
    input.addEventListener('input', function () {
        const filtro = input.value.trim().toLowerCase();
        let algunaVisible = false;
        Array.from(reservas).forEach(function (reserva) {
            const idDiv = reserva.querySelector('[id^="reserva-id-"]');
            let reservaId = '';
            if (idDiv) {
                reservaId = idDiv.id.replace('reserva-id-', '').toLowerCase();
            }
            if (filtro === '' || reservaId === filtro) {
                reserva.style.display = '';
                algunaVisible = true;
            } else {
                reserva.style.display = 'none';
            }
        });
        // Mensaje si no hay resultados
        const emptyMsg = document.getElementById('no-results-msg');
        if (!algunaVisible) {
            if (!emptyMsg) {
                const p = document.createElement('p');
                p.id = 'no-results-msg';
                p.textContent = 'No hay reservas que coincidan con la búsqueda.';
                reservasList.appendChild(p);
            }
        } else if (emptyMsg) {
            emptyMsg.remove();
        }
    });

    // --- Cambiar pagado y hecho ---
    Array.from(reservas).forEach(function (reserva) {
        const idDiv = reserva.querySelector('[id^="reserva-id-"]');
        if (!idDiv) return;
        const reservaId = idDiv.id.replace('reserva-id-', '');

        // Checkbox pagado y hecho
        const pagadoCheckbox = reserva.querySelector(`#reserva-pagado-${reservaId}`);
        const hechoCheckbox = reserva.querySelector(`#reserva-hecho-${reservaId}`);

        // Habilitar los checkboxes para edición
        if (pagadoCheckbox) pagadoCheckbox.disabled = false;
        if (hechoCheckbox) hechoCheckbox.disabled = false;

        // Evento para cambiar pagado
        if (pagadoCheckbox) {
            pagadoCheckbox.addEventListener('change', function () {
                actualizarReserva(reservaId, pagadoCheckbox.checked, hechoCheckbox ? hechoCheckbox.checked : false, pagadoCheckbox, hechoCheckbox);
            });
        }
        // Evento para cambiar hecho
        if (hechoCheckbox) {
            hechoCheckbox.addEventListener('change', function () {
                actualizarReserva(reservaId, pagadoCheckbox ? pagadoCheckbox.checked : false, hechoCheckbox.checked, pagadoCheckbox, hechoCheckbox);
            });
        }
    });

    function actualizarReserva(id, pagado, hecho, pagadoCheckbox, hechoCheckbox) {
        showToast("Aplicando cambios...", "info", 5000); 
        if (pagadoCheckbox) pagadoCheckbox.disabled = true;
        if (hechoCheckbox) hechoCheckbox.disabled = true;
        fetch(`/worker_ver_masaje/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ reserva_id: id, pagado: pagado, hecho: hecho })
        })
        .then(response => {
            if (!response.ok) throw new Error('Error al actualizar los datos');
            return response.json();
        })
        .then(data => {
            if (pagadoCheckbox) pagadoCheckbox.disabled = false;
            if (hechoCheckbox) hechoCheckbox.disabled = false;
            showToast("Datos actualizados", "success", 3000);
        })
        .catch(error => {
            showToast("Error al actualizar los datos: " + error, "error", 5000);
            if (pagadoCheckbox) pagadoCheckbox.checked = !pagadoCheckbox.checked;
            if (hechoCheckbox) hechoCheckbox.checked = !hechoCheckbox.checked;
            if (pagadoCheckbox) pagadoCheckbox.disabled = false;
            if (hechoCheckbox) hechoCheckbox.disabled = false;
        });
    }

    // Evitar submit del formulario
    form.addEventListener('submit', function (e) {
        e.preventDefault();
    });
});

// Utilidad para CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

