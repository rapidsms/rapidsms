"""A set of request processors that return dictionaries to be merged into a
template context. Each function takes the request object as its only parameter
and returns a dictionary to add to the context.
"""
from django.conf import settings
def layout(request):
    """
    a context processor that changes the base css of the layout.html in RapidSMS. This is useful in case you want to
    have a custom skin for RapidSMS.
    """
    return {
        "BASE_CSS":settings.BASE_CSS
    }

