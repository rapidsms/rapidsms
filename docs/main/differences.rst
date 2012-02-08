New things to RapidSMS (and maybe for Django devs as well)
===========================================================

Extensible Models
------------------

The ExtensibleModelBase class lets you define models that link to other models, creating a chain of inheritance. By defining django models in::

    <extending_app>/extensions/<app_to_extend>/<model_to_extend>.py


you can get new top-level properties on the <model_to_extend> object.

In order for your base model class to support this you must add the following line::

    __metaclass__ = ExtensibleModelBase


Additionally the django models defined in the file should be declared abstract, since they won't be instantiated.

See the `Contact` model in the rapidsms core for an example of a model that can be extended, and the contact.py file in the locations/extensions/rapidsms contrib app folder for an example of it being extended. The end result of these two classes is that a .location is available on instances of Contact models as a foreign key to the Location table.

Django App Settings
--------------------

A handy little module that lets you define default settings within your django app and import them from a second settings.py. There is a good README in the django-app-settings submodule, but from a practical use standpoint, all you have to remember is to include a settings.py in your root app/ directory with any app-specific settings and import your settings from rapidsms.conf instead of django.conf and everything should just work. It's a good practice to use app-specific prefixes for your settings to avoid conflicts.

The Webapp
-----------

The `apps/webapp` is gone, and `lib/rapidsms` _is_ the new webapp. If you are new to rapidsms, just remember that lib/rapidsms is the app that is the main entry point to the webui, and that's where the base urls and templates are stored.

Different Classes
------------------

(these are also described in the porting apps section below)

Reporter app's commonly used Reporter, PersistantBackend, and PersistantConnection models are gone!

They have been replaced by rapidsms.model's Contact, Backend, and Connection models (which are all persistent, so app authors no longer need to worry about keeping track of such things).

lib/rapidsms/message.py's Message is gone! Instead, there are MessageBase, IncomingMessage, and OutgoingMessage classes in lib/rapidsms/messages/

rapidsms.app.App has been replaced by rapidsms.apps.base.AppBase

Porting apps to work with the latest RapidSMS code
----------------------------------------------------

Views
^^^^^^

RapidSMS's wrapper of Django's render_to_response method is gone, so change the import line from::

    from rapidsms.utils import render_to_response

to::

    from django.template import RequestContext
    from django.shortcuts import render_to_response

and change the render_to_response method calls from::

    return render_to_response(req, "myapp/mytemplate.html")

to::

    return render_to_response("myapp/mytemplate.html", context_instance=RequestContext(req))


Apps
^^^^^

`rapidsms.app.App` ---> `rapidsms.apps.base.AppBase`

`from reporters.models import Reporter, PersistantConnection` ---> `from rapidsms.models import Contact, Connection`

`from rapidsms.message import Message` ---> `from rapidsms.messages import IncomingMessage, OutgoingMessage`

Handlers
^^^^^^^^^

`from rapidsms.contrib.handlers import KeywordHandler` ---> `from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler`
