#!/bin/sh

#
# IMPORTANT: To use, do the folling:
#
# 1. Change 'NAME' variable to the name of your project. E.g. "bednets_for_nigeria"
# 2. Place this file in the TOP-LEVEL of your project, right where 'manage.py' is
# 3. Link it into /etc/init.d e.g. > ln -s /usr/local/my_project/rapidsms-init.sh /etc/init.d/
# 4. Add it to the runlevels, on Ubuntu/Debian there is a nice tool to do this for you:
#    > sudo update-rc.d rapidsms-init.sh defaults
#
# NOTE: If you want to run multiple instances of RapidSMS, just put this init file in each project dir,
#       set a different NAME for each project, link it into /etc/init.d with _different_ names,
#       and add _each_ script to the runlevels.
#

### BEGIN INIT INFO
# Provides:          amatd daemon instance
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts instances of rapidsms router and web server
# Description:       starts instance of rapidsms router and web server using start-stop-daemon
### END INIT INFO

# set -e

ME=`readlink -f $0`
WHERE_AM_I=`dirname $ME`

############### EDIT ME ##################
NAME="smsforum" # change to your project name
DAEMON=$WHERE_AM_I/manage.py
DAEMON_OPTS=""
RUN_AS=root
APP_PATH=$WHERE_AM_I
ROUTER_PID_FILE=/var/run/${NAME}_router.pid
#WEBSERVER_PID_FILE=/var/run/${NAME}_webs.pid
WEBSERVER_PORT=8000
WEBSERVER_IP=127.0.0.1
############### END EDIT ME ##################
test -x $DAEMON || exit 0

do_start() {
    echo -n "Starting router for $NAME... "
    start-stop-daemon -d $APP_PATH -c $RUN_AS --start --background --pidfile $ROUTER_PID_FILE  --make-pidfile --exec $DAEMON -- route $DAEMON_OPTS
    echo "Router Started"
    sleep 2
    echo -n "Starting webserver for $NAME... "
    start-stop-daemon -d $APP_PATH -c $RUN_AS --start --background --exec $DAEMON -- runserver $WEBSERVER_IP:$WEBSERVER_PORT
    echo "Webserver Started"
}

hard_stop_runserver() {
    for i in `ps aux | grep -i "manage.py runserver" | grep -v grep | awk '{print $2}' ` ; do
        kill -9 $i
    done
    echo "Hard stopped runserver"
}

hard_stop_spomsky() {
    for i in `ps aux | grep -i "spomskyd" | grep -v grep | awk '{print $2}' ` ; do
        kill -9 $i
    done
    rm $SPOMSKY_PID_FILE 2>/dev/null
    echo "Hard stopped Spomskyd"
}

hard_stop_router() {
    for i in `ps aux | grep -i "manage.py route" | grep -v grep | awk '{print $2}' ` ; do
        kill -9 $i
    done
    rm $ROUTER_PID_FILE 2>/dev/null
    echo "Hard stopped router"
}

do_hard_restart() {
    do_hard_stop_all
    do_start
}
    
do_hard_stop_all() {
    hard_stop_runserver
    hard_stop_router
}

do_stop() {
    echo -n "Stopping router for $NAME... "
    start-stop-daemon --stop --pidfile $ROUTER_PID_FILE
    rm $ROUTER_PID_FILE 2>/dev/null
    echo "Router Stopped"
    sleep 2
    echo -n "Stopping webserver for $NAME... "
    hard_stop_runserver
    echo "Webserver Stopped"
}

do_restart() {
    do_stop
    sleep 2
    do_start
}

# check on PID's, if not running, restart
do_check_restart() {
    for pidf in $ROUTER_PID_FILE ; do
	if [ -f $pidf ] ; then
	    pid=`cat $pidf`
	    if [ ! -e /proc/$pid ] ; then
		echo "Process for file $pidf not running. Performing hard stop, restart"
		do_hard_restart
		return
	    fi
	fi
    done
    
    # now check for runserver
    webs=`ps aux | grep -i "manage.py runserver" | grep -v grep | wc -l`
    if [ $webs -lt 2 ] ; then
	echo "Can't find webserver, doing hard stop, restart"
	do_hard_restart
    fi
}

case "$1" in
  start)
        do_start
        ;;

  stop)
        do_stop
        ;;

  check-restart)
	do_check_restart
	;;

  hard-stop)
	do_hard_stop_all
	;;

  hard-restart)
	do_hard_restart
	;;
  restart|force-reload)
	do_restart
        ;;

  *)
        echo "Usage: $ME {start|stop|restart|force-reload|check-restart|hard-stop|hard-restart}" >&2
        exit 1
        ;;
esac

exit 0