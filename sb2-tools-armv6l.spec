%define __strip /bin/true
%define architecture_target armv6l
%define _build_name_fmt    %%{ARCH}/%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.dontuse.rpm
%define packages_in_tools  fakeroot bash bzip2 bzip2-libs coreutils db4 diffutils elfutils elfutils-libs elfutils-libelf fdupes file-libs filesystem glibc glibc-common groff libacl libattr libcap libgcc liblua libstdc++ ncurses-libs nspr nss nss-softokn-freebl pam popt readline rpm rpm rpm-build rpm-build rpm-devel rpm-libs rpm-libs sed setup sqlite tar xz-libs zlib perl perl-threads perl-threads-shared perl-Scalar-List-Utils perl-libs util-linux libblkid libuuid grep pcre scratchbox2 libsb2 gawk glib2 file net-tools glibc-devel gcc libgomp glibc-headers kernel-headers binutils cpp mpc mpfr gmp findutils cpio rpmlint-mini make m4 gzip libcap openssl-libs qemu-usermode autoconf automake ccache python python-libs zip xz doxygen fontconfig freetype expat cmake libarchive libcurl libxml2 libidn libicu libicu52 libmount libsmartcols
%define cross_compilers   cross-armv6l-gcc cross-armv6l-binutils 
%global _python_bytecompile_errors_terminate_build 0

Name:          sb2-tools-armv6l
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


%package dependency
Summary: Dependency for sb2 host side
Group: Development/Tools

%description dependency
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

shellquote()
{
    for arg; do
        arg=${arg//\\/\\\\}
#        arg=${arg//\$/\$}   # already needs quoting ;(
#        arg=${arg/\"/\\\"}  # dito
#        arg=${arg//\`/\`}   # dito
        arg=${arg//\\ |/\|}
        arg=${arg//\\|/|}
        echo "$arg"
    done
}

echo "Creating baselibs_new.conf"
echo ""
rm -rRf /tmp/baselibs_new.conf || true
shellquote "arch i486 targets armv6l:inject" >> /tmp/baselibs_new.conf
shellquote "%{name}" >> /tmp/baselibs_new.conf
shellquote "  targettype x86 block!" >> /tmp/baselibs_new.conf
shellquote "  targettype 32bit block!" >> /tmp/baselibs_new.conf
shellquote "  targettype inject autoreqprov off" >> /tmp/baselibs_new.conf
shellquote "  targettype inject extension -inject" >> /tmp/baselibs_new.conf
shellquote "  targettype inject +/" >> /tmp/baselibs_new.conf
shellquote "  targettype inject -%{_mandir}" >> /tmp/baselibs_new.conf
shellquote "  targettype inject -%{_docdir}" >> /tmp/baselibs_new.conf
shellquote "  targettype inject config    -/sb2-config$" >> /tmp/baselibs_new.conf

shellquote "arch i486 targets armv6l:inject" >> /tmp/baselibs_new.conf
shellquote "%{name}-dependency" >> /tmp/baselibs_new.conf
shellquote "  targettype x86 block!" >> /tmp/baselibs_new.conf
shellquote "  targettype 32bit block!" >> /tmp/baselibs_new.conf
shellquote "  targettype inject autoreqprov off" >> /tmp/baselibs_new.conf
shellquote "  targettype inject extension -inject" >> /tmp/baselibs_new.conf
shellquote "  targettype inject +/" >> /tmp/baselibs_new.conf
shellquote "  targettype inject -%{_mandir}" >> /tmp/baselibs_new.conf
shellquote "  targettype inject -%{_docdir}" >> /tmp/baselibs_new.conf
shellquote "  targettype inject config    -/sb2-config$" >> /tmp/baselibs_new.conf

cat /tmp/baselibs_new.conf > %{_sourcedir}/baselibs.conf
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

%files dependency
%defattr(-,root,root)
/etc/sb2-tools-template
