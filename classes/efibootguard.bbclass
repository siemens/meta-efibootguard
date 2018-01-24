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

# Set EFI_PROVIDER = "efibootguard" to use efibootguard on your live images instead of grub-efi
# (images built by image-live.bbclass or image-vm.bbclass)

do_bootimg[depends] += "${MLPREFIX}efibootguard:do_deploy"
do_bootimg[depends] += "${MLPREFIX}efibootguard-native:do_deploy"
do_bootdirectdisk[depends] += "${MLPREFIX}efibootguard:do_deploy"

EFIDIR = "/EFI/BOOT"

inherit fs-uuid
inherit logging

efi_populate() {
        DEST=$1
        if [ "${TARGET_ARCH}" = "i586" ]; then
            EFI_IMAGE="efibootguardia32.efi"
            DEST_EFI_IMAGE="bootia32.efi"
        elif [ "${TARGET_ARCH}" = "x86_64" ]; then
            EFI_IMAGE="efibootguardx64.efi"
            DEST_EFI_IMAGE="bootx64.efi"
        else
            bbfatal "Invalid target architecture for efibootguard: ${TARGET_ARCH}. Only i586 and x86_64 are supported."
        fi
        install -d ${DEST}${EFIDIR}
        install -m 0644 ${DEPLOY_DIR_IMAGE}/${EFI_IMAGE} ${DEST}${EFIDIR}/${DEST_EFI_IMAGE}
}

efi_iso_populate() {
        # Code copied from gummiboot.bbclass
        iso_dir=$1
        efi_populate $iso_dir
        mkdir -p ${EFIIMGDIR}/${EFIDIR}
        cp $iso_dir/${EFIDIR}/* ${EFIIMGDIR}${EFIDIR}
        cp $iso_dir/vmlinuz ${EFIIMGDIR}
        EFIPATH=$(echo "${EFIDIR}" | sed 's/\//\\/g')
        echo "fs0:${EFIPATH}\\${DEST_EFI_IMAGE}" > ${EFIIMGDIR}/startup.nsh
        if [ -f "$iso_dir/initrd" ] ; then
            cp $iso_dir/initrd ${EFIIMGDIR}
        fi
}

efi_hddimg_populate() {
        efi_populate $1
}

python build_efi_cfg() {
        # This function is expected by image-live.bbclass
        # If an iso is built for example as rescue medium, we only have one filesystem with efibootguard
        # So a boot configuration is needed on this iso file system.
        from subprocess import Popen, PIPE

        skipiso = d.getVar("NOISO", True)
        if not skipiso == "1":
            bb.note("Generating iso default boot configuration.")
            isodir = os.path.join(d.getVar("S", True), "iso")
            bindir_native = d.getVar("STAGING_BINDIR_NATIVE", True);
            bg_setenv_cmd = os.path.join(bindir_native, "bg_setenv")
            olddir = os.getcwd()

            make_isodir_cmd = ["mkdir", "-p", isodir]
            p = Popen(make_isodir_cmd)
            (out, err) = p.communicate()
            if not p.returncode == 0:
                bb.fatal("Could not create isodir: %s" % isodir)
            os.chdir(isodir)
            p = Popen([bg_setenv_cmd, "--file", "--kernel=vmlinuz", "--watchdog=30"], \
                       stdout=PIPE, stderr=PIPE)
            (out, err) = p.communicate()
            os.chdir(olddir)
            if not p.returncode == 0:
                bb.fatal("Could not execute bg_setenv. Please make sure efibootguard-native is installed.")

            bb.debug(2, "bg_setenv returned %s %s" % (out, err))

        else:
            bb.debug(2, "No iso built, no default boot configuration.")
}
