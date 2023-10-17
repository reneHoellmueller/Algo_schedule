from django import template

register = template.Library()


@register.filter(name='to')
def to(value, arg):
    """Konvertiert den Wert in den Typ, der durch arg spezifiziert wird."""
    converters = {
        'int': int,
        'str': str,
        'float': float
    }
    if arg in converters:
        return converters[arg](value)
    else:
        return value  # oder werfen Sie einen passenden Fehler


@register.filter(name='add')
def add(value, arg):
    """Addiert arg zu value."""
    try:
        return value + int(arg)
    except ValueError:
        return value  # oder werfen Sie einen passenden Fehler


@register.filter
def _enumerate(sequence):
    """
    Enumeriert eine Sequenz, indem sie ein (index, element)-Tupel für jedes Element in der Liste zurückgibt.
    """
    return enumerate(sequence)
