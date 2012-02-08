RapidSMS is a Free and Open Source framework for developing short message-based applications.

RapidSMS is a messaging development framework, in the same way that Django or Rails are web development frameworks. For example, Django is a framework -- but has out-of-the-box contrib apps that ship with the framework like admin interface, authentication, forms, etc.. (they say 'batteries included). On the other hand, DjangoCMS (http://www.django-cms.org/) is a product that is built with Django -- it is not Django -- that users can customize and use to manage content and power their organizations websites.

RapidSMS is designed to do the heavy lifting for you. You implement your application logic, and RapidSMS takes care of the rest.

RapidSMS is designed specifically to facilitate building applications around mobile SMS.
... but it supports pluggable messaging backends, including IRC and email, and more are possible (e.g. http).

* RapidSMS is Open Source and is written in Python.
* RapidSMS uses Django, allowing you to easily develop web-based views of your messaging app.
* RapidSMS is designed to scale efficiently.
* RapidSMS provides (or will eventually provide) core support for message parsing, i18n, and more.

RapidSMS is not:

* RapidSMS is not a product that does anything out-of-the-box. Developers can make products using RapidSMS that can provide functionality for SMS services. The most useful of these products ("apps") can even be shipped with the framework as contrib apps that will work out of the box