%define name openmolar-namespace
%define version 2.0.63
%define unmangled_version 2.0.63
%define release 1

Summary: Dental Practice Management Software - namespace
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
Dental Practice Management Software - library namespace

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
