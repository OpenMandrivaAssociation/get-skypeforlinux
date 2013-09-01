%define name			get-skype
%define version			4.2.0.11
%define release			2
%define instdir			%{_datadir}/skype
%define langdir			%{instdir}/lang
%define avatardir		%{instdir}/avatars
%define sounddir		%{instdir}/sounds
%define docdir			%{_datadir}/doc/skype
%define dbusdir			%{_sysconfdir}/dbus-1/system.d

ExclusiveArch: %{ix86}

# When updating tarball check that download size in description
# is correct

# %ifarch %{x86_64}
%define tar_name		skype_static
%define md5			f749e1c109fbe182b44d462d04f46bee
# %endif

%ifarch %{ix86}
%define tar_name		skype
%define md5			6e9553a6368853c647b1c5ad7f3cc99b
%endif


%define tmp_download_dir	%{_localstatedir}/lib/%{name}

# Don't generate dependencies for bundled libs
AutoReqProv:	no

Summary:	Download and Install Skype
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	Proprietary
Group:		Networking/Instant messaging
URL:		http://www.skype.com

Requires:	wget

%ifarch %{ix86}
Requires:	liblcms1
Requires:	libmng1
Requires:	libqtcore4
Requires:	libqtdbus4
Requires:	libqtnetwork4
Requires:	libqtwebkit4
Requires:	libqtgui4
Requires:	libqtsvg4
Requires:	libqtxml4
Requires:	libxscrnsaver1
Requires:	libxv1
Requires:	libv4l-wrappers
Requires:	libalsa2
Requires:	libpulseaudio0
%endif
%ifarch x86_64
Requires:	libz1
%endif

Obsoletes:	skype < %{version}
Provides:	skype = %{version}-%{release}

# The following are lists of filenames (124 in total) placed 
# in versioned text files to save clutter in the spec file.
Source0:	avatars-%{version}.txt
Source1:	sounds-%{version}.txt
Source2:	lang-%{version}.txt
# skype-txt-gen is a script to generate the above txt files, it
# also computes the md5sum from a downloaded version.
# See notes in the script.
Source3:	skype-txt-gen
# Manually created skype.desktop to replace invalid original in tar.bz2
Source4:	skype.desktop
# Dependencies for x86_64 package
Source5:	skypelibs.tar.xz
# Disable rpmlint for /opt
Source6:	get-skype.rpmlintrc

%description
This is an installer for Skype-%{version}.

This package does not contain any program files as the Skype license does
not allow distribution. By installing this package you will download and
install Skype from skype.com.
You must accept the Skype EULA before using it.
Please be patient, this is a 23 MB download and may take some time.
Removing this package will uninstall Skype from your system.


%pre
mkdir -p %{tmp_download_dir}
[[ -d %{tmp_download_dir} ]] || exit 1
cd %{tmp_download_dir} || exit 1

%ifarch x86_64
wget --force-clobber --timeout=30 --tries=3 "http://download.skype.com/linux/skype_static-%{version}.tar.bz2"
%endif

%ifarch %{ix86}
wget --force-clobber --timeout=30 --tries=3 "http://download.skype.com/linux/skype-%{version}.tar.bz2"
%endif

[[ -f %{tar_name}-%{version}.tar.bz2 ]] || { echo "Download failed"; rm -r %{tmp_download_dir}; exit 1; }
md5chk=$(md5sum %{tar_name}-%{version}.tar.bz2 | cut -d' ' -f1)
[[ %{md5} = $md5chk ]] || { echo "Download checksum failed"; rm %{tar_name}-%{version}.tar.bz2;\
cd ..; rm -r %{tmp_download_dir}; exit 1; }


%install
install -d -m 0755 %{buildroot}%{_bindir}
install -d -m 0755 %{buildroot}%{_datadir}/applications
install -m 755 %{SOURCE4} %{buildroot}%{_datadir}/applications/
install -d -m 0755 %{buildroot}%{instdir}
touch %{buildroot}%{instdir}/skype
install -d -m 0755 %{buildroot}%{dbusdir}
touch %{buildroot}%{dbusdir}/skype.conf
install -d -m 0755 %{buildroot}%{docdir}
touch %{buildroot}%{docdir}/{LICENSE,README}

install -d -m 0755 %{buildroot}%{instdir}/icons
install -d -m 0755 %{buildroot}%{_iconsdir}
touch %{buildroot}%{_iconsdir}/skype.png
for i in 16 32 48; do
touch %{buildroot}%{_iconsdir}/SkypeBlue_${i}x${i}.png
touch %{buildroot}%{instdir}/icons/SkypeBlue_${i}x${i}.png
done

install -d -m 0755 %{buildroot}%{avatardir}
while read line; do
touch %{buildroot}%{avatardir}/"$line"
done < %{SOURCE0}

install -d -m 0755 %{buildroot}%{sounddir}
while read line; do
touch %{buildroot}%{sounddir}/"$line"
done < %{SOURCE1}

install -d -m 0755 %{buildroot}%{langdir}
while read line; do
touch %{buildroot}%{langdir}/skype_"$line"
done < %{SOURCE2}

%ifarch x86_64
install -d -m 0755 %{buildroot}/opt
tar Jxf %{SOURCE5} -C %{buildroot}/opt

echo '#!/bin/bash
if [ "`pidof skype`" != "" ]; then
    echo "Skype is already running!"
else
    LD_LIBRARY_PATH=/opt/skypelibs LD_PRELOAD=/opt/skypelibs/v4l2convert.so exec %{instdir}/skype "$@"
fi' \
 > %{buildroot}%{_bindir}/skype && chmod +x %{buildroot}%{_bindir}/skype
%endif

%ifarch %{ix86}
echo '#!/bin/bash
if [ "`pidof skype`" != "" ]; then
    echo "Skype is already running!"
else
    LD_PRELOAD=/usr/lib/libv4l/v4l2convert.so exec %{instdir}/skype "$@"
fi' \
 > %{buildroot}%{_bindir}/skype && chmod +x %{buildroot}%{_bindir}/skype
%endif


%post
tmp_extract_dir=$(mktemp -d)
if ! [[ -d $tmp_extract_dir ]]; then
echo "Failed to create temporary directory"
rm -r %{tmp_download_dir} 
exit 1
fi

%ifarch x86_64
%define tmp_skype_dir ${tmp_extract_dir}/%{tar_name}QT-%{version}
%endif

%ifarch %{ix86}
%define tmp_skype_dir ${tmp_extract_dir}/%{tar_name}-%{version}
%endif

cd ${tmp_extract_dir}
tar jxf %{tmp_download_dir}/%{tar_name}-%{version}.tar.bz2

if ! [[ -d %{tmp_skype_dir} ]]; then
echo "Extracted file folder missing"
cd ..
rm -rf ${tmp_extract_dir}
rm -r %{tmp_download_dir}
exit 1
fi

# If any extra files are installed here then 
# corresponding ghost files need to be added in files

mkdir -p %{instdir}/{avatars,lang,sounds}

cp -f %{tmp_skype_dir}/icons/* %{_iconsdir}
cp -f %{_iconsdir}/SkypeBlue_48x48.png %{_iconsdir}/skype.png
mv -f %{tmp_skype_dir}/skype.conf %{dbusdir}
mv -f %{tmp_skype_dir}/LICENSE %{docdir}
mv -f %{tmp_skype_dir}/README %{docdir}
mv -f %{tmp_skype_dir}/skype %{instdir}
cp -f %{tmp_skype_dir}/avatars/* %{avatardir}/
cp -f %{tmp_skype_dir}/lang/* %{langdir}/
cp -f %{tmp_skype_dir}/sounds/* %{sounddir}/
cd ..
rm -r ${tmp_extract_dir} %{tmp_download_dir}


%files
%ghost %doc %{docdir}
%{_bindir}/skype
%ifarch x86_64
/opt/skypelibs
%endif
%attr(0644, root, root) %{_datadir}/applications/skype.desktop
%ghost %{_iconsdir}/skype.png
%ghost %{_iconsdir}/SkypeBlue_*.png
%ghost %{instdir}
%ghost %{dbusdir}/skype.conf


