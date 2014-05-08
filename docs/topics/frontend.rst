Front End
=========

Introduction
------------

RapidSMS provides an optional framework for making the applications on your
site have a common look and feel.

Starting with release 0.12.0, the framework uses `Twitter Bootstrap`_, v2.2.2.

This document is intended to describe how the contrib apps use Bootstrap,
and how you might use it in your own apps.

Base template
-------------

Your templates should extend ``base.html``, either directly or indirectly.
That will load Bootstrap and set up the common page structure for RapidSMS
apps.

The simplest way to provide content for your page is to override
``{% block content %}``. That block is rendered inside of a Bootstrap
`fluid row`_ like this:

.. code-block:: html

    <div class="row-fluid content">
       {% block content %}{% endblock %}
    </div>

You can then divide your page into columns using Bootstrap ``span``
classes:

.. code-block:: html

    {% block content %}
      <div class="span6">  Left side   </div>
      <div class="span6">  Right side  </div>
    {% endblock %}

See the Bootstrap documentation for more things you can do inside a fluid
row to affect the layout.

Title
-----

Set the page title with ``{% block title %}``:

.. code-block:: html

    {% block title %}Send a Text Message{% endblock title %}

Additional styles
-----------------

If you have a page that needs additional stylesheets, you can override
``{% block extra_stylesheets %}``:

.. code-block:: html

    {% block extra_stylesheets %}
      <link type="text/css" rel="stylesheet"
            href="{{ STATIC_URL }}my-app/stylesheets/my-app.css" />
    {% endblock %}

Additional javascript
---------------------

Additional javascript can be added by overriding ``{% extra_javascript %}``:

.. code-block:: html

    {% block extra_javascript %}
      <script src="{{ STATIC_URL }}my-app/js/my-app.js"
              type="text/javascript"></script>
    {% endblock %}

Page header
-----------

To display a header at the top of the page in the same style as other apps,
use the ``page-header`` class and ``<h1>``.  If you need to divide the
page into columns after that, you can include a div and then put your
``span`` divs inside that to keep everything organized:

.. code-block:: html
    :emphasize-lines: 2-4

    {% block content %}
      <div class="page-header">
        <h1>My Application Page Header</h1>
      </div>
      <div>
        <div class="span6">  Left side   </div>
        <div class="span6">  Right side  </div>
      </div>
    {% endblock %}


Top menu
--------

The menu at the top of the page is a Bootstrap `navigation bar`_.

Your site can configure the links that appear between the RapidSMS
logo and the login/logout link by overriding the
``rapidsms/_nav_bar.html`` template.  You can do this by creating
a file with this path from the top of your project:
``templates/rapidsms/_nav_bar.html``.

Your template will be included in the base page template. It should
contain ``<li>`` elements for each link. Example:

.. code-block:: html

    {% load url from future %}
    <li><a href="{% url 'app1' %}">App1</a></li>
    <li><a href="{% url 'app2' %}">App2</a></li>
    <li><a href="{% url 'app3' %}">App3</a></li>

.. note::

    Keep these links short. If the links take up too much room on the page,
    they will wrap in the header, forcing the bottom of the page header
    down and overlapping part of the page.

Login/Logout links
~~~~~~~~~~~~~~~~~~

The login or logout link can be removed or replaced by overriding the
`login_link` block. Here's the default value:

.. code-block:: html

     {% block login_link %}
       <li>
         {% block auth %}
           {% if user.is_authenticated %}
             <a href="{% url 'rapidsms-logout' %}">
               {% trans "Log out" %} {{ user.username }}
             </a>
           {% else %}
             <a href="{% url 'rapidsms-login' %}">{% trans "Log in" %}</a>
           {% endif %}
         {% endblock auth %}
       </li>
    {% endblock %}

Admin link
~~~~~~~~~~

Similarly, a link to the Django admin is shown for staff users who
are logged in. Change that by overriding the `admin_link` block.
Here's the default value:

.. code-block:: html

    {% block admin_link %}
      {% if user.is_staff %}
        <li>
          <a href="{% url 'admin:index' %}">{% trans "Admin" %}</a>
        </li>
      {% endif %}
    {% endblock %}

Tables
------

.. FIXME: add link to messagelog once we have a page for it

To include tables in a page, the `django_tables2`_ package works well.
Look at the `rapidsms.contrib.messagelog` app for an example. Note
particularly how the view overrides the default template used by
`django_tables2` to use one that takes advantage of Bootstrap styling.

Forms
-----

Bootstrap can make `forms`_ look nice too. RapidSMS's form tags have
been updated to work well with Bootstrap.  The ``render_form`` tag
will render your form's data fields correctly for Bootstrap. Then all you
have to do is add any submit buttons you need, properly marked up.
See the Bootstrap documentation for full details, but here's an example from
another contrib app,
:doc:`rapidsms.contrib.httptester </topics/contrib/httptester>`:

.. code-block:: html
   :emphasize-lines: 2,13,16-18

    {% extends "base.html" %}
    {% load forms_tags %}
    ...
    {% block content %}
      <div class="page-header">
        <h1>Message Tester</h1>
      </div>

      <div>
        <div class="span4">
          <div>
            <form action="" method="post" enctype="multipart/form-data">
              {% render_form message_form %}
              {% csrf_token %}

              <div class="form-actions">
                <button type="submit" class="btn btn-primary" id="send-btn" name="send-btn">Send</button>
                <label for="send-btn">Send single or multiple messages</label>
                ...
              </div>
            </form>
          </div>
        </div>
        <div class="span8">
        ...
         </div>

      </div>
    {% endblock %}

.. _messages_to_users:

Messages to Users
-----------------

.. versionadded:: 0.15.0

If you use the `Django messages framework`_ to send messages to your users, the base
template will display them nicely above the page content.


.. _Twitter Bootstrap: http://bootstrapdocs.com/v2.2.2/docs/index.html
.. _fluid row: http://bootstrapdocs.com/v2.2.2/docs/scaffolding.html#fluidGridSystem
.. _navigation bar: http://bootstrapdocs.com/v2.2.2/docs/components.html#navbar
.. _django_tables2: http://django-tables2.readthedocs.org/en/latest/
.. _forms: http://bootstrapdocs.com/v2.2.2/docs/base-css.html#forms
.. _Django messages framework: https://docs.djangoproject.com/en/dev/ref/contrib/messages/
