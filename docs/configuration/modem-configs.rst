Here you'll find some known working configurations for GSM Modems to use with RapidSMS. The top half the page addresses universal configuration issues for all GSM modems and the bottom half addresses configuration issues for specific modems.

Before you will need any of the information on this page, set up a modem and connect to it following this tutorial: Using A GSM Modem With Linux

Universal Configuration Issues
===============================

Resources
----------

This is a decent online reference to syntax of SMS related AT commands:
http://www.developershome.com/sms/howToSendSMSFromPC.asp

Comprehensive AT command reference:
http://www.multitech.com/en_US/DOCUMENTS/Families/MultiModemGPRS/manuals.aspx

Changing GSM Bands
-------------------

Modems use different GSM Bands in different parts of the world. A frequent problem that arises is that you use the modem in one part of the world, say North America, and then you travel somewhere else, say Africa, and it doesn't work.

Not all modems support all bands, so be careful to purchase one that is quadband. If you are using a quadband modem you can change the bands when you travel to different parts of the world. To switch the bands of modem from North America to a band that works in Europe/Africa you will need to change the frequency bands with an AT command.

The AT command for this is::

    AT+WMBS
    AT+WMBS=4,1 for US
    AT+WMBS=5,1 for Euro/Africa

Notes: rubyGSM supported this but it was never ported to pyGSM. It should be in the future. See:
http://github.com/adammck/rubygsm/blob/master/bin/gsm-modem-band

Modem Configuration
--------------------

If you are using pyGSM with RapidSMS then this page may give you some insights into what modems and devices will work with RapidSMS.

http://wiki.github.com/adammck/pygsm/

Sierra Wireless USBConnect 881
-------------------------------

This device works out of the box with pygsm. When connected, three separate ttyUSB devices are created: ttyUSB0, ttyUSB1, and ttyUSB2. I believe these represent isolated functions of the modem. Each device responds (or doesn't) differently to AT commands. ttyUSB2 is the one that works for sending SMS via AT commands.

This device does support using the AT+CNMI to forward incoming messages direct to the terminal (attached computer). This bypasses SIM storage and avoids the problem of SIMs filling up over time.

However, the device does not support the `AT+CNMI = 2,2,0,0,0` mode that pygsm tries to set by default. An edit to gsmmodem.py to change the string to AT+CNMI = 1,2,0,0,0 solves the problem.

Huawei E160 HSDPA USB modem
----------------------------

This modem has been reported to work "like a charm."

Huawei E220 modem
------------------

This modem is known to have issues with pyGSM. In order to get it to work with comment this line out of pygsm/lib/pygsm/gsmmodem.py::

    AT+WIND=0\r


Others have stated they have never got this modem working with pyGSM, we would not recommend it. People have also confirmed that they hacked pyGSM and got it working, a good project would be patching pyGSM so this modem would work out of the box.