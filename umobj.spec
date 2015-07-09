%{!?python_sitelib: %global python_sitelib %(%{python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
Name: umobj
Summary: Command-line utilties for S3-compatible Object Storage
Version: =VERSION=
Release: 1
Group: UMIACS
License: unknown
URL: https://github.com/UMIACS/umobj
Source0: %{name}-%{version}.tar.gz
Buildroot: %{_tmppath}/%{name}
Requires: %{python}
Requires: %{python}-boto
Requires: %{python}-progressbar
Requires: %{python}-argparse
Requires: %{python}-filechunkio
Requires: %{python}-bagit
Requires: qav >= 0.2.7
AutoReq: no
BuildArch: noarch

%description
UMIACS Object Storage command line utilties.

%prep
%setup
%build
%{python} setup.py build

%install
%{python} setup.py install --skip-build --root %{buildroot}
## install man pages
install -m 0755 -d %{buildroot}%{_mandir}/man1
install -Dp -m0644 share/man/man1/* \
    %{buildroot}%{_mandir}/man1

%clean
rm -rf %{buildroot}

%files
%defattr(0755,root,root,-)
%{_bindir}/bagobj
%{_bindir}/catobj
%{_bindir}/chobj
%{_bindir}/cmpobj
%{_bindir}/cpobj
%{_bindir}/lsobj
%{_bindir}/mkobj
%{_bindir}/mvobj
%{_bindir}/rmobj
%{_bindir}/syncobj
%defattr(0755,root,root,-)
%{python_sitelib}/umobj
%defattr(0644,root,root,-)
%{python_sitelib}/umobj/*
%{python_sitelib}/%{name}*.egg-info
%{_mandir}/man1/*.1.gz

%changelog
