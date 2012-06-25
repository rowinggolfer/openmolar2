%define name openmolar-client
%define version 2.0.63
%define unmangled_version 2.0.63
%define release 1

Summary: Dental Practice Management Software - client
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
Description: Dental Practice Management Software - Client Application

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
