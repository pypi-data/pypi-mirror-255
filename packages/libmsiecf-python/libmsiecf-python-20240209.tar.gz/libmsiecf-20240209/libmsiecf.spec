Name: libmsiecf
Version: 20240209
Release: 1
Summary: Library to access the MSIE Cache File (index.dat) format
Group: System Environment/Libraries
License: LGPL-3.0-or-later
Source: %{name}-%{version}.tar.gz
URL: https://github.com/libyal/libmsiecf
              
BuildRequires: gcc              

%description -n libmsiecf
Library to access the MSIE Cache File (index.dat) format

%package -n libmsiecf-static
Summary: Library to access the MSIE Cache File (index.dat) format
Group: Development/Libraries
Requires: libmsiecf = %{version}-%{release}

%description -n libmsiecf-static
Static library version of libmsiecf.

%package -n libmsiecf-devel
Summary: Header files and libraries for developing applications for libmsiecf
Group: Development/Libraries
Requires: libmsiecf = %{version}-%{release}

%description -n libmsiecf-devel
Header files and libraries for developing applications for libmsiecf.

%package -n libmsiecf-python3
Summary: Python 3 bindings for libmsiecf
Group: System Environment/Libraries
Requires: libmsiecf = %{version}-%{release} python3
BuildRequires: python3-devel python3-setuptools

%description -n libmsiecf-python3
Python 3 bindings for libmsiecf

%package -n libmsiecf-tools
Summary: Several tools for reading MSIE Cache File (index.dat)
Group: Applications/System
Requires: libmsiecf = %{version}-%{release}

%description -n libmsiecf-tools
Several tools for reading MSIE Cache File (index.dat)

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

%files -n libmsiecf
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.so.*

%files -n libmsiecf-static
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.a

%files -n libmsiecf-devel
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.so
%{_libdir}/pkgconfig/libmsiecf.pc
%{_includedir}/*
%{_mandir}/man3/*

%files -n libmsiecf-python3
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/python3*/site-packages/*.a
%{_libdir}/python3*/site-packages/*.so

%files -n libmsiecf-tools
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_bindir}/*
%{_mandir}/man1/*

%changelog
* Fri Feb  9 2024 Joachim Metz <joachim.metz@gmail.com> 20240209-1
- Auto-generated

