Name: UMobj
Summary: Command Line Utilties for UMIACS Object Storage Services
Version: =VERSION=
Release: 1
Group: UMIACS
License: unknown
URL: http://www.umiacs.umd.edu
Source0: %{name}-%{version}.tar.gz
Buildroot: %{_tmppath}/%{name}
Requires: python26, python26-boto, python26-progressbar, python26-filechunkio, environment-modules
BuildArch: noarch

%description
UMIACS Object Storage command line utilties.

%prep
%setup
%build
%install
make install DESTDIR=%{buildroot}
find %{buildroot}/opt/UMobj/bin -type f | xargs sed -i '1,1s/python/python26/'
## install the environment-modules support
install -Dp -m0644 ext/modulefiles/UMobj \
    %{buildroot}%{_sysconfdir}/modulefiles/UMobj

%clean
rm -rf %{buildroot}

%files
%defattr(0755,root,root,-)
# edit the following to list all files that required by the package
# by default, bin, man, data, and doc directories are included
%dir /opt/UMobj
/opt/UMobj/*
/etc/modulefiles/UMobj

%changelog
