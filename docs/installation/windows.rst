Windows Instructions: Installing latest RapidSMS source for development
========================================================================

Rapidsms in a virtual env is not yet working for windows! If you have it working please update this page!

If you use Eclipse, check out the :doc:`Eclipse Configuration <../configuration/eclipseconfiguration>` page.

First download and install setuptools from: http://pypi.python.org/pypi/setuptools

Add the scripts directory in python to your path (via environment variables).

1 Install virtualenv and pip
-----------------------------

From a terminal, run::

    $ easy_install virtualenv
    $ easy_install pip


2 Create virtualenv
--------------------
::

    $ virtualenv --no-site-packages rapidsms_dev
    $ cd rapidsms_dev\Scripts
    $ activate.bat

(you will need to run the bat script to activate your virtualenv everytime you start your rapidsms application)

3 Install RapidSMS
--------------------
::

    $ pip install rapidsms


From here you can follow the :doc:`Debian-based <debianbased>` turorial (starting at step 5)...