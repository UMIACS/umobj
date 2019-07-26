%define name umobj
%define release 1

Summary: UMIACS Object Storage Commands
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
License: LGPL v2.1
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires: %{python}
Requires: %{python}-boto
Requires: %{python}-progressbar
Requires: %{python}-filechunkio
Requires: %{python}-bagit
%if 0%{?el6}
Requires: %{python}-argparse
Requires: qav >= 0.3.2
%else
Requires: %{python}-qav >= 1.0.2
%endif
AutoReq: no
Prefix: %{_prefix}
BuildArch: noarch
Vendor: UMIACS Staff <github@umiacs.umd.edu>
Url: https://github.com/UMIACS/umobj

%description
Command-line utilties for S3-compatible Object Storage

%prep
%setup

%build
%{python} setup.py build

%install
%{python} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
## install man pages
install -m0755 -d $RPM_BUILD_ROOT%{_mandir}/man1
install -Dp -m0644 share/man/man1/* %{buildroot}%{_mandir}/man1

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%{_mandir}/man1/*.1.gz
