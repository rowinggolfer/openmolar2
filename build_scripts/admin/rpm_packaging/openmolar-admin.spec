%define name openmolar-admin
%define version 2.0.63
%define unmangled_version 2.0.63
%define release 1

Summary: Dental Practice Management Software - admin
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
Dental Practice Management Software - Admin Component
provides an assortment of command line and graphical tools for 
initialising a practice database, and managing many of the occasional 
maintenance tasks. Usually only one install per network 

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
