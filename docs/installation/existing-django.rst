Install RapidSMS in an existing Django Project
================================================

After installing virtualenv, etc for your platform::

 
    $ mkvirtualenv rapidsms-from-django
    $ pip install django
    $ pip install rapidsms
    $ django-admin.py startproject rapidtest

Additionally, you need to make the following modifications:

http://bitbucket.org/tobias.mcnulty/rapidsms-from-django/changeset/af0ff294d7a6