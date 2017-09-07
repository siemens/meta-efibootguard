# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
#
# Copyright (c) 2014, Intel Corporation.
# Copyright (c) 2017, Siemens AG.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# DESCRIPTION
# This implements the 'efibootguard-efi' source plugin class for 'wic'
#
# AUTHORS
# Tom Zanussi <tom.zanussi (at] linux.intel.com>
# Claudius Heine <ch (at] denx.de>
# Andreas Reichel <andreas.reichel (at] tngtech.com>

import os
import os.path
import shutil

from wic import msger
from wic.pluginbase import SourcePlugin
from wic.utils.misc import get_custom_config
from wic.utils.oe.misc import exec_cmd, exec_native_cmd, get_bitbake_var, \
                              BOOTDD_EXTRA_SPACE

class EfibootguardEFIPlugin(SourcePlugin):
    """
    Create EFI partition.
    This plugin supports the efibootguard bootloader.
    """

    name = 'efibootguard-efi'

    @classmethod
    def do_prepare_partition(cls, part, source_params, creator, cr_workdir,
                             oe_builddir, bootimg_dir, kernel_dir,
                             rootfs_dir, native_sysroot):
        """
        Called to do the actual content population for a partition i.e. it
        'prepares' the partition to be incorporated into the image.
        In this case, prepare content for an EFI (grub) boot partition.
        """
        if not bootimg_dir:
            bootimg_dir = get_bitbake_var("HDDDIR")
            if not bootimg_dir:
                msger.error("HDDDIR not set, exiting\n")
            # just so the result notes display it
            creator.set_bootimg_dir(bootimg_dir)

        staging_kernel_dir = kernel_dir

        hdddir = "%s/hdd/%s.%s" % (cr_workdir, part.label, part.lineno)

        install_cmd = "install -d %s/EFI/BOOT" % hdddir
        exec_cmd(install_cmd)

        cp_cmd = "cp %s/EFI/BOOT/* %s/EFI/BOOT" % (bootimg_dir, hdddir)
        exec_cmd(cp_cmd, True)

        # Calculate the number of extra blocks to be sure that the
        # resulting partition image is of the wanted size

        du_cmd = "du -bks %s" % hdddir
        out = exec_cmd(du_cmd)
        blocks = int(out.split()[0])

        extra_blocks = part.get_extra_block_count(blocks)

        if extra_blocks < BOOTDD_EXTRA_SPACE:
            extra_blocks = BOOTDD_EXTRA_SPACE

        blocks += extra_blocks

        msger.debug("Added %d extra blocks to %s to get to %d total blocks" % \
                    (extra_blocks, part.mountpoint, blocks))

        # dosfs image, created by mkdosfs
        efiimg = "%s/%s.%s.img" % (cr_workdir, part.label, part.lineno)

        dosfs_cmd = "mkdosfs -n %s -C %s %d" % (part.label.upper(), efiimg, blocks)
        exec_native_cmd(dosfs_cmd, native_sysroot)

        mcopy_cmd = "mcopy -i %s -s %s/* ::/" % (efiimg, hdddir)
        exec_native_cmd(mcopy_cmd, native_sysroot)

        chmod_cmd = "chmod 644 %s" % efiimg
        exec_cmd(chmod_cmd)

        du_cmd = "du -Lbks %s" % efiimg
        out = exec_cmd(du_cmd)
        efiimg_size = out.split()[0]

        part.size = int(efiimg_size)
        part.source_file = efiimg
