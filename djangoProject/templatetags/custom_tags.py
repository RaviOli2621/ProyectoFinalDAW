from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def render_boton(src, alt, action):
    context = {
        'src': src,
        'alt': alt,
        'action': action,
    }
    return render_to_string('commons/includes/imgBoton.include.html', context)