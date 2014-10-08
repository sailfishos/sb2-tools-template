%define __strip /bin/true
%define packages_in_tools  fakeroot bash bzip2 bzip2-libs coreutils db4 diffutils elfutils elfutils-libs elfutils-libelf fdupes file-libs filesystem glibc glibc-common groff libacl libattr libcap libgcc liblua libstdc++ ncurses-libs nspr nss nss-softokn-freebl pam popt readline rpm rpm rpm-build rpm-build rpm-devel rpm-libs rpm-libs sed setup sqlite tar xz-libs zlib perl perl-threads perl-threads-shared perl-Scalar-List-Utils perl-libs util-linux libblkid libuuid grep pcre scratchbox2 libsb2 gawk glib2 file net-tools glibc-devel gcc libgomp glibc-headers kernel-headers binutils cpp mpc mpfr gmp findutils cpio rpmlint-mini make m4 gzip libcap openssl-libs qemu-usermode autoconf automake ccache qtchooser qt5-qmake python python-libs zip xz doxygen qt5-tools fontconfig freetype expat cmake libarchive libcurl libxml2 libidn qt5-qtxml qt5-qtcore
%define cross_compilers   cross-armv7thl-gcc cross-armv7thl-binutils 
%global _python_bytecompile_errors_terminate_build 0
%define _target_cpu armv7thl

Name:          sb2-tools-armv7thl-inject
Version:       1.0
Release:       1
AutoReqProv:   0
BuildRequires: rpm grep tar patchelf sed
BuildRequires: %packages_in_tools
BuildRequires: %cross_compilers
ExclusiveArch: %{ix86}

# no auto requirements - they're generated
License:       BSD
Group:         Development/Tools
Summary:       SB2 cross tools

%description
This is a package providing %packages_in_tools %cross_compilers for SB2 tools directory 
It is not intended to be used in a normal system!


%package -n sb2-tools-armv7thl-dependency-inject
Summary: Dependency for sb2 host side
Group: Development/Tools

%description -n sb2-tools-armv7thl-dependency-inject
This is a package providing %packages_in_tools %cross_compilers for SB2 tools directory
It is not intended to be used in a normal system!

%prep

%build

%install

#set +x -e
mkdir -p %buildroot
rpm -ql %packages_in_tools %cross_compilers > filestoinclude1
cat > filestoignore << EOF
/etc/shadow
/etc/gshadow
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
/var/log/faillog
/var/log/tallylog
/var/lock
/var/lock/subsys
EOF
grep -vf filestoignore filestoinclude1 | sort | uniq > filestoinclude2
tar --no-recursion -T filestoinclude2 -cpf - | ( cd %buildroot && fakeroot tar -xvpf - )

sed 's|:.*$|:*:16229:0:99999:7:::|' < /etc/passwd > %{buildroot}/etc/shadow
sed 's|:.*$|:*::|' < /etc/group > %{buildroot}/etc/gshadow
chmod 0400 %buildroot/etc/shadow
chmod 0400 %buildroot/etc/gshadow

mkdir -p %buildroot/root/
mkdir -p %buildroot/var/lib/rpm/
mkdir -p %buildroot/etc/
touch %buildroot/etc/securetty
mkdir -p %buildroot/var/cache/ldconfig/
mkdir -p %buildroot/var/lock/subsys
touch %buildroot/etc/sb2-tools-template

%clean
rm -rf $RPM_BUILD_ROOT

%files -f filestoinclude2
%defattr(-,root,root)
%dir /root/
%dir /var/lib/rpm/
%dir /var/cache/ldconfig/
/etc/securetty
%verify(not md5 size mtime) %attr(0400,root,root) %config(noreplace) /etc/shadow
%verify(not md5 size mtime) %attr(0400,root,root) %config(noreplace) /etc/gshadow

%files -n sb2-tools-armv7thl-dependency-inject
%defattr(-,root,root)
/etc/sb2-tools-template
