RapidSMS contrib applications
=============================

The goal of the contributed apps repository is to provide a place for
applications that are designed to be reusable and solve common problems to
live. All applications in this repository must be sufficiently abstract so they
can be used for any deployment.

Some apps and interfaces in the contrib repository include:

* Locations: Locations uses the model "location," an abstract way for app
  authors to attach metadata to geographic points and includes a WebUI to 
  display them on a map. It is designed to be extensible by other apps so it is reusable.

  Locations provide a flexible framework for dealing with adminstrative
  boundaries, water points, health facilities, schools, or anything else that is
  tied to the data being collected and it's physical location on a map. More
  information about how to configure locations to fit your project's needs can be found on the Locations page.

* Messaging Interface: There is a messaging API that provides a simple way for
  users of the web interface to send messages to contacts. It allows app
  authors to create message-able objects, for example a school could be
  assigned contacts which would allow a message to be sent from the web
  interface to all the teachers in the school.

* :doc:`Handlers <handlers>`: Handlers a slimmer alternative to apps, instead
  of 1 app with 10   interface patternhandler provides a regex interface
  basehandler makes it easy   to write more handlers echo app is an app that is
  merely a container for a   handler that echos a message. It is a good example
  to look at to see how   handlers work.
