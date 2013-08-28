Name: UMobj
Summary: Command Line Utilties for UMIACS Object Storage Services
Version: =VERSION=
Release: 1
Group: UMIACS
License: unknown
URL: http://www.umiacs.umd.edu
Source0: %{name}-%{version}.tar.gz
Buildroot: %{_tmppath}/%{name}
%if 0%{?rhel} && 0%{?rhel} <= 5
Requires: python26, python26-boto, python26-progressbar, python26-filechunkio
%else
Requires: python, python-boto, python-progressbar, python-filechunkio
%endif
BuildArch: noarch

%description
UMIACS Object Storage command line utilties.

%prep
%setup
%build
%install
make install DESTDIR=%{buildroot}
%if 0%{?rhel} && 0%{?rhel} <= 5
find %{buildroot}/opt/UMobj/bin -type f | xargs sed -i '1s|^#!python|#!python26|'
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(0755,root,root,-)
# edit the following to list all files that required by the package
# by default, bin, man, data, and doc directories are included
%dir /opt/UMobj
/opt/UMobj/*

%changelog
