%define docdir %{_datadir}/doc/skypeforlinux
%define tmp_download_dir %{_localstatedir}/lib/%{oname}
%bcond_without stable

%define oname skypeforlinux

Summary:	Download and Install Electron (Chromium)-based Skype
Name:		get-%{oname}
Version:	8.27.0.85
Release:	1
License:	Proprietary
Group:		Networking/Instant messaging
Url:		http://www.skype.com
Requires:	wget
Suggests:	seahorse
Provides:	skype = %{EVRD}
ExclusiveArch:	%{x86_64}

%description
This is an installer for Skype-%{version}.

This package does not contain any program files as the Skype license does
not allow distribution. By installing this package you will download and
install Skype from skype.com.
You must accept the Skype EULA before using it.
Please be patient, this is a 61 MB download and may take some time.
Removing this package will uninstall Skype from your system.

%files

%pre
mkdir -p %{tmp_download_dir}
[[ -d %{tmp_download_dir} ]] || exit 1
cd %{tmp_download_dir} || exit 1

%if %{with stable}
wget --force-clobber --timeout=30 --tries=3 "https://repo.skype.com/rpm/stable/skypeforlinux_%{version}-1.x86_64.rpm"
%else
wget --force-clobber --timeout=30 --tries=3 "https://repo.skype.com/rpm/unstable/skypeforlinux_%{version}-1.x86_64.rpm"
%endif

%post
tmp_extract_dir=$(mktemp -d)
if ! [[ -d $tmp_extract_dir ]]; then
echo "Failed to create temporary directory"
rm -r %{tmp_download_dir}
exit 1
fi

#https://answers.microsoft.com/en-us/skype/forum/skype_linux-skype_startms-skype_installms/upgrade-for-skypeforlinux-5501/98f0760d-fc4a-42e5-9d40-87c45803d062
if [ `rpm -q get-skypeforlinux | wc -w` == 1 ]
then
    rpm -e get-skypeforlinux
fi

%define tmp_skype_dir ${tmp_extract_dir}/%{oname}-%{version}

mkdir -p %{tmp_skype_dir}
cd %{tmp_skype_dir}
rpm2cpio %{tmp_download_dir}/skypeforlinux_%{version}-1.x86_64.rpm | cpio -idmv

if ! [[ -d %{tmp_skype_dir} ]]; then
echo "Extracted file folder missing"
cd ..
rm -rf ${tmp_extract_dir}
rm -r %{tmp_download_dir}
exit 1
fi

mv -f %{tmp_skype_dir}%{_bindir}/skypeforlinux %{_bindir}/skypeforlinux
mv -f %{tmp_skype_dir}%{_datadir}/applications/%{oname}.desktop %{_datadir}/applications/%{oname}.desktop
mv -f %{tmp_skype_dir}%{_datadir}/pixmaps/%{oname}.png %{_datadir}/pixmaps/%{oname}.png
cp -rf %{tmp_skype_dir}%{docdir}/ %{_datadir}/doc/
cp -rf %{tmp_skype_dir}%{_iconsdir}/hicolor/ %{_iconsdir}/
cp -rf %{tmp_skype_dir}%{_datadir}/%{oname}/ %{_datadir}

cd ..
rm -r ${tmp_extract_dir} %{tmp_download_dir}

# Remove skype-install package if we have it installed
if [ `rpm -q skype-install | wc -w` == 1 ]
then
    rpm -e skype-install
fi

%preun
rm -f %{_bindir}/skypeforlinux
rm -f %{_datadir}/applications/%{oname}.desktop
rm -f %{_datadir}/pixmaps/%{oname}.png
rm -f %{_iconsdir}/hicolor/16x16/apps/%{oname}.png
rm -f %{_iconsdir}/hicolor/32x32/apps/%{oname}.png
rm -f %{_iconsdir}/hicolor/256x256/apps/%{oname}.png
rm -f %{_iconsdir}/hicolor/512x512/apps/%{oname}.png
rm -f %{_iconsdir}/hicolor/1024x1024/apps/%{oname}.png
rm -rf %{_datadir}/%{oname}
rm -rf %{docdir}

#----------------------------------------------------------------------------

%prep

%build

%install
