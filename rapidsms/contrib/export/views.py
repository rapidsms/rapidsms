#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import datetime
from subprocess import Popen, PIPE
from django.conf import settings
from django import http


def database(req):
    """
    Return a SQL dump of the current database, by reading the settings
    from settings.py, and calling the relevant dump program. Currently,
    only mySQL and SQLite3 are supported.
    """

    if settings.DATABASE_ENGINE == "mysql":
        cmd = "mysqldump --host=%s --user=%s --password=%s %s" %\
            (settings.DATABASE_HOST, settings.DATABASE_USER,
             settings.DATABASE_PASSWORD, settings.DATABASE_NAME)

    elif settings.DATABASE_ENGINE == "sqlite3":
        cmd = "sqlite3 %s .dump" %\
            (settings.DATABASE_NAME)

    else:
        return http.HttpResponse(
            "Sorry, %s databases are not "
            "supported yet." % (settings.DATABASE_ENGINE),
            content_type="text/plain",
            status=500)

    # execute the dump command, and wait for it to terminate
    proc = Popen([cmd], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    sql = proc.communicate()

    # download the file as plain text
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    resp = http.HttpResponse(sql, mimetype="text/plain")
    resp["content-disposition"] = "attachment; filename=%s.sql" % (today)
    return resp
