# busybox is included because busybox-symlinks-which needs it
# busybox-symlinks-which provides which
# libselinux is needed by busybox
%define packages_in_tools autoconf automake bash binutils busybox busybox-symlinks-which bzip2 bzip2-libs ccache cmake coreutils cpio cpp db4 diffutils doxygen elfutils elfutils-libelf elfutils-libs expat fakeroot fdupes file file-libs filesystem findutils fontconfig freetype gawk gcc glib2 glibc glibc-common glibc-devel glibc-headers gmp grep gzip kernel-headers libacl libarchive libattr libblkid libcap libcap libcurl libgcc libgomp libicu libidn liblua libmount libsb2 libselinux libsmartcols libstdc++ libuuid libxml2 m4 make mpc mpfr ncurses-libs net-tools nspr nss nss-pem nss-softokn-freebl openssl-libs pam pcre perl perl-libs perl-Scalar-List-Utils perl-threads perl-threads-shared popt python python-libs qemu-usermode readline rpm rpm-build rpm-devel rpm-libs scratchbox2 sed setup sqlite-libs tar util-linux xz xz-libs zip zlib

%define cross_compilers   cross-armv7tnhl-gcc cross-armv7tnhl-binutils
%define _target_cpu armv7tnhl
# Prevent stripping, python-bytecompiling etc. as this has been already done for the packages
%global __os_install_post %{nil}

Name:          sb2-tools-armv7tnhl-inject
Version:       1.0+git11
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

%package -n sb2-tools-aarch64-filesystem-inject
Summary: Filesystem files for sb2 target
Group: Development/Tools

%description -n sb2-tools-aarch64-filesystem-inject
This is a package providing /bin /lib /sbin symlinks for SB2 tools directory
It is only intended to be used in the preinstall!

%prep

%build

%install
#set +x -e

# We must make the /usr/* dirs to avoid problems when /bin is a symlink to /usr/bin
mkdir -p %buildroot/usr/bin
mkdir -p %buildroot/usr/lib
mkdir -p %buildroot/usr/sbin

# Get a list of all the files in our rpms *according to the rpm DB*
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
/usr/lib/pkgconfig/rpm.pc
/var/lib/rpm/
EOF
# Strip out the files we don't want (note at this point filenames are 'as per rpm DB')
grep -vf filestoignore filestoinclude1 | sort | uniq > filestoinclude2

# At this point the current project should have used a 'filesystem'
# package which runs the lua /usr merge in the post install.  So the
# rpm DB doesn't represent on-disk... fix that now:
sed -i filestoinclude2 -e '
   s,^/bin,/usr/bin/,
   s,^/lib,/usr/lib/,
   s,^/sbin,/usr/sbin,'

# Uncomment this to check :)
# cat filestoinclude2

# Copy files to buildroot and preserve permissions.
tar --no-recursion -T filestoinclude2 -cpf - | ( cd %buildroot && fakeroot tar -xvpf - ) > filesincluded
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
sort -u filesincluded > f.sorted
mv f.sorted filesincluded
# This can allow a check of the rpm DB vs the transformed/installed filelist
# cat filesincluded
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
# Make the symlinks needed for the preinstall to target
# Keep them relative - just in case
ln -s usr/bin %buildroot/bin
ln -s usr/lib %buildroot/lib
ln -s usr/sbin %buildroot/sbin

%clean
rm -rf $RPM_BUILD_ROOT

%files -f filesincluded
%defattr(-,root,root)
%dir /var/log
%dir /root/
%dir /var/cache/ldconfig/
/etc/securetty
%verify(not md5 size mtime) %attr(0400,root,root) %config(noreplace) /etc/shadow
%verify(not md5 size mtime) %attr(0400,root,root) %config(noreplace) /etc/gshadow

%files -n sb2-tools-armv7tnhl-dependency-inject
%defattr(-,root,root)
/etc/sb2-tools-template

%files -n sb2-tools-aarch64-filesystem-inject
%defattr(-,root,root)
/bin
/lib
/sbin
