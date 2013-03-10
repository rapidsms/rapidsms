Front End
=========

Introduction
------------

RapidSMS provides an optional framework for making the applications on your
site have a common look and feel.

Starting with release 0.12.0, the framework is based on `Twitter Bootstrap`_.

...

Top menu
--------

The menu at the top of the page is a Bootstrap navigation bar.

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

Keep these links short. If the links take up too much room on the page,
they will wrap in the header, forcing the bottom of the page header
down and overlapping part of the page.

Login/Logout links
~~~~~~~~~~~~~~~~~~

The login or logout link can be removed or replaced by overriding the
`login-link` block:

.. code-block:: html

     {% block login_link %}
        <li>
            {% block auth %}
                {% if user.is_authenticated %}
                    <a href="{% url 'rapidsms-logout' %}">{% trans "Log out" %} {{ user.username }}</a>
                {% else %}
                    <a href="{% url 'rapidsms-login' %}">{% trans "Log in" %}</a>
                {% endif %}
            {% endblock auth %}
        </li>
    {% endblock %}

Admin link
~~~~~~~~~~

Similarly, a link to the Django admin is shown for staff users who
are logged in. Change that by overriding the `admin-link` block:

.. code-block:: html

    {% block admin_link %}
        {% if user.is_staff %}
            <li>
                <a href="{% url 'admin:index' %}">{% trans "Admin" %}</a>
            </li>
        {% endif %}
    {% endblock %}

.. _Twitter Bootstrap: http://twitter.github.com/bootstrap/
