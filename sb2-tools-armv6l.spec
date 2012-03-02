%define __strip /bin/true
%define architecture_target armv6l
%define _build_name_fmt    %%{ARCH}/%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.dontuse.rpm
%define packages_in_tools  fakeroot bash bzip2 bzip2-libs coreutils db4 diffutils elfutils elfutils-libs elfutils-libelf fdupes file-libs filesystem glibc glibc-common groff libacl libattr libcap libgcc liblua libstdc++ ncurses-libs nspr nss nss-softokn-freebl pam popt readline rpm rpm rpm-build rpm-build rpm-devel rpm-libs rpm-libs sed setup sqlite tar xz-libs zlib perl perl-libs util-linux libblkid libuuid grep pcre scratchbox2 gawk glib2 file net-tools glibc-devel gcc libgomp glibc-headers kernel-headers binutils cpp mpc mpfr gmp findutils cpio rpmlint-mini make m4 gzip libcap qemu-usermode autoconf automake
%define cross_compilers   cross-armv6l-gcc cross-armv6l-binutils 

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

%prep

%build

%install

set +x
mkdir -p %buildroot
rpm -ql %packages_in_tools %cross_compilers > filestoinclude1
cat > filestoignore << EOF
/usr/share/man
/root
/var/lib/rpm
/usr/bin/chfn
/usr/bin/chsh
/etc/securetty
/var/cache/ldconfig
/usr/libexec/pt_chown
/usr/sbin/build-locale-archive
/usr/sbin/tzdata-update
/etc/security/opasswd
/sbin/unix_update
/var/log/faillog
/var/log/tallylog
EOF
rpm -ql glibc | grep /usr/sbin/glibc_post_upgrade >> filestoignore
grep -vf filestoignore filestoinclude1 | sort | uniq > filestoinclude2
tar --no-recursion -T filestoinclude2 -cpf - | ( cd %buildroot && fakeroot tar -xvpf - )

mkdir -p %buildroot/root/
mkdir -p %buildroot/var/lib/rpm/
mkdir -p %buildroot/etc/
touch %buildroot/etc/securetty
mkdir -p %buildroot/var/cache/ldconfig/

shellquote()
{
    for arg; do
        arg=${arg//\\/\\\\}
#        arg=${arg//\$/\$}   # already needs quoting ;(
#        arg=${arg/\"/\\\"}  # dito
#        arg=${arg//\`/\`}   # dito
        arg=${arg//\\|/\|}
        arg=${arg//\\|/|}
        echo "$arg"
    done
}

echo "Creating baselibs_new.conf"
echo ""
rm -rRf /tmp/baselibs_new.conf || true
shellquote "arch i586 targets armv6l:inject" >> /tmp/baselibs_new.conf
shellquote "%{name}" >> /tmp/baselibs_new.conf
shellquote "  targettype x86 block!" >> /tmp/baselibs_new.conf
shellquote "  targettype 32bit block!" >> /tmp/baselibs_new.conf
shellquote "  targettype inject autoreqprov off" >> /tmp/baselibs_new.conf
shellquote "  targettype inject extension -inject" >> /tmp/baselibs_new.conf
shellquote "  targettype inject +/" >> /tmp/baselibs_new.conf
shellquote "  targettype inject -%{_mandir}" >> /tmp/baselibs_new.conf
shellquote "  targettype inject -%{_docdir}" >> /tmp/baselibs_new.conf
shellquote "  targettype inject config    -/sb2-config$" >> /tmp/baselibs_new.conf

cat /tmp/baselibs_new.conf > %{_sourcedir}/baselibs.conf


%clean
rm -rf $RPM_BUILD_ROOT

%files -f filestoinclude2
%defattr(-,root,root)
%dir /root/
%dir /var/lib/rpm/
%dir /var/cache/ldconfig/
/etc/securetty