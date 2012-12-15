How to Make RapidSMS Tutorial Videos
======================================

This "how to" is for Linux users, primarily Ubuntu users. It will work in 10.4, Karmic Koala. The goal is to be able to record your screen and voice, transcode it into a format that youtube understands and then upload your video to youtube.

Recording Sound and Video
=============================

First you will need a piece of software to record your screen and voice. There are many of these but not all are very well supported. recordMyDesktop works well and is simple and configurable. To get this you can go to the Applications Menu>Ubuntu Software Center and type "gtk rec" gtk-recordMyDesktop will come up first and you can double click on it to install. It will then be in your Applications Menu under "Sound & Video."

Alternatively just type::

    sudo apt-get install gtk-recordMyDesktop

There is a tutorial on how to install, use and configure recordMyDesktop here:

http://www.youtube.com/watch?v=HaAXW67SUgk

Turning your .ogv into .avi
==============================

Next you will want to take the .ogv format that recordMyDesktop creates and turn it into a format that youtube will accept. There are many pieces of software that can do this and a good one to turn it into .avi is mencoder.

To install mencoder type::

    sudo apt-get install mencoder


Once it is installed type (changing foo to the path and name of your video)::

    mencoder foo.ogv -o foo.avi -oac mp3lame -lameopts fast:preset=standard -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=4000

There is a tutorial on how to convert using mencoder and then upload to youtube here:

http://www.youtube.com/watch?v=VuhYV0voL3M

Posting to youtube
====================

Create a youtube account (or use your existing one) and follow the tutorial above or any of the billion other tutorials on the internet to upload your video. Tag your video with both "rapidSMS" and "tutorial." Then share the video with the RapidSMS Developer user on youtube and post a message to the mailing list about your new video. It will get favorited by the community and show up on the channel.

The youtube channel is here: http://www.youtube.com/user/rapidsmsdev

For access to the RapidSMSdev youtube account ask Merrick.
