.. _provision_what:

What to Provision
-----------------

.. _a-good-basic-setup:

A Good Basic Setup
==================

One of the intimidating things about deploying a Django application is
the number of decisions that need to be made.

Here are a recommended set of choices for deploying Django
apps. Most of these choices have alternatives, and some are decided
for you if you're using a PaaS, but in the absence of a
reason to use an alternative, these should work reasonably well in most cases.

Operating System
    `Ubuntu LTS server`_: Ubuntu because it's stable, it's free, and it's
    popular among developers, so any Django or Python software is likely to
    work well on it. LTS because of the long support guarantee, and server
    since we don't need costly graphical desktop environments on our
    servers.

Django version
    The `latest released version`_: because it will be supported by security
    fixes for the longest time, compared to any older version, and Django
    has a history of putting out pretty stable releases. (Maybe wait a
    couple of weeks after a new release to see if there's a .1 release.)

Database
    `PostgreSQL`_: because it and MySQL are the most popular free databases, so
    it's well supported, and MySQL is lacking some features. For example,
    MySQL cannot perform schema changes in transactions, so if a schema
    migration fails in the middle, your data could be left in an indeterminate
    state.

    Sometimes there are reasons to use another database than PostgreSQL.
    Just be sure not to use SQLite, even though it's very easy to set up.
    It's not suited for production use.

Web server
    `Apache`_ or `nginx`_: both work well as front ends for Django applications.

    It is important to have a web server handle incoming requests, rather than
    having them go directly to the Django application, for a couple of reasons:

    * Web servers are designed to efficiently process the load of incoming
      requests, and deal with the wide variety of web clients. That lets
      the WSGI server focus on hosting the Django application.
    * The Django application should never be used to serve static files in
      production. If the static files are not being served by another system,
      the web server is used to either serve the static files, or proxy the
      requests to something other than the Django application.

WSGI server
    `mod_wsgi`_ with `Apache`_, or `gunicorn`_: Either of these work well.

    The WSGI server provides a Python process to run your Django application.

    `mod_wsgi`_ can be convenient if you are already be using Apache on the
    server for static files. Gunicorn is easier to configure and run.

    In any case, never use `runserver` in production. It is not secure,
    and performs poorly.

Message queue server
    `RabbitMQ`_: because it's stable and popular.  `Redis`_ is also
    commonly used as a message queue server.

Schema migration
    `South`_: because it's really the only choice available for schema migrations
    in Django.

RapidSMS Router
    :router:`DatabaseRouter`: because it has the most features.

Asynchronous task scheduler
    `Celery`_: see :ref:`why_celery`.


Other Recommendations
=====================

Here are a few other recommendations.

`Fail2ban`_
    install to detect and block some intrusion attempts

Firewall
    Block any incoming traffic that isn't needed by your application or
    server. Ubuntu provides the `ufw`_ tool which makes this easy.

Logwatch
    `Logwatch`_ will check your system logs daily and email you a daily
    report. This is helpful for spotting unusual activity.

`Automatic security updates`_
    You can set up Ubuntu to automatically install security-related
    updates.

ntp
    use ntp to keep system clock up to date


.. _Apache: http://httpd.apache.org
.. _Automatic security updates: https://help.ubuntu.com/community/AutomaticSecurityUpdates
.. _Celery: http://www.celeryproject.org/
.. _Fail2ban: http://www.fail2ban.org/wiki/index.php/Main_Page
.. _gunicorn: http://gunicorn.org/
.. _latest released version: https://www.djangoproject.com/download/
.. _Logwatch: https://help.ubuntu.com/community/Logwatch
.. _mod_wsgi: http://code.google.com/p/modwsgi/
.. _nginx: http://nginx.org
.. _PostgreSQL: http://www.postgresql.org/
.. _RabbitMQ: http://www.rabbitmq.com/
.. _Redis: http://redis.io
.. _South:  http://south.readthedocs.org/en/latest/
.. _Ubuntu LTS Server: http://www.ubuntu.com/business/server
.. _ufw: https://help.ubuntu.com/community/UFW
