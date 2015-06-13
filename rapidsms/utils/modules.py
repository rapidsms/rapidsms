#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import os
import sys
import inspect

from django.utils.importlib import import_module


__all__ = ('import_class', 'import_module', 'try_import', 'find_python_files',
           'get_classes', 'get_class', 'get_package_path')


def import_class(import_path, base_class=None):
    """
    Imports and returns the class described by import_path, where
    import_path is the full Python path to the class.
    """
    try:
        module, class_name = import_path.rsplit('.', 1)
    except ValueError:
        raise ImportError("%s isn't a Python path." % import_path)
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImportError('Error importing module %s: "%s"' %
                          (module, e))
    try:
        class_ = getattr(mod, class_name)
    except AttributeError:
        raise ImportError('Module "%s" does not define a "%s" '
                          'class.' % (module, class_name))
    if not inspect.isclass(class_):
        raise ImportError('%s is not a class.' % import_path)
    if base_class and not issubclass(class_, base_class):
        msg = "%s is not a subclass of %s" % (class_name, base_class.__name__)
        raise ImportError(msg)
    return class_


def try_import(module_name):
    """
    Import and return *module_name*.

    >>> try_import("csv") # doctest: +ELLIPSIS
    <module 'csv' from '...'>

    Unlike the standard try/except approach to optional imports, inspect
    the stack to avoid catching ImportErrors raised from **within** the
    module. Only return None if *module_name* itself cannot be imported.

    >>> try_import("spam.spam.spam") is None
    True
    """

    try:
        __import__(module_name)
        return sys.modules[module_name]

    except ImportError:

        # extract a backtrace, so we can find out where the exception
        # was raised from. if there is a NEXT frame, it means that the
        # import statement succeeded, but an ImportError was raised from
        # *within* the imported module. we must allow this error to
        # propagate, to avoid silently masking it.
        traceback = sys.exc_info()[2]
        if traceback.tb_next:
            raise

        # else, the exception was raised from this scope. *module_name*
        # couldn't be imported, which is fine, since allowing that is
        # the purpose of this function.
        return None


def find_python_files(path):
    """
    Return a list of the Python files (*.py) in a directory. Note that
    the existance of a Python source file does not guarantee that it is
    a valid module, because the directory (or any number of its parents)
    may not contain an __init__.py, rendering it a non-module.

    For example, to list the Python files in the 'encodings' package,
    (which is always available, as part of the stdlib):

    >>> import encodings
    ... monkeys

    >>> p = encodings.__path__[0]
    >>> find_python_files(p) # doctest: +ELLIPSIS
    ['aliases', 'ascii', 'base64_codec', 'big5', ...]

    This seems a bit of an oversimplification, given that Python modules
    can live inside eggs and zips and the such, but if it's good enough
    for django.core.management.find_commands, it's good enough for me.

    Return an empty list if the directory doesn't exist, couldn't be
    iterated, or contains no relevant files.

    >>> find_python_files("doesnt-exist")
    []
    """

    try:
        return sorted([

            # trim the extension
            file[:-3]

            # iterate all files in the path
            # (doesn't include . and .. links)
            for file in os.listdir(path)

            # ignore __magic__ files and those
            # not ending with the .py suffix
            if not file.startswith(('_', '.'))
            and file.endswith('.py')])

    except OSError:
        return []


def get_classes(module, superclass=None):
    """
    Return a list of new-style classes defined in *module*, excluding
    _private and __magic__ names, and optionally filtering only those
    inheriting from *superclass*. Note that both arguments are actual
    modules, not names.

    This method only returns classes that were defined in *module*.
    Those imported from elsewhere are ignored.
    """

    objects = [
        getattr(module, name)
        for name in dir(module)
        if not name.startswith("_")]

    # filter out everything that isn't a new-style
    # class, or wasn't defined in *module* (ie, it
    # is imported from somewhere else)
    classes = [
        obj for obj in objects
        if isinstance(obj, type)
        and (obj.__module__ == module.__name__)]

    # if a superclass was given, filter the classes
    # again to remove those that aren't its subclass
    if superclass is not None:
        classes = [
            cls for cls in classes
            if issubclass(cls, superclass)]

    return classes


def get_class(module, superclass=None):
    """
    Return the lone class contained by *module*, or raise a descriptive
    AttributeError if *module* contains zero or more than one class.
    This is useful when expecting a single class from a module without
    knowing its name, to avoid the usual constantly-named object in a
    module (eg. App, Backend, Command, Handler).
    """

    classes = get_classes(
        module, superclass)

    if len(classes) == 1:
        return classes[0]

    # the error message includes *superclass*
    # if one was given, otherwise it's generic
    desc = "subclasses of %s" % (superclass.__name__)\
        if superclass else "new-style classes"

    if len(classes) > 1:
        names = ", ".join([cls.__name__ for cls in classes])
        raise(AttributeError("Module %s contains multiple %s (%s)." %
                            (module.__name__, desc, names)))

    else:  # len < 1
        raise(AttributeError("Module %s contains no %s." %
                            (module.__name__, desc)))


def get_package_path(package_name):
    """
    Import *package_name*, and return its absolute path.

    >>> get_package_path("encodings") # doctest: +ELLIPSIS
    '/.../python.../encodings'

    Raise AttributeError if *package_name* is a module (*.py).

    >>> get_package_path("csv")
    Traceback (most recent call last):
    ...
    AttributeError: 'csv' is not a package
    """

    try:
        __import__(package_name)
        return sys.modules[package_name].__path__[0]

    # wrap with a better message
    except AttributeError:
        raise(AttributeError('%r is not a package' % (package_name)))
