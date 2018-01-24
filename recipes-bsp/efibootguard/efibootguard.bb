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

LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=b234ee4d69f5fce4486a80fdaf4a4263"

SRC_URI = "git://github.com/siemens/efibootguard.git;protocol=https;branch=master"
SRCREV = "e3263ab8132b8d0be3b1e5513afc4a93f287e9e5"

S = "${WORKDIR}/git"

DEPENDS = "gnu-efi pciutils zlib"

inherit autotools deploy

COMPATIBLE_HOST = "(x86_64.*|i.86.*)-linux"

PACKAGES = "${PN}-tools \
            ${PN}-tools-dbg \
            ${PN}-tools-staticdev \
            ${PN}-tools-dev \
            ${PN}-efi"

EXTRA_OECONF = "--with-gnuefi-sys-dir=${STAGING_DIR_HOST} \
                --with-gnuefi-include-dir=${STAGING_INCDIR}/efi \
                --with-gnuefi-lib-dir=${STAGING_LIBDIR}"

FILES_${PN}-tools = "${bindir}"
FILES_${PN}-tools-dbg = "/usr/src/debug"
FILES_${PN}-tools-staticdev = "${libdir}/lib*.a"
FILES_${PN}-tools-dev = "${includedir}/${BPN}"
FILES_${PN}-efi = "${libdir}/${BPN}"

do_deploy () {
	install ${B}/efibootguard*.efi ${DEPLOYDIR}
}
addtask deploy before do_build after do_compile

BBCLASSEXTEND = "native"
DEPENDS_class-native = "zlib"

do_compile_class-native () {
	oe_runmake bg_setenv
}

do_install_class-native () {
	install -d ${D}${bindir}/
	install -m755 ${B}/bg_setenv ${D}${bindir}/
	ln -s bg_setenv ${D}${bindir}/bg_printenv
}

do_deploy_class-native () {
}

