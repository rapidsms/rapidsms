from django.test import TestCase
from rapidsms.utils.modules import (import_class, import_module, get_class)


class ParentA(object):
    pass


class ChildOfA(ParentA):
    pass


class ParentB(object):
    pass


class ImportClassTest(TestCase):

    def test_bad_path(self):
        """Invalid paths should raise an error."""
        self.assertRaises(ImportError, import_class, "bad_path")

    def test_valid_class(self):
        """Valid paths should return the proper class."""
        class_ = import_class("rapidsms.utils.test_modules.ParentA")
        self.assertEqual(class_, ParentA)

    def test_nonexistent_class(self):
        """Valid path with invalid class should raise an error."""
        self.assertRaises(ImportError, import_class,
                          "rapidsms.utils.test_modules.NoClass")

    def test_valid_base_class(self):
        """Class should match base_class if supplied."""
        class_ = import_class("rapidsms.utils.test_modules.ChildOfA",
                              ParentA)
        self.assertTrue(issubclass(class_, ParentA))
        self.assertEqual(class_, ChildOfA)

    def test_invalid_base_class(self):
        """If class doesn't match base_class, an error should be raised."""
        self.assertRaises(ImportError, import_class,
                          "rapidsms.utils.test_modules.ParentB",
                          base_class=ParentA)


class GetClassTest(TestCase):

    def test_get_class(self):
        """get_class() should return the proper class."""
        module = import_module('rapidsms.utils.test_modules')
        class_ = get_class(module, ParentB)
        self.assertEqual(ParentB, class_)

    def test_no_classes_found(self):
        """An error should be raised if no classes are found."""
        from rapidsms.backends.base import BackendBase
        module = import_module('rapidsms.utils.test_modules')
        self.assertRaises(AttributeError, get_class, module, BackendBase)

    def test_multiple_classes_found(self):
        """An error should be raised if multiple classes are found."""
        module = import_module('rapidsms.utils.test_modules')
        self.assertRaises(AttributeError, get_class, module, ParentA)
