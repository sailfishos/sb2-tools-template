%define __strip /bin/true
%define packages_in_tools autoconf automake bash binutils bzip2 bzip2-libs ccache cmake coreutils cpio cpp db4 diffutils doxygen elfutils elfutils-libelf elfutils-libs expat fakeroot fdupes file file-libs filesystem findutils fontconfig freetype gawk gcc glib2 glibc glibc-common glibc-devel glibc-headers gmp grep groff gzip kernel-headers libacl libarchive libattr libblkid libcap libcap libcurl libgcc libgcrypt libgomp libgpg-error libicu libicu52 libidn liblua libmount libsb2 libsmartcols libstdc++ libuuid libxml2 m4 make mpc mpfr ncurses-libs net-tools nspr nss nss-softokn-freebl openssl-libs pam pcre perl perl-libs perl-Scalar-List-Utils perl-threads perl-threads-shared popt python python-libs qemu-usermode qt5-qmake qt5-qtcore qt5-qtxml qt5-tools qtchooser readline rpm rpm-build rpm-devel rpm-libs rpmlint-mini scratchbox2 sed setup sqlite systemd-libs tar util-linux xz xz-libs zip zlib

%define cross_compilers   cross-armv7tnhl-gcc cross-armv7tnhl-binutils 
%global _python_bytecompile_errors_terminate_build 0
%define _target_cpu armv7tnhl

Name:          sb2-tools-armv7tnhl-inject
Version:       1.0
Release:       1
AutoReqProv:   0
BuildRequires: rpm grep tar patchelf sed
BuildRequires: %packages_in_tools
BuildRequires: %cross_compilers


# no auto requirements - they're generated
License:       BSD
Group:         Development/Tools
Summary:       SB2 cross tools

%description
This is a package providing %packages_in_tools %cross_compilers for SB2 tools directory 
It is not intended to be used in a normal system!


%package -n sb2-tools-armv7tnhl-dependency-inject
Summary: Dependency for sb2 host side
Group: Development/Tools

%description -n sb2-tools-armv7tnhl-dependency-inject
This is a package providing %packages_in_tools %cross_compilers for SB2 tools directory
It is not intended to be used in a normal system!

%prep

%build

%install

#set +x -e
mkdir -p %buildroot
rpm -ql %packages_in_tools %cross_compilers > filestoinclude1
#/var/log contains lots of random data we don't need
sed -i -e '/\/var\/log/d' filestoinclude1
cat > filestoignore << EOF
/etc/shadow
/etc/gshadow
/etc/mtab
/usr/share/man
/root
/var/lib/rpm
/usr/bin/chfn
/usr/bin/chsh
/etc/securetty
/var/cache/ldconfig
/usr/libexec/pt_chown
/usr/lib/locale/locale-archive
/usr/sbin/build-locale-archive
/usr/sbin/tzdata-update
/etc/security/opasswd
/sbin/unix_update
/var/lock
/var/lock/subsys
EOF
grep -vf filestoignore filestoinclude1 | sort | uniq > filestoinclude2
tar --no-recursion -T filestoinclude2 -cpf - | ( cd %buildroot && fakeroot tar -xvpf - )
sed -i "s/^\(.*\)$/\"\1\"/g" filestoinclude2
cat filestoinclude2
sed 's|:.*$|:*:16229:0:99999:7:::|' < /etc/passwd > %{buildroot}/etc/shadow
sed 's|:.*$|:*::|' < /etc/group > %{buildroot}/etc/gshadow
chmod 0400 %buildroot/etc/shadow
chmod 0400 %buildroot/etc/gshadow
mkdir -p %buildroot/var/log
mkdir -p %buildroot/root/
mkdir -p %buildroot/var/lib/rpm/
mkdir -p %buildroot/etc/
touch %buildroot/etc/securetty
mkdir -p %buildroot/var/cache/ldconfig/
mkdir -p %buildroot/var/lock/subsys
#overwite hosts file to avoid getting a random hostname
cat > %{buildroot}/etc/hosts << EOF
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
EOF
touch %buildroot/etc/sb2-tools-template

%clean
rm -rf $RPM_BUILD_ROOT

%files -f filestoinclude2
%defattr(-,root,root)
%dir /var/log
%dir /root/
%dir /var/lib/rpm/
%dir /var/cache/ldconfig/
/etc/securetty
%verify(not md5 size mtime) %attr(0400,root,root) %config(noreplace) /etc/shadow
%verify(not md5 size mtime) %attr(0400,root,root) %config(noreplace) /etc/gshadow

%files -n sb2-tools-armv7tnhl-dependency-inject
%defattr(-,root,root)
/etc/sb2-tools-template
