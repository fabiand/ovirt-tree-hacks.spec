Summary:        Hacks required to build a tree
Name:           ovirt-tree-hacks
Version:        1.0
Release:        0.7
License:        MIT
Group:	        System Environment/Base
Requires:       vdsm

%define see_bug echo Applying hack for bug

%define systemdunits /usr/lib/systemd/system/
%description
TBD

%prep
%setup -c -T


%build


%install
#
#
#
%see_bug https://bugzilla.redhat.com/show_bug.cgi?id=1261056
mkdir -p %{buildroot}/%{systemdunits}/vdsm-network.service.wants/
cat > %{buildroot}/%{systemdunits}/vdsm-network.service.wants/hack-bonding-defaults.service <<EOC
[Service]
ExecStart=/bin/curl -o /var/lib/vdsm/bonding-defaults.json "https://gerrit.ovirt.org/gitweb?p=vdsm.git;a=blob_plain;f=vdsm/bonding-defaults.json;hb=HEAD"
EOC

#
#
#
%see_bug https://bugzilla.redhat.com/show_bug.cgi?id=1260747
mkdir -p %{buildroot}/usr/bin
cat > %{buildroot}/usr/bin/hack-rhev-dir <<EOS
#!/bin/bash
set -x
mkdir -vp /var/lib/vdsm/rhev
chown -v vdsm:kvm /var/lib/vdsm/rhev
chattr -i /
ln -s /var/lib/vdsm/rhev /rhev
chattr +i /
EOS
chmod a+x %{buildroot}/usr/bin/hack-rhev-dir

cat > %{buildroot}/%{systemdunits}/vdsm-network.service.wants/hack-rhev-dir.service <<EOC
[Unit]
Before=vdsm-network.service

[Service]
ExecStart=/usr/bin/hack-rhev-dir
EOC

#
# Two bugs which are related to uids / nss-altfiles is not reocgnized always
#
%see_bug https://bugzilla.redhat.com/show_bug.cgi?id=1261093
%see_bug https://bugzilla.redhat.com/show_bug.cgi?id=1171291
mkdir -p %{buildroot}/usr/bin
cat > %{buildroot}/usr/bin/hack-uids <<EOS
#!/bin/bash

{ cat /etc/passwd ; egrep "qemu|kvm|vdsm|sanlock|rpc" /usr/lib/passwd ; } | sort -u > /etc/passwd_
mv -v /etc/passwd_ /etc/passwd

{ cat /etc/group ; egrep "qemu|kvm|vdsm|sanlock|rpc" /usr/lib/group ; } | sort -u > /etc/group_
mv -v /etc/group_ /etc/group

sed -i '/^\(qemu\|kvm\):/ { s/,sanlock// ; s/$/,sanlock/ }' /etc/group
EOS
chmod a+x %{buildroot}/usr/bin/hack-uids

# Run it before rpcbind which is run before vdsm
mkdir -p %{buildroot}/%{systemdunits}/rpcbind.service.wants/
cat > %{buildroot}/%{systemdunits}/rpcbind.service.wants/hack-rpc-uid.service <<EOC
[Unit]
Before=rpcbind.service

[Service]
ExecStart=/usr/bin/hack-uids
EOC


%post
# FIXME unfiled
sed -i "/Wants/ s/mom-vdsm\.service// ; /Wants/ a # mom-vdsm\.service dependency got removed" \
       %{systemdunits}/vdsmd.service


%files
/usr/bin/hack-rhev-dir
/usr/bin/hack-uids
/usr/lib/systemd/system/rpcbind.service.wants/hack-rpc-uid.service
/usr/lib/systemd/system/vdsm-network.service.wants/hack-bonding-defaults.service
/usr/lib/systemd/system/vdsm-network.service.wants/hack-rhev-dir.service


%changelog
* Tue Sep 08 2015 Fabian Deutsch <fabiand@redhat.com> - 1.0-0.1
- Initial hacks
