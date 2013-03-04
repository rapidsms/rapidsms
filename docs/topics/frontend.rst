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


.. _Twitter Bootstrap: http://twitter.github.com/bootstrap/
