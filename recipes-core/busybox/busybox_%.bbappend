# EFI Boot Guard
#
# Copyright (c) Siemens AG, 2017
#
# Authors:
#   Claudius Heine  <ch@denx.de>
#   Andreas Reichel <andreas.reichel.ext@siemens.com>
#
# This work is licensed under the terms of the GNU GPL, version 2.
# See the COPYING.GPLv2 file in the top-level directory.

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI += "file://watchdog.cfg \
            file://watchdog.sh"

do_install_append() {
	install -d "${D}${sysconfdir}/init.d"
	install -m 0755 "${WORKDIR}/watchdog.sh" "${D}${sysconfdir}/init.d/watchdog.sh"
	install -d "${D}${sysconfdir}/rcS.d"
	ln -sf ../init.d/watchdog.sh "${D}${sysconfdir}/rcS.d/S00watchdog.sh"
}
