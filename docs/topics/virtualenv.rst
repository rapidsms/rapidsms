
.. _using-virtualenv:

Using virtualenv
****************

We highly recommend using `virtualenv`_ and `virtualenvwrapper`_ to work on
RapidSMS. These tools provide isolated Python environments, which are more
practical than installing packages system wide. They also allow installing
packages without administrator privileges.

.. _virtualenv: http://www.virtualenv.org/en/latest/index.html
.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/en/latest/

1. **Install virtualenv and virtualenvwrapper.** Use pip to install the latest
   version (and upgrade if you have an older copy):

.. code-block:: bash

    sudo pip install --upgrade virtualenv
    sudo pip install --upgrade virtualenvwrapper

Then follow the `virtualenvwrapper install docs`_ to setup your shell properly.

.. _virtualenvwrapper install docs: http://virtualenvwrapper.readthedocs.org/en/latest/install.html

2. **Create a new virtual environment for RapidSMS.** Now we'll create a new
   virtual environment to isolate our development:

.. code-block:: bash

    mkvirtualenv --distribute --no-site-packages rapidsms

3. **Remember to activate your virtualenv.** If you restart or need to return
   to your virtualenv at any point, you can easily reactivate it:

.. code-block:: bash

    workon rapidsms
