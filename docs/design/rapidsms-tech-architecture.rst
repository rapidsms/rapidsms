RapidSMS basically consists of three parts: Applications, Backends, and the Router. 

It also uses Django to display a WebUI in a separate process (so running the router requires launching 'runrouter' and getting the website to work requires launching 'runserver' or apache or whatnot). Each component is explained below.

If you are new to RapidSMS most likely you will want to develop Applications.

Application (‘App’)
=====================

:doc:`Apps <apps>` perform one or more of the following functions:

Processes messages from the Router
Extends the data-model
Present UI within the WebUI
Examples:

Registration: Provides a web UI to administer remote users (model extension, UI)

Note: If your code does not perform any of the above tasks it’s probably a Library not an App.

Backends
=========

Backends receive messages from external sources, and deliver messages from Applications to external sources.

External sources include:

GSM Handset or Modem: via the pyGSM backend
HTTP clients: via HTTP backed
Router

Core code that routes messages between Backends and Apps.

WebUI
=======

A Django application that presents a unified web UI for all the installed and active Apps that have UI components.

Currently WebUI presents a ‘dashboard’ overview and tabs for each App with a UI.

Library
==========

A set of code, probably in the form of a Python Module (containing Class and/or Module functions) to perform any helper, utility, or domain specific functionality that can be usefully shared.

Examples of things that would make good libraries:

Message parsers (Keyworder, Form processor etc…)

Handlers
==========

Handlers are shortcuts which make it easy to deal with well-known behaviour. For example, the KeyWordHandler makes it easy to respond to keywords.

Currently we have:

:doc:`KeywordHandler <keyword-handler>` (matches a keyword, exactly as given)
PatternHandler (matches a RegEx)
Handlers can be found in lib/rapidsms/contrib/handlers
