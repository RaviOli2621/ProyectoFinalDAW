document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.search-bar');
    const input = form.querySelector('input[name="q"]');
    idReserva = ""
    reservaEl = document.getElementsByClassName('reserva')[0];
    container = document.getElementById('nothingDesc');
    title = document.getElementsByClassName('Title')[0].children[2];
    reservaEl.style.visibility = 'hidden';
    checkbox = container.children[4].children[0].children[1]
    checkbox.addEventListener('change', function(){queCambiado="pagado"; consultar();});
    queCambiado = "";

    function consultar() {
        showToast("Cambiando pagado", "info", 50000);
        checkbox.disabled = true;
        container.children[5].children[0].children[1].disabled = true;
        fetch(`/worker_ver_masaje/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ reserva_id: idReserva, pagado: checkbox.checked, hecho: container.children[5].children[0].children[1].checked })
        })
        .then(response => {
            if (!response.ok) throw new Error('Error al actualizar los datos');
            return response.json();
        })
        .then(data => {
            showToast("Datos actualizados", "succes", 5000);
            checkbox.disabled = false;
            container.children[5].children[0].children[1].disabled = false;
        })
        .catch(error => {
            showToast("Error al actualizar los datos" + error, "error", 5000);
            if(queCambiado == "pagado") checkbox.checked = !checkbox.checked;
            checkbox.disabled = false;
            if(queCambiado == "hecho") container.children[5].children[0].children[1].checked = !container.children[5].children[0].children[1].checked;
            container.children[5].children[0].children[1].disabled = false;
        });
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const id = input.value.trim();
        if (!id) {
            showToast("Introduzca un id de reserva", "error", 5000);
            return;
        }
        showToast("Buscando", "info", 50000);

        fetch(`/get_reserva_by_id/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ reserva_id: id })
        })
        .then(response => {
            if (!response.ok) throw new Error('No se encontró la reserva');
            return response.json();
        })
        .then(data => {
            document.getElementsByClassName('Title')[0].children[1].innerHTML = "";
            document.getElementsByClassName('Title')[0].children[4].innerHTML = "";
            container.children[0].innerHTML = formatearFecha(data.fecha);        
            container.children[1].innerHTML = formatearHora(data.fecha);        
            container.children[2].innerHTML = formatearDuracion(data.duracion);        
            container.children[3].innerHTML = Number(data.masajePrecio).toFixed(1).replace('.', ',') + '€';
            checkbox.checked = data.pagado;
            checkbox.disabled = false;
            container.children[5].innerHTML = '<label><p>Hecha:</p><input type="checkbox" id="hecho"></label>';
            container.children[5].children[0].children[1].checked = data.hecho;
            title.innerHTML = data.titulo
            reservaEl.style.backgroundImage = `url('/static/${data.foto.split("/static/")[1]}')`;
            reservaEl.style.visibility = 'visible';
            showToast("Reserva encontrada", "succes", 5000);
            idReserva = data.id

            container.children[5].children[0].children[1].addEventListener('change', function(){queCambiado="hecho"; consultar();});
        })
        .catch(error => {
            showToast("Reserva no encontrada o error en la búsqueda." + error, "error", 5000);
            reservaEl.style.visibility = 'hidden';
        });
    });

});
function formatearFecha(fechaIso) {
    const fechaObj = new Date(fechaIso);
    const dia = String(fechaObj.getDate()).padStart(2, '0');
    const mes = String(fechaObj.getMonth() + 1).padStart(2, '0');
    const anio = fechaObj.getFullYear();
    return `${dia}-${mes}-${anio}`;
}
function formatearHora(fechaIso) {
    const fechaObj = new Date(fechaIso);
    const horas = String(fechaObj.getHours()).padStart(2, '0');
    const minutos = String(fechaObj.getMinutes()).padStart(2, '0');
    return `${horas}:${minutos}`;
}
function formatearDuracion(segundos) {
    const horas = Math.floor(segundos / 3600);
    const minutos = Math.round((segundos % 3600) / 60);
    if (minutos === 0) {
        return `${horas}.0h`;
    }
    const minutosDecimal = Math.floor(minutos / 6);
    return `${horas}.${minutosDecimal}h`;
}