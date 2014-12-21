#!/bin/bash

# Sets up chroot for ListHandler and InstallHandler tests, so we can test in an isolated environment
# See https://wiki.archlinux.org/index.php/DeveloperWiki:Building_in_a_Clean_Chroot#Setting_Up_A_Chroot and https://wiki.archlinux.org/index.php/Chroot#Using_chroot for more details

# Requires root
if [[ $EUID -ne 0 ]]; then
   echo "Run script as root"
   exit 1
fi

# Requires devtools package
echo "Checking for devtools package..."
pacman -Qs devtools > /dev/null
if [[ "$?" != "0" ]]; then
    echo "devtools package is required"
    exit 1
fi


CHROOT_DIR='chroot/root'

# Make chroot if it doesn't exist
if [[ ! -d "$CHROOT_DIR" ]]; then
    mkdir $CHROOT_DIR
    mkarchroot $CHROOT/root base-devel
fi

# Setup chroot for use
cd $CHROOT_DIR
mount -t proc proc proc/
mount --rbind /sys sys/
mount --rbind /dev dev/

cp /etc/resolv.conf etc/resolv.conf

# You should now be able to manually chroot in with `chroot $CHROOT_DIR /bin/bash`
