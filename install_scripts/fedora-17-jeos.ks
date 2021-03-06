url --url=http://mirrors.kernel.org/fedora/releases/17/Fedora/x86_64/os/
# Without the Everything repo, we cannot install cloud-init
#repo --name="fedora-everything" --baseurl=http://mirrors.kernel.org/fedora/releases/17/Everything/x86_64/os/
repo --name="fedora-everything" --mirrorlist=https://mirrors.fedoraproject.org/metalink?repo=fedora-17&arch=x86_64
install
graphical
vnc --password=${adminpw}
keyboard us
lang en_US.UTF-8
skipx
network --device eth0 --bootproto dhcp
rootpw ${adminpw}
firewall --disabled
authconfig --enableshadow --enablemd5
selinux --enforcing
timezone --utc America/New_York
bootloader --location=mbr
zerombr
clearpart --all --drives=vda

part biosboot --fstype=biosboot --size=1 --ondisk=vda
part /boot --fstype ext4 --size=200 --ondisk=vda
part pv.2 --size=1 --grow --ondisk=vda
volgroup VolGroup00 --pesize=32768 pv.2
logvol swap --fstype swap --name=LogVol01 --vgname=VolGroup00 --size=768 --grow --maxsize=1536
logvol / --fstype ext4 --name=LogVol00 --vgname=VolGroup00 --size=1024 --grow
poweroff

bootloader --location=mbr --timeout=5 --append="rhgb quiet"

%packages
@base
cloud-init

%end
