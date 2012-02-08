Context
========

We are trying to set up a multi-tech modem on a windows XP computer to periodically take a dump of HIV results from an access database, connect to the internet, send the results over HTTP to RapidSMS, and then disconnect from the internet. The reason for this is two-fold:

The lab computers are not supposed to have a persistent connection to the internet.
If there was a persistent connection the cost would quickly get prohibative but if we only send a bit of data, once a day, it should remain cost effective.
Equipment and Network:

We are using the multitech MTCBA-G-F4 GPRS modem on Windows 7 Starter(we don't have an xp test environment) using a usb to serial connection. We are in Zambia and have both Zain and MTN sim cards.

Strategy
==========

There are two strategies for making the MultiTech use the mobile data network. The first is that we want Windows itself to set up the modem as a network connection and then allow us to surf the net over our sim card. The second is our ultimate goal. That is to use the AT command set to directly control the modem to give us net access. This will allow us to incorporate internet connectivity into a script that can run in the background. Ultimately we discovered that you cannot use hyperterminal to open a data connection with AT commands and actually pass any data but that we needed to use rasdial (or wvdial on linux) to open a connection and pass data over it. We document our solution here: Using Dialers With The Multi-tech

Dependencies
==============

In order to interact with the modem we need to install a usb to serial driver, the modem drivers, and hyperterminal.

Install the USB to serial driver
========================================

The driver you need is the PL2303 Driver which can be found on the prolific website. It is an .exe file which you need to install as opposed to installing it from the device manager. After you install it you also need to unplug and replug in the modem. If it doesn't work then reboot.

http://www.prolific.com.tw/Eng/downloads.asp?ID=31

Install Hyperterminal
============================

Hyperterminal is a utility that used to be included with windows in all versions before windows Vista. You could find it in older versions of Windows by going C:\\program files\windows nt\hypertrm.exe

To get it from XP: Start your Windows XP computer. Copy the files hypertrm.dll and hypertrm.exe from that computer to the target Windows Vista or Windows 7 system where you want to install it. Instead, you can download the files in a zip-package. If you are using the Zip files extract the two files from that pack to get target system. Make sure that both the files hypertrm.dll and hypertrm.exe are in one folder. Double-click the hypertrm.exe file to launch the HyperTerminal client. Once you are done, you have a HyperTerminal client that works normally on Windows 7 and Vista. So you have a HyperTerminal client completely free and it works perfectly.

There are instructions on how to do that and a link to the files zipped up here:

http://blog.taragana.com/index.php/archive/how-to-install-windows-xp-...

There is a tutorial on how to use hyperterminal here:

http://www.developershome.com/sms/howToUseHyperTerminal.asp

Downloaded MultiTech device drivers
=================================================

We downloaded both the xp and vista drivers from the multi-tech site and used the vista drivers with windows 7. You can find a directory of the MultiTech drivers here:

http://www.multitech.com/en_US/support/updates/drivers/drivers_by_filename.asp

Connect to GPRS network using windows built in networking and modem software
===============================================================================

We generally followed the commands from Multitech GPRS User Guide(30 page one), pages 23-24 which utilized the dial-up modem settings and the set up dial-up connection settings, but it was slightly different do to the fact we were using windows 7.

Here is what we did:

* Opened Control Panel form the Start menu
* Typed Modem into the search box on the upper right.
* Clicked on Phone and Modem
* Filled out the location with fake info
* clicked on the modem tab
* clicked "add"
* checked "Don't detect my modem; I will select it from a list: and clicked next
* click have disk
* clicked browse
* went to where we had the driver for the multitech downloaded (our desktop)
* since there were not windows 7 drivers we used the vista ones and loaded 9234MU.INF
* click OK
* we then selected MultiTech Systems GSM_GPRS Wireless Modem, click Next
* select the port comm 11
* select next and it should be finished
* Then select the multitech modem, then click on properties
* click on change settings
* click on the advanced tab
* add AT+CGDCONT=1,"IP","internet"
* click ok, click ok
* The modem is now connected.

Use the modem to connect to the internet
============================================

* Opened Control Panel form the Start menu
* Click on Network and Internet
* Click on Network and Sharing Center
* Click set up New connection or network
* Select "set up dial-up connection" and click next
* Enter `*99***1#` as the number and no username or password for Zain
* Hit connect
* You should be told you can connect to the internet.

Your multitech modem is now able to access the internet over the mobile gprs network

Notes
======

* we used the number *99# and no username or password for MTN
* we used the number *99***1# and no username or password for Zain
* we used com11 and had to disconnect hyperterminal to access to it.
* Only one type of service can access the port at a time.