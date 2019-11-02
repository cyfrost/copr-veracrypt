%global pname VeraCrypt
%global dummy_package   0
%global tarballdir %{pname}_%{version}
%global srcdir %{tarballdir}/src
%global indocdir %{tarballdir}/doc
%global gitcommit_full 6252d96b0de2001b29596715c8f3345cc93324f7
%global gitcommit %(c=%{gitcommit_full}; echo ${c:0:7})
%global date 20191031
%global sourcerepo https://github.com/veracrypt/VeraCrypt

%define license_files %{srcdir}/License.txt
%define debug_package %{nil}
%define wx_version_major 3
%define wx_version_minor 0
%define wx_version %{wx_version_major}.%{wx_version_minor}
%define force_wx_gtk2 %{nil}
%define force_wx_gtk2 0
%define wx_name_postfix %{nil}

Name:   veracrypt
Version:  1.24.1
Release:  1.%{date}git%{gitcommit}%{?dist}
Summary:  Disk encryption with strong security based on TrueCrypt

License:  Apache License 2.0 and TrueCrypt License 3.0
URL:    https://www.veracrypt.fr/
Source0:  %{sourcerepo}/tarball/%{gitcommit_full}

Packager: cyfrost <cyrus.frost@hotmail.com>
%if "%{?wx_toolkit}" != ""
BuildRequires:  compat-wxGTK%{?wx_name_postfix}-%{wx_toolkit}-devel
%else
BuildRequires:  wxGTK3-devel
%endif
BuildRequires: gcc-c++
BuildRequires: fuse-devel
BuildRequires: desktop-file-utils
BuildRequires: ImageMagick
BuildRequires: util-linux
BuildRequires: yasm
BuildRequires:  ghostscript
%if 0%{?fedora}
BuildRequires:  ghostscript-core
%endif

%description
VeraCrypt is a free open source disk encryption software for Windows, Mac OSX and Linux. Brought to you by IDRIX (https://www.idrix.fr) and based on TrueCrypt 7.1a.

%global gitcommit_full 6252d96b0de2001b29596715c8f3345cc93324f7

%prep
%autosetup -n %{gitcommit_full}


%if 0%{?wx_version_major} >= 3
  %if 0%{?wx_version_minor} == 0
    %define wx_name_postfix %{wx_version_major}
  %else
    %define wx_name_postfix %{wx_version_major}%{wx_version_minor}
  %endif
%endif

# Force toolkit
# e.g. gtk2 instead of gtk3
%define wx_toolkit %{nil}
%if 0%{?force_wx_gtk2}
  %if 0%{?wx_version_major} >= 3
    %if 0%{?wx_version_minor} == 0
      %define wx_toolkit gtk2
    %endif
  %endif
%endif

%undefine update_mime_database_n
%if 0%{?fedora}%{?rhel}
  %define update_mime_database_n 1
%endif

%define doc_license %{nil}
%define doc_license 1
%if 0%{?rhel}%{?fedora}
  %if 0%{?rhel}
    %if 0%{?rhel} < 7
      %define doc_license 0
    %endif
  %else
    %if 0%{?fedora} < 19
      %define doc_license 0
    %endif
  %endif
%endif

%define enable_dumpfullversion %{nil}
%define enable_dumpfullversion 0
%if 0%{?rhel}%{?fedora}
  %if 0%{?rhel}
    %if 0%{?rhel} > 7
      %define enable_dumpfullversion 1
    %endif
  %else
    %if 0%{?fedora} > 25
      %define enable_dumpfullversion 1
    %endif
  %endif
%endif

%define doctarget %{_docdir}/%{name}
%if 0%{?rhel}
  %define doctarget %{_docdir}/%{name}-%{version}
%endif


%build
%if 0%{wx_version_major} < 3
WXCONFIG="wx-config"
%else
WXCONFIG="wx-config-%{wx_version}"
%endif
export WXCONFIG

%if "%{?wx_toolkit}" != ""
if hash "${WXCONFIG}-%{?wx_toolkit}" >/dev/null 2>&1 ; then
  WXCONFIG="${WXCONFIG}-%{?wx_toolkit}"
  export WXCONFIG
fi
%endif

%if !0%{?dummy_package}
   pushd %{srcdir}
   %{__make} WX_CONFIG="${WXCONFIG}" %{?_smp_mflags}
   popd
%endif

%install
#%make_install -C %{tarballdir}/src
%{__install} -d "%{buildroot}%{_bindir}"
%if !0%{?dummy_package}
%{__install} %{srcdir}/Main/veracrypt "%{buildroot}%{_bindir}"
%endif
%{__install} -d "%{buildroot}%{_docdir}/%{name}"
%if !0%{?doc_license}
%{__install} -m 0644 %{srcdir}/License.txt "%{buildroot}%{doctarget}"
%endif
%{__install} -d "%{buildroot}%{_datadir}/applications" "%{buildroot}%{_datadir}/pixmaps"
%{__install} %{srcdir}/Setup/Linux/%{name}.desktop "%{buildroot}%{_datadir}/applications"
%{__install} %{srcdir}/Resources/Icons/%{pname}-256x256.xpm "%{buildroot}%{_datadir}/pixmaps/%{name}.xpm"

# cleanup

# desktop files
test -f %{srcdir}/Setup/Linux/%{name}.desktop && \
   %{__install} -p -D -m 0644 "%{srcdir}/Setup/Linux/%{name}.desktop" "%{buildroot}%{_datadir}/applications/%{name}.desktop" || :

# application start script
# none

# man pages
# not really man pages in this case, just html and text
if test -e "%{indocdir}/chm/VeraCrypt User Guide.chm" ;
then
   mv "%{indocdir}/chm/VeraCrypt User Guide.chm" "%{indocdir}/chm/VeraCrypt_User_Guide.chm" || :
fi
! test -d "%{buildroot}%{doctarget}" && %{__install} -d "%{buildroot}%{doctarget}" || :
%{__install} -D -m 0644 %{indocdir}/chm/VeraCrypt_User_Guide.chm %{buildroot}%{doctarget}

# icons
pushd %{srcdir}/Resources/Icons
for s in 16 48 128 256 ;
do
   convert "%{pname}-${s}x${s}.xpm" "%{pname}-${s}x${s}.png" && \
      %{__install} -p -D -m 0644 "%{pname}-${s}x${s}.png" "%{buildroot}%{_datadir}/icons/hicolor/${s}x${s}/apps/%{name}.png" || :
done
popd

for e in {xpm,png} ;
do
  test -f "%{srcdir}/Resources/Icons/%{pname}-256x256.${e}" || continue
  %{__install} -p -D -m 0644 "%{srcdir}/Resources/Icons/%{pname}-256x256.${e}" "%{buildroot}%{_datadir}/pixmaps/%{name}.${e}"
done

:

%clean
rm -rf %{buildroot} || :

%post
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
/usr/bin/update-mime-database "%{_datadir}/mime" &>/dev/null || :
update-desktop-database &> /dev/null || :
/sbin/ldconfig || :

%preun
# is it a final removal?
#if test "$1" = "0" ;
#then
#fi   

%postun
update-desktop-database &> /dev/null || :
if test "$1" = "0" ;
then
   touch --no-create %{_datadir}/icons/hicolor &>/dev/null
   gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
   /usr/bin/update-mime-database "%{_datadir}/mime" &>/dev/null || :
fi
/sbin/ldconfig || :

%posttrans
/usr/bin/gtk-update-icon-cache "%{_datadir}/icons/hicolor" &>/dev/null || :
/usr/bin/update-mime-database "%{_datadir}/mime" &>/dev/null || :

%files
%if 0%{?doc_license}
%license %{license_files}
%else
%doc %{license_files}
%endif
%doc %{indocdir}/chm/VeraCrypt_User_Guide.chm %{indocdir}/EFI-DCS/ %{indocdir}/html/
%if !0%{?dummy_package}
%{_bindir}/%{name}
%endif
%{_datadir}/applications/*.desktop
%{_datadir}/pixmaps/*
%{_datadir}/icons/hicolor/*/apps/*

%changelog
* Sat Nov 2 2019 Cyrus Frost <cyrus.frost@hotmail.com>
 - Update to VeraCrypt v1.24-Hotfix release
* Fri Oct 11 2019 Cyrus Frost <cyrus.frost@hotmail.com>
 - Update to VeraCrypt v1.24
* Sun Oct 6 2019 Cyrus Frost <cyrus.frost@hotmail.com>
 - rebuild rpm
* Wed Sep 26 2018 B Stack <bgstack15@gmail.com> 1.23-1
- rebuild rpm
