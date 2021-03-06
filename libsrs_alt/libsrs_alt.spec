Summary:	Implementation of the SRS specification
Name:		libsrs_alt
Version:	1.0
Release:	3
License:	GPL
Group:		Libraries
Source0:	http://opsec.eu/src/srs/%{name}-%{version}.tar.bz2
# Source0-md5:	6d1539eeba08dffe83f92ac38e229dda
URL:		http://opsec.eu/src/srs/
BuildRequires:	autoconf >= 2.59
BuildRequires:	automake
BuildRequires:	libstdc++-devel
BuildRequires:	libtool
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
Libsrs_alt is an implementation of the SRS specification as found at
http://spf.pobox.com/srs.html.

%package devel
Summary:	Header files for libsrs_alt library
Group:		Development/Libraries

%description devel
Header files for libsrs_alt library.

%package static
Summary:	Static libsrs_alt library
Group:		Development/Libraries

%description static
Static libsrs_alt library.

%prep
%setup -q

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS
%attr(755,root,root) %{_bindir}/srs
%attr(755,root,root) %{_libdir}/libsrs_alt.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libsrs_alt.so.1

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libsrs_alt.so
%{_libdir}/libsrs_alt.la
%{_includedir}/*.h

%files static
%defattr(644,root,root,755)
%{_libdir}/libsrs_alt.a
