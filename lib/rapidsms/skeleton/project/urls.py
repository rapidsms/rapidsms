#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


# i'm afraid that url routing within rapidsms is a bit of a mess, right
# now. the rapidsms.djangoproject.urls module reveals artifacts of an
# earlier, more magical framework. you can add your urls here, but the
# urls of the contrib apps are bundled within them, making them rather
# difficult to change. fixing this (removing the magic) is a priority.


from django.conf.urls.defaults import *
urlpatterns = patterns("",
    
)
