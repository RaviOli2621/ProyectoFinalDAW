import os

def get_filename(image_field):
    """Devuelve solo el nombre del archivo de una imagen."""
    if image_field and hasattr(image_field, 'name'):
        return os.path.basename(image_field.name)  # Extrae solo el nombre del archivo
    return ""  # Si no hay imagen, devuelve una cadena vacía