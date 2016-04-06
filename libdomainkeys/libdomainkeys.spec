Summary: DomainKey Implementor's library
Name: libdomainkeys
Version: 0.69
Release: 7%{?dist}
License: Yahoo! DomainKeys Public License
Group: System Environment/Libraries
URL: http://domainkeys.sourceforge.net/
Source0: http://prdownloads.sourceforge.net/domainkeys/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: openssl-devel
Provides: libdomainkeys-devel = %{evr}

%description
DomainKey Implementor's library.

%package devel
Summary: DomainKey development files
Group: System Environment/Libraries
Provides: libdomainkeys-devel

%description devel
This package contains necessary header files for DomainKey development.

%prep
%setup -q
perl -pi -e's/CFLAGS=/CFLAGS=%{optflags} -fPIC /' Makefile
echo "-lresolv" > dns.lib

%build
make UNAME=Linux

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_includedir}
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_bindir}

install -p -m 0644 domainkeys.h dktrace.h %{buildroot}%{_includedir}
install -p -m 0644 libdomainkeys.a %{buildroot}%{_libdir}
install -p -m 0755 dknewkey dktest %{buildroot}%{_bindir}

%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc README CHANGES *.html
%{_bindir}/*
%{_libdir}/libdomainkeys.a

%files devel
%{_includedir}/*


%changelog
* Tue Mar  1 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.69-6
- Update to 0.69.

* Fri Dec 29 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 0.68-5
- Remove dot from summary ...
- Fix permissions from include files

* Sun Nov 27 2005 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 0.68.

* Sat Jul  2 2005 Axel Thimm <Axel.Thimm@ATrpms.net>
- Initial build.
