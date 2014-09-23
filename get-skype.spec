%define instdir %{_datadir}/skype
%define langdir %{instdir}/lang
%define avatardir %{instdir}/avatars
%define sounddir %{instdir}/sounds
%define docdir %{_datadir}/doc/skype
%define dbusdir %{_sysconfdir}/dbus-1/system.d
# When updating tarball check that download size in description
# is correct
%define md5 95db8f2072b9acd6f79ed42da3d6db79
%define tmp_download_dir %{_localstatedir}/lib/%{name}

Summary:	Download and Install Skype
Name:		get-skype
Version:	4.3.0.37
Release:	4
License:	Proprietary
Group:		Networking/Instant messaging
URL:		http://www.skype.com
BuildArch:	noarch

Requires(pre):	wget
Requires:	libv4l-wrappers
# (fwang) these requires comes from combine of `objdump -x skype|grep NEEDED`
# and `strings skype|grep lib.*.so`
Requires:	libasound.so.2
Requires:	libXv.so.1
Requires:	libXss.so.1
Requires:	librt.so.1
Requires:	libdl.so.2
Requires:	libX11.so.6
Requires:	libXext.so.6
Requires:	libQtDBus.so.4
Requires:	libQtWebKit.so.4
Requires:	libQtXml.so.4
Requires:	libQtGui.so.4
Requires:	libQtNetwork.so.4
Requires:	libQtCore.so.4
Requires:	libpthread.so.0
Requires:	libpulse.so.0
Requires:	libstdc++.so.6
Requires:	libm.so.6
Requires:	libgcc_s.so.1
Requires:	libc.so.6
Obsoletes:	skype < %{version}
Provides:	skype = %{version}-%{release}

# The following are lists of filenames (128 in total) placed 
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
Source5:	get-skype.rpmlintrc
ExclusiveArch:	%{ix86} x86_64
# Don't generate dependencies for bundled libs
AutoReqProv:	no

%description
This is an installer for Skype-%{version}.

This package does not contain any program files as the Skype license does
not allow distribution. By installing this package you will download and
install Skype from skype.com.
You must accept the Skype EULA before using it.
Please be patient, this is a 16 MB download and may take some time.
Removing this package will uninstall Skype from your system.


%pre
mkdir -p %{tmp_download_dir}
[[ -d %{tmp_download_dir} ]] || exit 1
cd %{tmp_download_dir} || exit 1
wget --force-clobber --timeout=30 --tries=3 "http://download.skype.com/linux/skype-%{version}.tar.bz2"
[[ -f skype-%{version}.tar.bz2 ]] || { echo "Download failed"; rm -r %{tmp_download_dir}; exit 1; }
md5chk=$(md5sum skype-%{version}.tar.bz2 | cut -d' ' -f1)
[[ %{md5} = $md5chk ]] || { echo "Download checksum failed"; rm skype-%{version}.tar.bz2;\
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
for i in 16 32 48 64 96 128 256; do
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

echo "#!/bin/bash
LD_PRELOAD=/usr/lib/libv4l/v4l2convert.so %{instdir}/skype" > %{buildroot}%{_bindir}/skype && chmod +x %{buildroot}%{_bindir}/skype


%post
tmp_extract_dir=$(mktemp -d)
if ! [[ -d $tmp_extract_dir ]]; then
 echo "Failed to create temporary directory"
 rm -r %{tmp_download_dir} 
 exit 1
fi

%define tmp_skype_dir ${tmp_extract_dir}/skype-%{version}
cd ${tmp_extract_dir}
tar jxf %{tmp_download_dir}/skype-%{version}.tar.bz2

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
cp -f %{_iconsdir}/SkypeBlue_96x96.png %{_iconsdir}/skype.png
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
%attr(0644, root, root) %{_datadir}/applications/skype.desktop
%ghost %{_iconsdir}/skype.png
%ghost %{_iconsdir}/SkypeBlue_*.png
%ghost %{instdir}
%ghost %{dbusdir}/skype.conf
 