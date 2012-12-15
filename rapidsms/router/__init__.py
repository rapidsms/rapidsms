from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

from rapidsms.router.api import receive, send, lookup_connections

__all__ = ['import_class', 'get_router', 'get_test_router']


def import_class(import_path):
    """
    Imports and returns the class described by import_path, where
    import_path is the full Python path to the class.
    """
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


def get_router():
    router = getattr(settings, 'RAPIDSMS_ROUTER',
                     'rapidsms.router.blocking.BlockingRouter')
    if isinstance(router, basestring):
        router = import_class(router)()
    return router


def get_test_router():
    return import_class(getattr(settings, 'TEST_RAPIDSMS_ROUTER',
                        'rapidsms.router.blocking.BlockingRouter'))
get_test_router.__test__ = False
