%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
#%{!?python_pkg: %global python_pkg %(%{__python} -c "from sys import executable; print executable.split('/')[-1]")}
Name: UMobj
Summary: Command Line Utilties for UMIACS Object Storage Services
Version: =VERSION=
Release: 1
Group: UMIACS
License: unknown
URL: https://staff.umiacs.umd.edu/gitlab/staff/UMobj
Source0: %{name}-%{version}.tar.gz
Buildroot: %{_tmppath}/%{name}
Requires: %{python_pkg}, %{python_pkg}-boto, %{python_pkg}-progressbar, %{python_pkg}-filechunkio
BuildArch: noarch

%description
UMIACS Object Storage command line utilties.

%prep
%setup
%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root %{buildroot}
## install man pages
install -m 0755 -d %{buildroot}%{_mandir}/man1
install -Dp -m0644 share/man/man1/* \
    %{buildroot}%{_mandir}/man1

%clean
rm -rf %{buildroot}

%files
%defattr(0755,root,root,-)
%{_bindir}/chobj
%{_bindir}/cpobj
%{_bindir}/lsobj
%{_bindir}/md5obj
%{_bindir}/mkobj
%{_bindir}/mvobj
%{_bindir}/rmobj
%defattr(0644,root,root,-)
%{python_sitelib}/umobj
%{python_sitelib}/UMobj*.egg-info
%{_mandir}/man1/*.1.gz

%changelog
