Name:           libgsasl
Version:        1.8.0
Release:        1%{?dist}
Summary:        GNU SASL library 

Group:          System Environment/Libraries
License:        LGPLv2+ 
URL:            http://www.gnu.org/software/gsasl/
Source0:        ftp://ftp.gnu.org/gnu/gsasl/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libidn-devel
BuildRequires:  krb5-devel
BuildRequires:  libntlm-devel

BuildRequires:  pkgconfig

%description
The library includes support for the SASL framework
and at least partial support for the CRAM-MD5, EXTERNAL,
GSSAPI, ANONYMOUS, PLAIN, SECURID, DIGEST-MD5, LOGIN,
and NTLM mechanisms.


%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       pkgconfig

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -q


%build
%configure --disable-static --disable-rpath
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT INSTALL='install -p'
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'
%find_lang %{name}


%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS COPYING NEWS README THANKS
%{_libdir}/libgsasl.so.*

%files devel
%defattr(-,root,root,-)
%doc COPYING
%{_includedir}/gsasl*
%{_libdir}/libgsasl.so
%{_libdir}/pkgconfig/libgsasl.pc


%changelog
* Thu Apr 7 2016 Andrey Lyarskiy <alyarskiy@stacksoft.ru> - 1.8-1
- Updating to 1.8 from upstream

* Tue Jan 12 2010 Nikolay Vladimirov <nikolay@vladimiroff.com> - 1.4-4
- Fix another small typo(wrong version)

* Tue Jan 12 2010 Nikolay Vladimirov <nikolay@vladimiroff.com> - 1.4-3
- Fix another small typo(mixed tabs and spaces)

* Tue Jan 12 2010 Nikolay Vladimirov <nikolay@vladimiroff.com> - 1.4-2
- Fix small typo

* Tue Jan 12 2010 Nikolay Vladimirov <nikolay@vladimiroff.com> - 1.4-1
- new upstream release

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.29-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.29-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 1 2009 Nikolay Vladimirov <nikolay@vladimiroff.com> - 0.2.29-1
- Rewrite to use poll instead of select.
- Don't use poll with POLLOUT to avoid busy-waiting.

* Tue Jul 29 2008 Nikolay Vladimirov <nikolay@vladimiroff.com> - 0.2.27-1
- new upstream release 0.2.27

* Tue Jun 3 2008 Nikolay Vladimirov <nikolay@vladimiroff.com> - 0.2.26-1
- new upstream release 0.2.26

* Sat Mar 29 2008 Nikolay Vladimirov <nikolay@vladimiroff.com> - 0.2.25-1
- new upstream release

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.2.18-6
- Autorebuild for GCC 4.3

* Thu Aug 29 2007 Nikolay Vladimirov <nikolat@vladimiroff.com> - 0.2.18-5
- rebuild for ppc32 selinux fix

* Thu Aug 2 2007 Nikolay Vladimirov <nikolat@vladimiroff.com> - 0.2.18-4
- License tag changed
 
* Tue Jun 26 2007 Nikolay Vladimirov <nikolay@vladimiroff.com> - 0.2.18-3
- added NTLM support

* Fri Jun 22 2007 Nikolay Vladimirov <nikolay@vladimiroff.com> - 0.2.18-2
- fixed mixed-use-of-spaces-and-tabs
- fixed timestamps for header files 
- edited summary

* Thu Jun 21 2007 Nikolay Vladimirov <nikolay@vladimiroff.com> - 0.2.18-1
- initial release
