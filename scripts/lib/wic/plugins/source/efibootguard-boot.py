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
# This implements the 'efibootguard-boot' source plugin class for 'wic'
#
# AUTHORS
# Tom Zanussi <tom.zanussi (at] linux.intel.com>
# Claudius Heine <ch (at] denx.de>
# Andreas Reichel <andreas.reichel (at] tngtech.com>

import os
import logging

from wic import WicError
from wic.pluginbase import SourcePlugin
from wic.engine import get_custom_config
from wic.misc import exec_cmd, exec_native_cmd, get_bitbake_var, \
                     BOOTDD_EXTRA_SPACE

msger = logging.getLogger('wic')

class EfibootguardBootPlugin(SourcePlugin):
    """
    Create boot partition.
    This plugin supports efibootguard bootloader.
    """

    name = 'efibootguard-boot'

    @classmethod
    def _get_kernel_params(cls, source_params):
        kernel_src = source_params.get("kernel", get_bitbake_var("KERNEL_IMAGETYPE"))
        if ";" in kernel_src:
            kernel_src, kernel_dst = kernel_src.split(";", 1)
        else:
            kernel_dst = kernel_src

        return kernel_src, kernel_dst

    @classmethod
    def do_configure_partition(cls, part, source_params, creator, cr_workdir,
                               oe_builddir, bootimg_dir, kernel_dir,
                               native_sysroot):
        """
        Called before do_prepare_partition(), creates loader-specific config
        """
        hdddir = "%s/hdd/%s.%s" % (cr_workdir, part.label, part.lineno)

        install_cmd = "install -d %s" % hdddir
        exec_cmd(install_cmd)

        bootloader = creator.ks.bootloader

        cmdline = "root=%s %s\n" % \
                   (creator.rootdev, bootloader.append)

        _, kernel_dst = cls._get_kernel_params(source_params)

        cwd = os.getcwd()
        os.chdir(hdddir)
        config_cmd = 'bg_setenv -f . -k "C:%s:%s" -a "%s" -r %s -w %s' % \
                      (part.label.upper(), \
                       kernel_dst, \
                       cmdline.strip(), \
                       source_params.get("revision", 1), \
                       source_params.get("watchdog", 5))

        exec_native_cmd(config_cmd, native_sysroot)
        os.chdir(cwd)

    @classmethod
    def do_prepare_partition(cls, part, source_params, creator, cr_workdir,
                             oe_builddir, bootimg_dir, kernel_dir,
                             rootfs_dir, native_sysroot):
        """
        Called to do the actual content population for a partition i.e. it
        'prepares' the partition to be incorporated into the image.
        In this case, prepare content for an EFI (grub) boot partition.
        """
        if not kernel_dir:
            kernel_dir = get_bitbake_var("DEPLOY_DIR_IMAGE")
            if not kernel_dir:
                raise WicError("DEPLOY_DIR_IMAGE not set, exiting\n")

        staging_kernel_dir = kernel_dir

        hdddir = "%s/hdd/%s.%s" % (cr_workdir, part.label, part.lineno)

        kernel_src, kernel_dst = cls._get_kernel_params(source_params)

        install_cmd = "install -m 0644 %s/%s %s/%s" % \
            (staging_kernel_dir, kernel_src, hdddir, kernel_dst)
        exec_cmd(install_cmd)

        # Write label as utf-16le to EFILABEL file
        fd = open("%s/EFILABEL" % hdddir, 'wb')
        fd.write(part.label.upper().encode("utf-16le"))
        fd.close()

        # Copy the specified initrd to the BOOT partition
        initrd = source_params.get('initrd')

        if initrd:
            cp_cmd = "cp %s/%s %s" % (kernel_dir, initrd, hdddir)
            exec_cmd(cp_cmd, True)

        else:
            msger.debug("Ignoring missing initrd")

        du_cmd = "du -bks %s" % hdddir
        out = exec_cmd(du_cmd)
        blocks = int(out.split()[0])

        # Calculate number of extra blocks to be sure that the resulting
        # partition image has the wanted size.
        extra_blocks = part.get_extra_block_count(blocks)

        if extra_blocks < BOOTDD_EXTRA_SPACE:
            extra_blocks = BOOTDD_EXTRA_SPACE

        blocks += extra_blocks

        msger.debug("Added %d extra blocks to %s to get to %d total blocks" % \
                    (extra_blocks, part.mountpoint, blocks))

        # dosfs image, created by mkdosfs
        bootimg = "%s/%s.%s.img" % (cr_workdir, part.label, part.lineno)

        dosfs_cmd = "mkdosfs -F 16 -n %s -C %s %d" % (part.label.upper(), \
                    bootimg, blocks) 

        exec_native_cmd(dosfs_cmd, native_sysroot)

        mcopy_cmd = "mcopy -i %s -s %s/* ::/" % (bootimg, hdddir)
        exec_native_cmd(mcopy_cmd, native_sysroot)

        chmod_cmd = "chmod 644 %s" % bootimg
        exec_cmd(chmod_cmd)

        du_cmd = "du -Lbks %s" % bootimg
        out = exec_cmd(du_cmd)
        bootimg_size = out.split()[0]

        part.size = int(bootimg_size)
        part.source_file = bootimg
