#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.utils import paginated


class Column(object):
    creation_counter = 0

    def __init__(self, verbose_name=None, sortable=True):
        self.verbose_name = verbose_name
        self.sortable = sortable

        self.creation_counter = Column.creation_counter
        Column.creation_counter += 1

    @staticmethod
    def sort_key(column):
        return column.creation_counter


class BoundColumn(object):
    """
    Column bound to a table instance.
    """

    def __init__(self, table, name):
        self._column = getattr(table, name)
        self._table = table
        self._name = name

    def sorted(self):
        return self._table.sort_field == self._name

    def sort_url(self):
        params = self._table.request.GET.copy()
        params["sort"] = self._name

        if self._table.sort_field == self._name:
            params["order"] = (self._table.sort_order == "desc")\
                and "asc" or "desc"

        elif "order" in params:
            del params["order"]

        return "%s?%s" % (self._table.request.path, params.urlencode())

    def __getattr__(self, name):
        return getattr(self._column, name)


class MetaTable(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super(MetaTable, cls).__new__(
            cls, name, bases, attrs)

        new_cls._columns = [
            key
            for key, value in attrs.items()
            if isinstance(value, Column)]

        return new_cls


class Table(object):
    __metaclass__ = MetaTable

    def __init__(self, request):
        self.request = request

        # check the validity of the 'sort' param
        self.sort_field = self.request.GET.get("sort", "date")
        self.sort_order = self.request.GET.get("order", "asc")

        # check that sort_field is valid
        if not self.sort_field in self._columns:
            raise ValueError()

        # refuse invalid sort orders
        if self.sort_order != "asc"\
        and self.sort_order != "desc":
            raise ValueError()

        self._bound_column_cache = []

    def get_query_set(self):
        raise NotImplemented()

    def get_sorted_query_set(self):
        qs = self.get_query_set().order_by(self.sort_field)
        return qs.reverse() if (self.sort_order == "desc") else qs

    @property
    def columns(self):
        return sorted([
            BoundColumn(self, name)
            for name in self._columns],
            key=Column.sort_key)

    @property
    def paginator(self):
        return paginated(self.request, self.get_sorted_query_set())

    @property
    def verbose_sort_order(self):
        return (self.sort_order == "asc")\
            and "ascending" or "decending"

    #@property
    #def rows(self):
    #    return self.paginator.object_list
