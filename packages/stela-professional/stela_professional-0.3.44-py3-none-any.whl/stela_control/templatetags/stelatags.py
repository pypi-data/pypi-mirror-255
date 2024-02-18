from django import template
from django.utils import timezone
import bleach, pytz


register = template.Library()

def cash(val, precision=2):
    try:
        int_val = int(val)
    except ValueError:
        raise template.TemplateSyntaxError(
        f'Value must be an integer. {val} is not an integer')

    if int_val < 1000:
        return str(int_val)
    
    elif int_val < 1_000_000:
        return f'{ int_val/1000.0:.{precision}f}'.rstrip('0').rstrip('.') + 'k'
    else:
        return f'{int_val/1_000_000.0:.{precision}f}'.rstrip('0').rstrip('.') + 'M'

register.filter('cash', cash)

@register.simple_tag
def set(varname, value):
    return value

@register.filter
def br_only(value):
    allowed_tags = ['br']
    return bleach.clean(value, tags=allowed_tags, strip=True)

@register.filter
def convert_to_user_timezone():
    user_timezone = pytz.timezone()
    print(user_timezone)
    return timezone.localtime()

@register.filter(name='truncatewords_custom')
def truncatewords_custom(value, arg):
    try:
        arg = int(arg)
    except ValueError:  
        return value

    words = value.split()  

    if len(words) > arg:
        return ' '.join(words[:arg]) + '...'
    else:
        return value