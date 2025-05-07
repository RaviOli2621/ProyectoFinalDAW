document.addEventListener('DOMContentLoaded', calcular);

    function calcular() {
        clearDropdownListeners();

        if (window.innerWidth <= 768) {

            document.querySelectorAll('.dropdown-toggle').forEach(function(btn) {
                let tapped = false;
                btn.addEventListener('click', function(e) {
                    const dropdown = btn.parentElement.querySelector('.dropdown-content');
                    if (!tapped) {
                        e.preventDefault();
                        // Cierra otros dropdowns
                        document.querySelectorAll('.dropdown-content').forEach(function(dc) {
                            if (dc !== dropdown) dc.style.display = 'none';
                        });
                        dropdown.style.display = 'block';
                        tapped = true;
                        // Espera el segundo tap solo durante 1 segundo
                        setTimeout(() => { tapped = false; }, 1000);
                    } else {
                        // Segundo tap: navega
                        if(btn.getAttribute('data-href') != null) window.location.href = btn.getAttribute('data-href');
                    }
                    e.stopPropagation();
                });
            });

            // Cierra el menú si se hace click fuera
            document.addEventListener('click', function() {
                document.querySelectorAll('.dropdown-content').forEach(function(dc) {
                    dc.style.display = 'none';
                });
            });

            // User icon dropdown en móvil
            document.querySelectorAll('.userIcon .contenedorFoto').forEach(function(foto) {
                foto.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const dropdown = foto.parentElement.querySelector('.dropdown-content');
                    // Cierra otros dropdowns
                    document.querySelectorAll('.dropdown-content').forEach(function(dc) {
                        if (dc !== dropdown) dc.style.display = 'none';
                    });
                    dropdown.style.display = (dropdown.style.display === 'block') ? 'none' : 'block';
                });
            });
        }else{
            document.querySelectorAll('.dropdown-toggle').forEach(function(btn) {
                let tapped = false;
                btn.addEventListener('click', function(e) {
                    if (window.innerWidth <= 768) {
                        const dropdown = btn.parentElement.querySelector('.dropdown-content');
                        if (!tapped) {
                            e.preventDefault();
                            // Cierra otros dropdowns
                            document.querySelectorAll('.dropdown-content').forEach(function(dc) {
                                if (dc !== dropdown) dc.style.display = 'none';
                            });
                            dropdown.style.display = 'block';
                            tapped = true;
                            setTimeout(() => { tapped = false; }, 1000);
                        } else {
                            // Segundo tap: navega
                            if(btn.getAttribute('data-href') != null) window.location.href = btn.getAttribute('data-href');
                        }
                        e.stopPropagation();
                    } else {
                        // Escritorio: navega normalmente
                        if(btn.getAttribute('data-href') != null) window.location.href = btn.getAttribute('data-href');
                    }
                });
            });
        }
        window.addEventListener('resize', function() {
                calcular(); 
        });
        function clearDropdownListeners() {
            // Clona los nodos para eliminar listeners previos
            document.querySelectorAll('.dropdown-toggle').forEach(btn => {
                btn.replaceWith(btn.cloneNode(true));
            });
            document.querySelectorAll('.userIcon .contenedorFoto').forEach(foto => {
                foto.replaceWith(foto.cloneNode(true));
            });
        }
}