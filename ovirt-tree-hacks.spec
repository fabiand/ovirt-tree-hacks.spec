Summary:        Hacks required to build a tree
Name:           ovirt-tree-hacks
Version:        1.0
Release:        0.1
License:        MIT
Group:	        System Environment/Base

%define see_bug echo Applying hack for bug

%description
TBD

%prep
%setup -c -T


%build


%install


%post
%see_bug https://bugzilla.redhat.com/show_bug.cgi?id=1260747
mkdir -vp %{_sharedstatedir}/rhev
rmdir -v /rhev
ln -s /rhev %{_sharedstatedir}/rhev

%see_bug https://bugzilla.redhat.com/show_bug.cgi?id=1171291
grep rpc /usr/lib/passwd >> /etc/passwd
grep rpc /usr/lib/group >> /etc/group

# FIXME unfiled
sed -i "/Wants/ s/mom-vdsm\.service//" \
       "/Wants/ a # mom-vdsm\.service dependency got removed" \
       /usr/lib/systemd/system/vdsmd.service


%files


%changelog
* Tue Sep 08 2015 Fabian Deutsch <fabiand@redhat.com> - 1.0-0.1
- Initial hacks
