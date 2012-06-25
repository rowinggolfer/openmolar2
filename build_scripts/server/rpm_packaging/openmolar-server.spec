%define name openmolar-server
%define version 2.0.63
%define unmangled_version 2.0.63
%define release 1

Summary: Dental Practice Management Software - server
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPL v3
Group: Office
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Neil Wallace <neil@openmolar.com>
Url: http://www.openmolar.com

BuildRequires: python

%description
Dental Practice Management Software - Server Component
the openmolar daemon running on port 230.
provides remote call functions and status messages to bridge between 
the openmolar-admin application (which may be on a remote machine) and
the postgres database server (which is a dependency of this package)

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
