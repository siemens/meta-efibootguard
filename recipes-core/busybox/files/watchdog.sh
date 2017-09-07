#!/bin/sh
### BEGIN INIT INFO
# Provides:          watchdog
# Required-Start:    mountvirtfs
# Required-Stop: 
# Default-Start:     S
# Default-Stop:
# Short-Description: Start watchdog
# Description:
### END INIT INFO

. /etc/default/rcS

/sbin/watchdog /dev/watchdog

: exit 0

