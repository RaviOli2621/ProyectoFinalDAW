document.getElementById('id_foto').addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('fotoUser').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});
document.querySelector('.current-photo').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        document.getElementById('id_foto').click();
    }
});