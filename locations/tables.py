#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from djangotables import Table, Column


class LocationTable(Table):
    name = Column()
    #slug = Column()

    #class Meta:
    #    order_by = 'name'
