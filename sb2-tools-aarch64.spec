%define packages_in_tools autoconf automake gnu-bash binutils gnu-which bzip2 bzip2-libs cargo ccache clang clang-libs cmake cpio cpp db4 gnu-diffutils doxygen elfutils elfutils-libelf elfutils-libs expat fakeroot fdupes file file-libs filesystem gnu-findutils fontconfig freetype gawk gcc gcc-c++ glib2 glibc glibc-common glibc-devel glibc-headers gmp gnu-coreutils gnu-grep gnu-gzip kernel-headers libacl libarchive libattr libblkid libcap libcap libcurl libgcc libgomp libicu liblua lua-posix libmount libnghttp2 libpsl libsb2 libsmartcols libstdc++ libstdc++-devel libuuid libxml2 llvm-libs m4 make mpc mpfr ncurses-libs net-tools nspr nss nss-pem nss-softokn-freebl openssl-libs libxcrypt pam pcre pcre2 perl perl-libs perl-Scalar-List-Utils perl-threads perl-threads-shared popt python3-base python3-libs python3-setuptools python3-rpm-generators qemu-usermode readline rpm rpm-build rpm-devel rpm-libs rpm-sign rpmlint-mini rust scratchbox2 gnu-sed setup sqlite-libs gnu-tar util-linux xz xz-libs zip zlib zstd libzstd
%define cross_compilers   cross-aarch64-gcc cross-aarch64-binutils
%define _target_cpu aarch64
# Prevent stripping, python-bytecompiling etc. as this has been already done for the packages
%global __os_install_post %{nil}

Name:          sb2-tools-aarch64-inject
Version:       1.0+git29
Release:       1
AutoReqProv:   0
BuildRequires: rpm grep tar patchelf sed
BuildRequires: %packages_in_tools
BuildRequires: %cross_compilers
# We should build only on i586/i486 these packages, however
# ExclusiveArch: or ExcludeArch: do not work here, because after OBS starts building
# we set the _target_cpu above to e.g. armv7hl and then rpm declines to build the package.
Source101: precheckin.sh
Source200: sb2-tools-template-rpmlintrc
# no auto requirements - they're generated
License:       BSD
Summary:       SB2 cross tools

%description
This is a package providing %packages_in_tools %cross_compilers for SB2 tools directory 
It is not intended to be used in a normal system!


%package -n sb2-tools-aarch64-dependency-inject
Summary: Dependency for sb2 host side

%description -n sb2-tools-aarch64-dependency-inject
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
# Copy files to buildroot and preserve permissions.
tar --no-recursion -T filestoinclude2 -cpf - | ( cd %buildroot && fakeroot tar -xvpf - ) > filesincluded

# Rust is special. It executes cc in host-cc mode which is SBOX_DISABLE_MAPPING=1
# This means it cannot see the rustlib in the target. Instead of adding rust-std-static
# to sb2-tools-template we symlink to the target
# We need to move the existing content first
echo files in %buildroot/usr/lib/rustlib:
find %buildroot/usr/lib/rustlib
echo and in filelist:
grep rustlib filesincluded

mkdir -p %buildroot/target/usr/lib/
echo moving /usr/lib/rustlib to /target
mv %buildroot/usr/lib/rustlib %buildroot/target/usr/lib/
sed -i filesincluded -e 's,usr/lib/rustlib,target/usr/lib/rustlib,'
ln -s /target/usr/lib/rustlib  %buildroot/usr/lib/
echo /usr/lib/rustlib >> filesincluded

echo files in %buildroot/target:
find %buildroot/target
echo now in filelist:
grep rustlib filesincluded

# Add back "/" prefix, add double quotes to protect file names with spaces, use %%dir directive for
# directories to prevent "File listed twice" warnings.
sed -i filesincluded -e '
    # First line is special - it is the root directory
    1s,^\./$,%%dir /,
    t
    # Lines ending with / are special - they are directory paths
    s,^\(.*\)/$,%%dir "/\1",
    t
    # Everything else
    s,^.*$,"/&",
    '
cat filesincluded
sed 's|:.*$|:*:16229:0:99999:7:::|' < /etc/passwd > %{buildroot}/etc/shadow
sed 's|:.*$|:*::|' < /etc/group > %{buildroot}/etc/gshadow
chmod 0400 %buildroot/etc/shadow
chmod 0400 %buildroot/etc/gshadow
mkdir -p %buildroot/var/log
mkdir -p %buildroot/root/
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

%files -f filesincluded
%defattr(-,root,root)
%dir /var/log
%dir /root/
%dir /var/cache/ldconfig/
/etc/securetty
%verify(not md5 size mtime) %attr(0400,root,root) %config(noreplace) /etc/shadow
%verify(not md5 size mtime) %attr(0400,root,root) %config(noreplace) /etc/gshadow

%files -n sb2-tools-aarch64-dependency-inject
%defattr(-,root,root)
/etc/sb2-tools-template
