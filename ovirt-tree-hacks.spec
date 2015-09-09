Summary:        Hacks required to build a tree
Name:           ovirt-tree-hacks
Version:        1.0
Release:        0.4
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
%see_bug https://bugzilla.redhat.com/show_bug.cgi?id=1261056
mkdir -p %{buildroot}/%{systemdunits}/vdsm-network.service.d/
cat > %{buildroot}/%{systemdunits}/vdsm-network.service.d/get-bonding-defaults.conf <<EOC
[Service]
ExecStartPre=/bin/curl -o /var/lib/bonding-defaults.json "https://gerrit.ovirt.org/gitweb?p=vdsm.git;a=blob_plain;f=vdsm/bonding-defaults.json;hb=HEAD"
EOC

%see_bug https://bugzilla.redhat.com/show_bug.cgi?id=1260747
mkdir -p %{buildroot}/usr/bin
cat > %{buildroot}/usr/bin/create-rhev-dir <<EOS
mkdir -vp /var/lib/vdsm/rhev
chown -v vdsm:kvm /var/lib/vdsm/rhev
chattr -i /
ln -s /var/lib/vdsm/rhev /rhev
chattr +i /
EOS
chmod a+x %{buildroot}/usr/bin/create-rhev-dir

mkdir -p %{buildroot}/%{systemdunits}/vdsmd.service.d/
cat > %{buildroot}/%{systemdunits}/vdsmd.service.d/create-rhev-dir.conf <<EOC
[Service]
ExecStartPre=/usr/bin/create-rhev-dir
EOC

%see_bug https://bugzilla.redhat.com/show_bug.cgi?id=1261093
mkdir -p %{buildroot}/usr/bin
cat > %{buildroot}/usr/bin/sync-sanlock <<EOS
{ cat /etc/passwd ; egrep "qemu|kvm|vdsm|sanlock" /usr/lib/passwd ; } | sort -u > /etc/passwd_
mv -v /etc/passwd_ /etc/passwd

{ cat /etc/group ; egrep "qemu|kvm|vdsm|sanlock" /usr/lib/group ; } | sort -u > /etc/group_
mv -v /etc/group_ /etc/group

sed -i '/^\(qemu\|kvm\):/ s/$/,sanlock/" /etc/group
EOS
chmod a+x %{buildroot}/usr/bin/sync-sanlock

mkdir -p %{buildroot}/%{systemdunits}/vdsmd.service.d/
cat > %{buildroot}/%{systemdunits}/vdsmd.service.d/handle-sanlock-uid.conf <<EOC
[Service]
ExecStartPre=/usr/bin/sync-sanlock
EOC

%see_bug https://bugzilla.redhat.com/show_bug.cgi?id=1171291
mkdir -p %{buildroot}/%{systemdunits}/vdsm-network.service.d/
cat > %{buildroot}/%{systemdunits}/vdsmd-network.service.d/handle-rpc-uid.conf <<EOC
[Service]
ExecStartPre=/usr/bin/grep rpc /usr/lib/passwd >> /etc/passwd ; /usr/bin/grep rpc /usr/lib/group >> /etc/group
EOC

# FIXME unfiled
sed -i "/Wants/ s/mom-vdsm\.service//" \
       "/Wants/ a # mom-vdsm\.service dependency got removed" \
       /usr/lib/systemd/system/vdsmd.service


%files
/usr/bin/create-rhev-dir
/usr/bin/sync-sanlock
/usr/lib/systemd/system/vdsm-network.service.d/get-bonding-defaults.conf
/usr/lib/systemd/system/vdsmd.service.d/create-rhev-dir.conf
/usr/lib/systemd/system/vdsmd.service.d/handle-sanlock-uid.conf


%changelog
* Tue Sep 08 2015 Fabian Deutsch <fabiand@redhat.com> - 1.0-0.1
- Initial hacks
