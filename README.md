# EFI Boot Guard meta layer #

A meta-layer for integration of `efibootguard` into a yocto project.

## Development ##

Mailing list:
[efibootguard-dev@googlegroups.com](efibootguard-dev@googlegroups.com)

Archive:
[https://www.mail-archive.com/efibootguard-dev@googlegroups.com](https://www.mail-archive.com/efibootguard-dev@googlegroups.com)

## Current status ##

Tested with:

poky (rocko): 342fbd6a3e57021c8e28b124b3adb241936f3d9d
https://git.yoctoproject.org/git/poky

meta-intel: 7bf03f7612834142355189c46ccdb4b309acc58a
https://git.yoctoproject.org/git/meta-intel

meta-openembedded: 8cef6b38e62e6c79ec857510df454cefc868b0df
http://git.openembedded.org/meta-openembedded

## project integration ##

Steps:

1. Include this meta layer into your project

2. Set `EFI_PROVIDER` to "efibootguard" in your local.conf or in your
   `conf/machine/<MACHINE>.conf`:
```
EFI_PROVIDER="efibootguard"
```

3. Provide a project-specific .wks file using the python source plugins
   of this layer for image creation

4. Build the roots and the hdd image using the new .wks file

## Example .wks file ##

```
# short-description: Create a bootable disk image with efibootguard
# long-description: Creates a partitioned EFI disk image,
# using efibootguard, that the user can directly dd to boot media.

# EFI partition containing efibootguard
part --source efibootguard-efi --size 32 --extra-space 0 --overhead-factor 1 --ondisk mmcblk0 --label efi --part-type=EF00 --align 1024

# Two root partitions for updateability, leave away 2nd if not used
part / --source rootfs --size 1024 --extra-space 0 --overhead-factor 1 --ondisk mmcblk0 --fstype=ext4 --label platform0 --align 1024
part --source rootfs --size 1024 --extra-space 0 --overhead-factor 1 --ondisk mmcblk0 --fstype=ext4 --label plaftorm1 --align 1024

# Two config partitions to load boot configuration and kernel
part --source efibootguard-boot --size 32 --extra-space 0 --overhead-factor 1 --ondisk mmcblk0 --label boot0 --align 1024 --part-type=0700 --sourceparams "watchdog=60,revision=2"
part --source efibootguard-boot --size 32 --extra-space 0 --overhead-factor 1 --ondisk mmcblk0 --label boot1 --align 1024 --part-type=0700 --sourceparams "watchdog=60,revision=1"

# Other partitions
part --size 1024 --extra-space 0 --overhead-factor 1 --ondisk mmcblk0 --label persistent --align 1024 --fstype=ext4
part swap --ondisk mmcblk0 --size 512 --fstype=swap --label swap --align 1024

# Important for type of partition table
bootloader --ptable gpt --append="console=ttyS1,115200n8 reboot=efi,warm rw debugshell=5 rootwait"
```

*NOTE*: The `--append` option to the bootloader gives kernel parameters that are written into the efibootguard environment file.
