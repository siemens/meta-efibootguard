DEPENDS += "efibootguard-native"
DEPENDS += "${@'efibootguard' if d.getVar('EFI_PROVIDER') == 'efibootguard' else ''}"
