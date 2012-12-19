from django import template

register = template.Library()

@register.filter
def display_list(list_):
    '''display a list'''
    return ','.join([unicode(i) for i in list_])
