# EFI Boot Guard
#
# Copyright (c) Siemens AG, 2017-2019
#
# Authors:
#   Claudius Heine  <ch@denx.de>
#   Andreas Reichel <andreas.reichel.ext@siemens.com>
#
# This work is licensed under the terms of the GNU GPL, version 2.
# See the COPYING.GPLv2 file in the top-level directory.

LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=b234ee4d69f5fce4486a80fdaf4a4263"

SRC_URI = "git://github.com/siemens/efibootguard.git;protocol=https;branch=master \
    file://0001-Makefile-Fix-static-tool-build-on-incremental-builds.patch \
    file://0002-Makefile-Fix-static-tool-build-on-incremental-builds.patch \
    file://0003-Find-pkg-config-on-cross-compilation.patch \
    file://0004-configure-libpci-detection-optional.patch \
"
SRCREV = "c01324d0da202727eb0744c0f67a78f9c9b65c46"

S = "${WORKDIR}/git"

DEPENDS_class-target = "gnu-efi pciutils zlib libcheck"

inherit autotools deploy pkgconfig

COMPATIBLE_HOST = "(x86_64.*|i.86.*)-linux"

PACKAGES = "${PN}-tools-dbg \
            ${PN}-tools-staticdev \
            ${PN}-tools-dev \
            ${PN}-tools \
            ${PN}"

EXTRA_OECONF = "--with-gnuefi-sys-dir=${STAGING_DIR_HOST} \
                --with-gnuefi-include-dir=${STAGING_INCDIR}/efi \
                --with-gnuefi-lib-dir=${STAGING_LIBDIR}"

FILES_${PN}-tools = "${bindir}"
FILES_${PN}-tools-dbg = "/usr/src/debug ${bindir}/.debug /usr/lib/debug"
FILES_${PN}-tools-staticdev = "${libdir}/lib*.a"
FILES_${PN}-tools-dev = "${includedir}/${BPN}"
FILES_${PN} = "${libdir}/${BPN}"

do_deploy () {
	install ${B}/efibootguard*.efi ${DEPLOYDIR}
}
addtask deploy before do_build after do_compile

DEPENDS_class-native = "zlib libcheck"
EXTRA_OECONF_class-native += "--disable-libpci"

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

BBCLASSEXTEND = "native"
