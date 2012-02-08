In order for this tutorial to make sense you first have to have a Multi-tech modem attached to your computer and we documented that process here: :doc:`Using The Multi-tech Modem With Windows <windows/modem>`

In order to get the MultiTech Modem to create a Data Connection and allow us to use the internet we discovered that you have to use the built in windows utility rasdial. It is not necessary to pass any AT commands to the modem. (In Linux you can use wvdial to do the same thing.)

Using the built in command line dialer rasdial we created two batch scripts one to connect and one to disconnect.

The connection batch script is called conn.bat and has the following line of code::

    rasdial Internet /phone:*99***1#

    [initiates dialer] [connection name] [/command]

The disconnect batch script is called discon.bat and has the following line of code::

    rasdial Internet /disconnect

    [initiates dialer] [connection name] [/command]

Later we integrated the commands directly in our Python script using::

    os.popen
    os.popen("rasdial Internet /phone:*99***1#")
    os.popen("rasdial Internet /disconnect")


Notes
=========

* We can send credit to the modem
* If the card is all the way out of credit the modem may need to be dis-connected and re-connected to the computer
* After you create a network connection on this XP install and assign it a name, it creates another network connection called internet assigned to the same modem. The one you name seems to connect and then disconnect, the one that XP creates seems able to maintain a persistent connection.