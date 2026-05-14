from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """Replace commas and extra spaces in text"""
    if value:
        # Replace commas with spaces
        value = value.replace(',', ' ')
        # Replace multiple spaces with single space
        import re
        value = re.sub(r'\s+', ' ', value)
        # Remove extra periods
        value = value.replace('..', '.')
    return value