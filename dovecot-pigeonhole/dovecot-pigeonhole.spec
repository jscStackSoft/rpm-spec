Summary: Sieve plugin for dovecot
Name: dovecot-pigeonhole
Version: 0.4.13
Release: 2%{?dist}
Epoch: 2
License: LGPL
Group: System Environment/Daemons
URL: http://pigeonhole.dovecot.org/
Source0: http://pigeonhole.dovecot.org/releases/2.2/dovecot-2.2-pigeonhole-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: dovecot-devel >= 1:2.2
#BuildRequires: autoconf, automake, libtool
BuildRequires: gcc-c++
BuildRequires: pkgconfig
BuildRequires: flex, bison
BuildRequires: openssl-devel
Requires: dovecot >= 1:2.2
Obsoletes: dovecot-sieve < %{evr}
Provides: dovecot-sieve = %{evr}

%description
Sieve is a language that can be used to create filters for electronic
mail.

Dovecot Sieve is a fully rewritten Sieve implementation for Dovecot 
v1.2 and newer. The main reason for rewriting the Sieve engine was 
to provide more reliable script execution and to provide better 
error messages to users and system administrators. This 
implementation is part of the Pigeonhole project. 

**IMPORTANT NOTICE**
Read this before migrating from dovecot-sieve-cmu package:
http://wiki.dovecot.org/LDA/Sieve/Dovecot#Migration_from_CMUSieve

%package devel
Summary: Libraries and headers for %{name}
Group: Development/Libraries
Requires: %{name} = %{epoch}:%{version}-%{release}

%description devel
This package contains development files for linking against %{name}.

%package -n dovecot-managesieve
Summary: Manage Sieve daemon for dovecot
Group: System Environment/Daemons

%description -n dovecot-managesieve
This package provides the Manage Sieve daemon for dovecot.

%prep
%setup -q -n dovecot-2.2-pigeonhole-%{version}

%build
#rm -f m4/lt* m4/libtool.m4 build-aux/ltmain.sh
#autoreconf -fiv
%configure --with-dovecot=%{_libdir}/dovecot \
  --with-managesieve=yes \
  INSTALL_DATA="install -c -p -m644"
make

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

#remove the libtool and static archives
find %{buildroot}%{_libdir}/dovecot/ -name '*.la' -o -name '*.a' \
  | xargs -r rm -f

%clean
rm -rf %{buildroot}

%check
make test

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING COPYING.LGPL INSTALL NEWS README
%{_bindir}/sieve-test
%{_bindir}/sieve-filter
%{_bindir}/sievec
%{_bindir}/sieve-dump
%{_libdir}/dovecot/lib90_sieve_plugin.so
%{_libdir}/dovecot/libdovecot-sieve.so*
%{_libdir}/dovecot/doveadm/lib10_doveadm_sieve_plugin.so
%{_libdir}/dovecot/sieve/lib90_sieve_extprograms_plugin.so
%{_libdir}/dovecot/settings/libpigeonhole_settings.so
%{_mandir}/man1/sieve-test.1*
%{_mandir}/man1/sieve-filter.1*
%{_mandir}/man1/sievec.1*
%{_mandir}/man1/sieved.1*
%{_mandir}/man1/sieve-dump.1*
%{_mandir}/man1/doveadm-sieve.1*
%{_mandir}/man7/pigeonhole.7*
%{_docdir}/dovecot-2.*/example-config/conf.d/90-sieve*.conf
%{_docdir}/dovecot-2.*/sieve

%files devel
%defattr(-,root,root,-)
%dir %{_includedir}/dovecot/sieve
%{_includedir}/dovecot/sieve/*.h
%{_datadir}/aclocal/dovecot-pigeonhole.m4

%files -n dovecot-managesieve
%dir %{_libdir}/dovecot/settings/
%{_libdir}/dovecot/settings/libmanagesieve_login_settings.so
%{_libdir}/dovecot/settings/libmanagesieve_settings.so
%{_libexecdir}/dovecot/managesieve
%{_libexecdir}/dovecot/managesieve-login
%{_docdir}/dovecot-2*/example-config/conf.d/20-managesieve.conf

%changelog
* Sun Oct  6 2013 Kim Bisgaard <kim+j2@alleroedderne.adsl.dk> - 2:0.4.1-31
- Update to 0.4.2

* Thu Jul  4 2013 Axel Thimm <Axel.Thimm@ATrpms.net> - 2:0.4.1-28
- Update to 0.4.1.

* Thu May 16 2013 Axel Thimm <Axel.Thimm@ATrpms.net> - 2:0.4.0-24
- Update to 0.4.0.

* Wed May 15 2013 Axel Thimm <Axel.Thimm@ATrpms.net> - 2:0.3.5-23
- Update to 0.3.5.

* Thu Mar  8 2012 Axel Thimm <Axel.Thimm@ATrpms.net> - 2:0.3.0-22
- Update to 0.3.0.

* Thu Dec  8 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 2:0.2.5-20
- Update to 0.2.5.

* Sat Nov 12 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 2:0.2.4-19
- Update to 0.2.4.

* Wed Apr 27 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 2:0.2.3-16
- Update to 0.2.3.

* Mon Jan  3 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 2:0.2.2-13
- Update to 0.2.2.

* Wed Oct 27 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 2:0.2.1-12
- Fix rpath in managesieve-login.

* Thu Sep 30 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 2:0.2.1-11
- Update to 0.2.1 GA.

* Sat Aug 28 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0-10
- Update to latest source code.

* Fri Aug 20 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0-9
- Update to latest source code.

* Thu Aug 12 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0-8
- Update to latest source code.

* Wed Jul 21 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0-7
- Update to latest source code.

* Mon Jul  5 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:0.1.17-6
- Update to latest source code.

* Tue Apr  6 2010 Angel Marin <anmar@anmar.eu.org> - 1:0.1.15-5
- Update to a dovecot 2.x compatible source tree
- Merged dovecot-managesieve package

* Mon Jan 25 2010 Angel Marin <anmar@anmar.eu.org> - 1:0.1.15-4
- Update to 0.1.15.
- More Makefile fixups to make it build against dovecot-devel

* Wed Jan  6 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:0.1.14-3
- Rename package to dovecot-sieve (was dovecot-sieve-new).
- Make it "newer" than current versioning to allow proper upgrade paths.
- Some minor specfile fixes.

* Mon Dec 21 2009 Angel Marin <anmar@anmar.eu.org> - 0.1.14-2
- Update to 0.1.14.

* Thu Dec 17 2009 Angel Marin <anmar@anmar.eu.org> - 0.1.13-1
- first build
