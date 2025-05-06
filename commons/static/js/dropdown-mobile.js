document.addEventListener('DOMContentLoaded', function() {
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
                    window.location.href = btn.getAttribute('data-href');
                }
                e.stopPropagation();
            } else {
                // Escritorio: navega normalmente
                window.location.href = btn.getAttribute('data-href');
            }
        });
    });

    // Cierra el menú si se hace click fuera
    document.addEventListener('click', function() {
        document.querySelectorAll('.dropdown-content').forEach(function(dc) {
            dc.style.display = 'none';
        });
    });

    // User icon dropdown en móvil
    if (window.innerWidth <= 768) {
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
    }
});