If want to use a GSM modem with Ubuntu Linux it is very easy.

Acquiring a Modem
====================

We highly recommend you use the MultiTech MTCBA-G-F4 modem as it has been used extensively field and it supports a very good implementation of AT command set with minimal "surprises".

Here is the modem we recommend:

http://www.multitech.com/en_US/products/families/multimodemgprs/

We purchase our MultiTech modems here:

http://www.modemexpress.com/servlet/the-1529/Multitech-Modem-Wireless-GPRS/Detail

For other modems you can log your experiences at: :doc:`Modem Configs <../configuration/modem-configs>`

Connecting the Modem
========================

Just attach it to your computer you will see mounted at one of two places depending if it is a USB device or a serial device.

If you are using the serial version of the modem you will likely find it at: `/dev/ttyS0`

If you are using the USB version or USB serial adaptor of the modem you will likely find it at: ``/dev/ttyUSB0``

Talking to the Modem
======================

Linux tools that talk to the modem using the AT command set include:

* gtkterm
* picocom
* minicom
* screen

We recommend you use gtkterm. To install it type::

    sudo apt-get install gtkterm

Make sure you modem is plugged in and turned on then type gtkterm and tell it which port to find the mode on. For example for the USB to serial device::

    gtkterm --port /dev/ttyUSB0


Then try the equivelent of a "hello world" by typing::

    AT

The modem should echo back::

    OK

Other AT commands, including those for sending and receiving SMS, are described here: 

http://www.multitech.com/en_US/DOCUMENTS/Families/MultiModemGPRS/manuals.aspx

External Resources
======================

Changing the frequency band on the multitech with ubuntu http://infoactivist.net/2010/10/rapidsms-on-ubuntu-10-04-with-multitech-mtcba-g-u-f4/