# -- metadata

%define srcname igwn-archive
%define version 0.1.1
%define release 1

Name:      python-%{srcname}
Version:   %{version}
Release:   %{release}%{?dist}
Summary:   Utilities for interacting with the IGWN Software Archive

License:   GPLv3+
Url:       https://computing.docs.ligo.org/guide/software/distribution/
Source0:   %pypi_source
Packager:  Duncan Macleod <duncan.macleod@ligo.org>
Vendor:    Duncan Macleod <duncan.macleod@ligo.org>
BuildArch: noarch
Prefix:    %{_prefix}

# rpmbuild dependencies
BuildRequires: python-srpm-macros
BuildRequires: python-rpm-macros
BuildRequires: python3-rpm-macros

# build dependencies
BuildRequires: help2man
BuildRequires: python%{python3_pkgversion}-devel
BuildRequires: python%{python3_pkgversion}-pip
BuildRequires: python%{python3_pkgversion}-setuptools >= 38.2.5
BuildRequires: python%{python3_pkgversion}-wheel

%description
igwn-archive provides utilities for interacting with the IGWN
Software Archive at <https://software.igwn.org>.
This package is the source RPM distribution.

# -- packages

%package -n python%{python3_pkgversion}-%{srcname}
Summary: Python %{python3_version} igwn-archive library
Requires: rsync
%if 0%{?rhel} == 0 || 0%{?rhel} >= 8
Recommends: python%{python3_pkgversion}-coloredlogs
%endif
%{?python_provide:%python_provide python%{python3_pkgversion}-%{srcname}}
%description -n python%{python3_pkgversion}-%{srcname}
igwn-archive provides utilities for interacting with the IGWN
Software Archive at <https://software.igwn.org>.
This package provides the Python %{python3_version} library.

%package -n %{srcname}
Summary: Command line utilities for igwn-archive
Requires: python%{python3_pkgversion}-%{srcname} = %{version}-%{release}
%description -n %{srcname}
igwn-archive provides utilities for interacting with the IGWN
Software Archive at <https://software.igwn.org>.
This package provides the command-line utilities.

# -- build steps

%prep
%autosetup -n %{srcname}-%{version}

%build
%py3_build_wheel

%install
%py3_install_wheel igwn_archive-%{version}-*.whl
# man pages
mkdir -p %{buildroot}%{_mandir}/man1
export PYTHONPATH="%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}:${PYTHONPATH}"
help2man \
	--output %{buildroot}%{_mandir}/man1/igwn-source-upload.1 \
	--name "IGWN source distribution uploader" \
	--no-info \
	--no-discard-stderr \
	--section 1 \
	--source %{srcname} \
	--version-string %{version} \
	%{buildroot}%{_bindir}/igwn-source-upload

%check
export PYTHONPATH="%{buildroot}%{python3_sitelib}"
export PATH="%{buildroot}%{_bindir}:${PATH}"
igwn-source-upload --help

%clean
rm -rf $RPM_BUILD_ROOT

# -- files

%files -n python%{python3_pkgversion}-%{srcname}
%license LICENSE
%doc README.md
%{python3_sitelib}/*

%files -n %{srcname}
%license LICENSE
%doc README.md
%{_bindir}/*
%{_mandir}/man1/*.1*

# -- changelog

%changelog
* Tue Feb 06 2024 Duncan Macleod <duncan.macleod@ligo.org> - 0.1.1-1
- update to 0.1.1
- add rsync requirement for python3-igwn-archive

* Wed Feb 09 2022 Duncan Macleod <duncan.macleod@ligo.org> - 0.1.0-2
- fix requires for igwn-archive

* Tue Feb 08 2022 Duncan Macleod <duncan.macleod@ligo.org> - 0.1.0-1
- initial release
