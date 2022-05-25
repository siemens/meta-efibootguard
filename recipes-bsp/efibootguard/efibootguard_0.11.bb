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

LICENSE = "GPL-2.0-only"
LIC_FILES_CHKSUM = "file://COPYING;md5=b234ee4d69f5fce4486a80fdaf4a4263"
SUMMARY = "A bootloader based on UEFI"

SRC_URI = "gitsm://github.com/siemens/efibootguard.git;protocol=https;branch=master"
SRCREV = "eda1b987f8ca41d64b46f53347a8c89c6fc03c31"

S = "${WORKDIR}/git"

DEPENDS:class-target = "gnu-efi pciutils zlib libcheck"

inherit autotools deploy pkgconfig

COMPATIBLE_HOST = "(x86_64.*|i.86.*)-linux"

PACKAGES =+ " \
    ${PN}-kernel-stub \
    ${PN}-tools \
    ${PN}-tools-secure-boot \
    ${PN}-tools-bash-completion \
    ${PN}-tools-zsh-completion \
"

EXTRA_OECONF = "--with-gnuefi-sys-dir=${STAGING_DIR_HOST} \
                --with-gnuefi-include-dir=${STAGING_INCDIR}/efi \
                --with-gnuefi-lib-dir=${STAGING_LIBDIR}"

FILES:${PN}-tools-bash-completion = " \
    ${datadir}/bash-completion \
"
RDEPENDS:${PN}-tools-bash-completion = "bash-completion"

FILES:${PN}-tools-zsh-completion = " \
    ${datadir}/zsh/site-functions \
"

SUMMARY:${PN}-tools = "User space utilities bg_printenv bg_setenv"
FILES:${PN}-tools = " \
    ${bindir}/bg_printenv \
    ${bindir}/bg_setenv \
"

SUMMARY:${PN}-tools-secure-boot = "Helper utility to create unified kernel images"
FILES:${PN}-tools-secure-boot = " \
    ${bindir}/bg_gen_unified_kernel \
"
RDEPENDS:${PN}-tools-secure-boot += "python3-core"

FILES:${PN}-staticdev = "${libdir}/lib*.a"
FILES:${PN}-dev = " \
    ${includedir}/${BPN} \
    ${libdir}/libebgenv.so \
    ${libdir}/pkgconfig/*.pc \
"

SUMMARY:${PN}-kernel-stub = "A simple UEFI stub which allows to form unified kernel images"
FILES:${PN}-kernel-stub += "${libdir}/efibootguard/kernel-stub*.efi"

FILES:${PN} += " \
    ${libdir}/libebgenv-${PV}*.so \
"

do_deploy () {
	install ${B}/efibootguard*.efi ${DEPLOYDIR}
}
addtask deploy before do_build after do_compile

DEPENDS:class-native = "zlib-native libcheck-native"
EXTRA_OECONF:class-native = "--with-gnuefi-sys-dir=${STAGING_DIR_HOST} \
                             --with-gnuefi-include-dir=${STAGING_INCDIR}/efi \
                             --with-gnuefi-lib-dir=${STAGING_LIBDIR} \
                             --disable-bootloader"

do_compile:class-native () {
	oe_runmake bg_setenv
}

do_install:class-native () {
	install -d ${D}${bindir}/
	install -m755 ${B}/bg_setenv ${D}${bindir}/
	ln -s bg_setenv ${D}${bindir}/bg_printenv
}

do_install:append() {
    # Fix bash-completion path
    if [ -d ${D}/${datadir}/${BPN}/completion/bash ]; then
        install -d ${D}/${datadir}/bash-completion/completions
        mv ${D}/${datadir}/${BPN}/completion/bash/bg_printenv.bash ${D}/${datadir}/bash-completion/completions/bg_printenv
        mv ${D}/${datadir}/${BPN}/completion/bash/bg_setenv.bash ${D}/${datadir}/bash-completion/completions/bg_setenv
        rm -rf ${D}/${datadir}/${BPN}/completion/bash
    fi

    # Fix zsh-completion path
    if [ -d ${D}/${datadir}/${BPN}/completion/zsh ]; then
        install -d ${D}/${datadir}/zsh/site-functions
        mv ${D}/${datadir}/${BPN}/completion/zsh/_bg_printenv ${D}/${datadir}/zsh/site-functions/_bg_printenv
        mv ${D}/${datadir}/${BPN}/completion/zsh/_bg_setenv ${D}/${datadir}/zsh/site-functions/_bg_setenv
        rm -rf ${D}/${datadir}/${BPN}/completion/zsh
    fi
}

do_deploy:class-native () {
}

BBCLASSEXTEND = "native"
