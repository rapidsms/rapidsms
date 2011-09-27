from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def get_router():
    """
    Imports and returns the router class described by the RAPIDSMS_ROUTER
    setting, where RAPIDSMS_ROUTER is the full Python path to the class.
    """
    import_path = getattr(settings, 'RAPIDSMS_ROUTER',
                          'rapidsms.router.legacy.LegacyRouter')
    try:
        dot = import_path.rindex('.')
    except ValueError:
        raise ImproperlyConfigured("%s isn't a Python path." % import_path)
    module, classname = import_path[:dot], import_path[dot + 1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                   (module, e))
    try:
        return getattr(mod, classname)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                   'class.' % (module, classname))

# TODO: remove this global singleton
# a single instance of the router singleton is available globally, like
# the db connection. it shouldn't be necessary to muck with this very
# often (since most interaction with the Router happens within an App or
# Backend, which have their own .router property), but when it is, it
# should be done via this process global
router = get_router()()
