Name: UMobj
Summary: Command Line Utilties for UMIACS Object Storage Services
Version: =VERSION=
Release: 1
Group: UMIACS
License: unknown
URL: http://www.umiacs.umd.edu
Source0: %{name}-%{version}.tar.gz
Buildroot: %{_tmppath}/%{name}
Requires: python, python-boto, python-progressbar, python-filechunkio, environment-modules
BuildArch: noarch

%description
UMIACS Object Storage command line utilties.

%prep
%setup
%build
%install
make install DESTDIR=%{buildroot}
## install the environment-modules support
install -Dp -m0644 ext/modulefiles/UMobj \
    %{buildroot}%{_sysconfdir}/modulefiles/UMobj
## install the profile.d support
install -Dp -m0644 ext/profile.d/UMobj.csh \
    %{buildroot}%{_sysconfdir}/profile.d/UMobj.csh
install -Dp -m0644 ext/profile.d/UMobj.sh \
    %{buildroot}%{_sysconfdir}/profile.d/UMobj.sh

%clean
rm -rf %{buildroot}

%files
%defattr(0755,root,root,-)
# edit the following to list all files that required by the package
# by default, bin, man, data, and doc directories are included
%dir /opt/UMobj
/opt/UMobj/*
/etc/modulefiles/UMobj
/etc/profile.d/UMobj.csh
/etc/profile.d/UMobj.sh

%changelog
