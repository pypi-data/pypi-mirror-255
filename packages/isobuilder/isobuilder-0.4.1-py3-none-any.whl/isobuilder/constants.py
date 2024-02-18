AUTHORIZED_KEYS = '''ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDwYgIyxyeI9kkxQuO0unybG6dmuMmARJSjew+Ue6HlCLEh7RjE2G3mMywztk7EKXrIs93leBacp2l2PrUp0HkijH4IreAsMh81P56UPLWAfsWoU3UfYGJw1OFAPCIaWCyCegKfaB9DcIi3NXWtI0t7gcPgnmhDMVxmqinZ9+eYKy79Vt5iK8cLJzedsSAjmV2R9Q7JS6Ic6IV0Rj0GzwPBbI+gJenGUE0oLAmZfSAYJFMvBhKk6HrIp4zMVbnKinGoN4HkxeeP+oqyiJIqRWP8hhyKJoeHZ7a94TSRG1TEg1v6SEoDgqLXojC6b1mZpt0uN616gEbvOpC6B4xXHcAr peadmin@master1'''  # noqa

ISOLINUX_CFG = '''serial 1 115200
include menu.cfg
default menu.c32
prompt 1
timeout 50'''


TXT_CFG = '''label dnsops
  menu label ^DNS Engineering Base System
  kernel /install/vmlinuz
  append  auto=true priority=critical initrd=/install/initrd.gz ramdisk_size=16384 root=/dev/ram rw console=ttyS1,115200n8 file=/cdrom/preseed/dnsops.seed ---
label memtest
  menu label Test ^memory
  kernel /install/mt86plus
label hd
  menu label ^Boot from first hard disk
  localboot 0x80'''  # noqa

GRUB = '''GRUB_DEFAULT=0
GRUB_TIMEOUT=3
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
GRUB_CMDLINE_LINUX_DEFAULT=""
GRUB_CMDLINE_LINUX="rootdelay=90 console=tty0 console=ttyS1,115200n8"
GRUB_TERMINAL=serial
GRUB_SERIAL_COMMAND="serial --speed=115200 --unit=1 --word=8 --parity=no --stop=1" '''

GRUB_CFG = '''
if loadfont /boot/grub/font.pf2 ; then
        set gfxmode=auto
        insmod efi_gop
        insmod efi_uga
        insmod gfxterm
        terminal_output gfxterm
fi
serial --speed=115200 --unit=1 --word=8 --parity=no --stop=1
terminal_input serial
terminal_output serial
set menu_color_normal=white/black
set menu_color_highlight=black/light-gray
set timeout=5

menuentry "Install Ubuntu Server" {
        set gfxpayload=keep
        linux   /install/vmlinuz critical ramdisk_size=16384 root=/dev/ram locale=en_US ipv6.disable=1 file=/cdrom/preseed/dnsops.seed console=ttyS1,115200n8 ---
        initrd  /install/initrd.gz
}

menuentry "Rescue a broken system" {
        set gfxpayload=keep
        linux   /install/vmlinuz  rescue/enable=true ---
        initrd  /install/initrd.gz
}
grub_platform
if [ "$grub_platform" = "efi" ]; then
menuentry 'Boot from next volume' {
        exit
}
menuentry 'UEFI Firmware Settings' {
        fwsetup
}
fi
'''  # noqa
PRESEED = '''d-i netcfg/get_hostname string {hostname}
d-i preseed/early_command string umount /media
d-i debian-installer/locale string en_US
d-i debian-installer/language string en
d-i debian-installer/country string US
d-i keyboard-configuration/xkb-keymap select us
d-i preseed/locale string en_US
d-i netcfg/disable_autoconfig boolean true
d-i netcfg/disable_dhcp boolean true
d-i netcfg/choose_interface string {interface}
d-i netcfg/get_ipaddress string {ipaddress}
d-i netcfg/get_netmask string {netmask}
d-i netcfg/get_gateway string {gateway}
d-i netcfg/get_domain string {domain}
d-i netcfg/get_nameservers string 8.8.8.8
d-i netcfg/confirm_static boolean true
d-i netcfg/wireless_wep string
d-i cdrom-detect/cdrom_device string /dev/sr1
d-i mirror/http/proxy string
d-i mirror/http/hostname string prod.mirror.dns.icann.org
d-i mirror/http/directory string /repos/main/ubuntu/
d-i clock-setup/utc boolean true
d-i time/zone string UTC
d-i clock-setup/ntp boolean true
d-i base-installer/kernel/image string linux-server
d-i passwd/root-login boolean true
d-i passwd/root-password-crypted password {password}
d-i passwd/make-user boolean false
d-i user-setup/encrypt-home boolean false
d-i pkgsel/include string openssh-server curl
d-i pkgsel/upgrade select none
d-i pkgsel/update-policy select none
d-i grub-installer/only_debian boolean true
d-i grub-installer/with_other_os boolean true
d-i finish-install/reboot_in_progress note
d-i cdrom-detect/eject boolean false
d-i preseed/late_command string {late_command}
d-i partman-auto/disk string /dev/sda
d-i partman/unmount_active boolean true
d-i partman-auto/purge_lvm_from_device boolean true
d-i partman-auto/method string lvm
d-i partman-lvm/device_remove_lvm boolean true
d-i partman-auto-lvm/new_vg_name string vg_lroot
d-i partman-md/device_remove_md boolean true
d-i partman-lvm/confirm boolean true
d-i partman-lvm/confirm_nooverwrite boolean true
d-i partman-auto/expert_recipe string \\
dell_scheme ::          \\
  1 1 1 free                              \\
     $bios_boot{{ }}                        \\
     method{{ biosgrub }} .                 \\
  200 200 200 fat32                       \\
     $primary{{ }}                          \\
     method{{ efi }} format{{ }} .            \\
  4096 1100 4096 ext4     \\
    $primary{{ }} $bootable{{ }}  \\
    method{{ format }} format{{ }}  \\
    use_filesystem{{ }}   \\
    filesystem{{ ext4 }}    \\
    mountpoint{{ / }}     \\
  .         \\
  4096 4096 4096 linux-swap   \\
    method{{ swap }} format{{ }}  \\
  .         \\
  2000 2200 2400 ext4     \\
    $lvmok{{ }} \\
    method{{ format }} format{{ }}  \\
    use_filesystem{{ }}   \\
    filesystem{{ ext4 }}    \\
    mountpoint{{ /tmp }}    \\
  .         \\
  4096 2200 4096 ext4     \\
    $lvmok{{ }} \\
    method{{ format }} format{{ }}  \\
    use_filesystem{{ }}   \\
    filesystem{{ ext4 }}    \\
    mountpoint{{ /usr }}    \\
  .         \\
  4096 2200 4096 ext4     \\
    $lvmok{{ }} \\
    method{{ format }} format{{ }}  \\
    use_filesystem{{ }}   \\
    filesystem{{ ext4 }}    \\
    mountpoint{{ /var }}    \\
  .         \\
  4096 2200 26624 ext4      \\
    $lvmok{{ }} \\
    method{{ format }} format{{ }}  \\
    use_filesystem{{ }}   \\
    filesystem{{ ext4 }}    \\
    mountpoint{{ /opt }}    \\
  .
d-i partman-partitioning/confirm_write_new_label boolean true
d-i partman/choose_partition select Finish partitioning and write changes to disk
d-i partman/confirm boolean true
d-i partman/confirm_nooverwrite boolean true
tasksel tasksel/first multiselect openssh-server
'''

LATE_COMMAND = f"""echo {{hostname}} > /target/etc/hostname; \
mkdir -p /target/root/.ssh; \
cp /cdrom/dnsops/grub /target/etc/default/; \
echo "{AUTHORIZED_KEYS}" > /target/root/.ssh/authorized_keys; \
chmod 0600 /target/root/.ssh/authorized_keys; \
chmod 0700 /target/root/.ssh; \
echo "net.ipv6.conf.all.accept_ra = 0" >/target/etc/sysctl.d/net.ipv6.conf.all.accept_ra.conf; \
echo "net.ipv6.conf.default.accept_ra = 0" \
    >/target/etc/sysctl.d/net.ipv6.conf.default.accept_ra.conf; \
echo "net.ipv6.conf.{{ipv6_primary}}.accept_ra = 0" \
    >/target/etc/sysctl.d/net.ipv6.conf.interface.accept_ra.conf; \
echo "precedence ::ffff:0:0/96 100" >/target/etc/gai.conf; \
in-target update-grub
"""
