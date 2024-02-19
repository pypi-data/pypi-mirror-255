Name: libnk2
Version: 20240210
Release: 1
Summary: Library to access the Nickfile (NK2) format
Group: System Environment/Libraries
License: LGPL-3.0-or-later
Source: %{name}-%{version}.tar.gz
URL: https://github.com/libyal/libnk2
              
BuildRequires: gcc              

%description -n libnk2
Library to access the Nickfile (NK2) format

%package -n libnk2-static
Summary: Library to access the Nickfile (NK2) format
Group: Development/Libraries
Requires: libnk2 = %{version}-%{release}

%description -n libnk2-static
Static library version of libnk2.

%package -n libnk2-devel
Summary: Header files and libraries for developing applications for libnk2
Group: Development/Libraries
Requires: libnk2 = %{version}-%{release}

%description -n libnk2-devel
Header files and libraries for developing applications for libnk2.

%package -n libnk2-python3
Summary: Python 3 bindings for libnk2
Group: System Environment/Libraries
Requires: libnk2 = %{version}-%{release} python3
BuildRequires: python3-devel python3-setuptools

%description -n libnk2-python3
Python 3 bindings for libnk2

%package -n libnk2-tools
Summary: Several tools for reading Nickfiles (NK2)
Group: Applications/System
Requires: libnk2 = %{version}-%{release} 
 

%description -n libnk2-tools
Several tools for reading Nickfiles (NK2)

%prep
%setup -q

%build
%configure --prefix=/usr --libdir=%{_libdir} --mandir=%{_mandir} --enable-python
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
%make_install

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files -n libnk2
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.so.*

%files -n libnk2-static
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.a

%files -n libnk2-devel
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.so
%{_libdir}/pkgconfig/libnk2.pc
%{_includedir}/*
%{_mandir}/man3/*

%files -n libnk2-python3
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/python3*/site-packages/*.a
%{_libdir}/python3*/site-packages/*.so

%files -n libnk2-tools
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_bindir}/*
%{_mandir}/man1/*

%changelog
* Sat Feb 10 2024 Joachim Metz <joachim.metz@gmail.com> 20240210-1
- Auto-generated

