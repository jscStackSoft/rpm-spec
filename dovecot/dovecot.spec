%bcond_without inotify
%bcond_with forcequota2
%bcond_without pidfile
%bcond_without solr
%bcond_with systemd
%bcond_without rquota

%global _hardened_build 1
Summary: Dovecot Secure imap server
Name: dovecot
Epoch: 1
Version: 2.2.23
Release: 1%{?dist}
License: MIT
Group: System Environment/Daemons

URL: http://www.dovecot.org/
Source0: http://www.dovecot.org/releases/2.2/%{name}-%{version}.tar.gz
Source1: dovecot.init
Source2: dovecot.pam
Source3: maildir-migration.txt
Source9: dovecot.sysconfig
Source10: dovecot.tmpfilesd

#our own
Source14: dovecot.conf.5

Source88: dovecot.logrotate
Patch1: dovecot-2.1-defaultconfig.patch
Patch2: dovecot-1.0.beta2-mkcert-permissions.patch
Patch3: dovecot-1.0.rc7-mkcert-paths.patch
Patch4: dovecot-2.1.10-reload.patch
Patch5: dovecot-2.1-privatetmp.patch

#wait for network
Patch6: dovecot-2.1.10-waitonline.patch
#Patch7: dovecot-2.2.4-saslconflict.patch
Source15: prestartscript

Patch102: dovecot-1.1.3-pam-setcred.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: autoconf, automake, libtool, gettext-devel
BuildRequires: gcc-c++
BuildRequires: krb5-devel
BuildRequires: openssl-devel
BuildRequires: openldap-devel, cyrus-sasl-devel
BuildRequires: pam-devel
BuildRequires: pkgconfig
BuildRequires: zlib-devel, bzip2-devel, lz4-devel, xz-devel
BuildRequires: libcap-devel
%{?with_solr:BuildRequires: libcurl-devel expat-devel}
%{?with_lucene:BuildRequires: clucene-core-devel}
%{?with_rquota:BuildRequires: quota-devel}
# Explicit Runtime Requirements
#Requires: openssl >= 0.9.7f-4
Requires: openssl
Requires: shadow-utils
Requires: lz4, xz
%if %{with systemd}
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%else
Requires: initscripts, chkconfig
%endif

Provides: %{name}-pgsql = %{evr}, %{name}-mysql = %{evr}
Obsoletes: %{name}-pgsql < %{epoch}:%{version}-%{release}, %{name}-mysql < %{epoch}:%{version}-%{release}, %{name}-sqlite < %{epoch}:%{version}-%{release}, %{name}-ldap < %{epoch}:%{version}-%{release}, %{name}-gssapi < %{epoch}:%{version}-%{release}
Conflicts: %{name}-pgsql > %{epoch}:%{version}-%{release}, %{name}-mysql > %{epoch}:%{version}-%{release}, %{name}-sqlite > %{epoch}:%{version}-%{release}, %{name}-ldap > %{epoch}:%{version}-%{release}, %{name}-gssapi > %{epoch}:%{version}-%{release}

BuildRequires: postgresql-devel
BuildRequires: mysql-devel
BuildRequires: sqlite-devel
BuildRequires: db4-devel

%define ssldir %{_sysconfdir}/pki/%{name}

%global restart_flag /var/run/%{name}/%{name}-restart-after-rpm-install

%description
Dovecot is an IMAP server for Linux/UNIX-like systems, written with security 
primarily in mind.  It also contains a small POP3 server.  It supports mail 
in either of maildir or mbox formats.

%package devel
Summary: Libraries and headers for Dovecot
Group: Development/Libraries
Requires: %name = %{epoch}:%{version}-%{release}
Requires: openssl-devel

%description devel
This package contains development files for linking against %{name}.

%prep
%setup -q
%patch1 -p1 -b .default-settings
%patch2 -p1 -b .mkcert-permissions
%patch3 -p1 -b .mkcert-paths
#%patch4 -p1 -b .reload
#%patch5 -p1 -b .privatetmp
#%patch6 -p1 -b .waitonline
#%patch7 -p1 -b .saslconflict
sed -i '/DEFAULT_INCLUDES *=/s|$| '"$(pkg-config --cflags libclucene-core)|" src/plugins/fts-lucene/Makefile.in
%patch102 -p1 -b .pam-setcred
cat Makefile.am > Makefile.am.bak
echo 'ACLOCAL_AMFLAGS=-I .' > Makefile.am
cat Makefile.am.bak >> Makefile.am

%build
#required for fdpass.c line 125,190: dereferencing type-punned pointer will break strict-aliasing rules
export CFLAGS="%{optflags} -fno-strict-aliasing"
export LDFLAGS="-Wl,-z,now -Wl,-z,relro %{?__global_ldflags}"
autoreconf -I . -ifv
%configure                       \
    --disable-dependency-tracking \
    INSTALL_DATA="install -c -p -m644" \
    --docdir=%{_docdir}/%{name}-%{version}     \
    --disable-static             \
    --with-nss                   \
    --with-shadow                \
    --with-pam                   \
    --with-gssapi=plugin         \
    --with-ldap=plugin           \
    --with-sql=plugin            \
    --with-pgsql                 \
    --with-mysql                 \
    --with-sqlite                \
    --with-zlib                  \
    --with-lzma                  \
    --with-lz4                   \
    --with-libcap                \
    --with-ssl=openssl           \
    --with-ssldir=%{ssldir}      \
    %{?with_inotify:--with-notify=inotify} \
    %{?with_forcequota2:--with-linux-quota=2} \
    %{?with_solr:--with-solr}    \
    %{?with_lucene:--with-lucene} \
    %{?with_systemd:--with-systemdsystemunitdir=%{_unitdir}} \
    --with-docs

sed -i 's|/etc/ssl|/etc/pki/dovecot|' doc/mkcert.sh doc/example-config/conf.d/10-ssl.conf

make

%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

mv $RPM_BUILD_ROOT/%{_docdir}/%{name}-%{version} %{_builddir}/%{name}-%{version}/docinstall

install -p -D -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/dovecot
# Detect whether the system is using pam_stack
if test -f /%{_lib}/security/pam_stack.so \
   && ! grep "Deprecated pam_stack module" /%{_lib}/security/pam_stack.so \
      2>&1 > /dev/null; then
  perl -pi -e's,include(\s*)(.*),required\1pam_stack.so service=\2,' \
    $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/dovecot
  touch -r %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/dovecot
fi
# Detect whether the system has /etc/pam.d/password-auth
if test ! -f %{_sysconfdir}/pam.d/password-auth; then
  perl -pi -e's,password-auth,system-auth,' \
    $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/dovecot
  touch -r %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/dovecot
fi

install -p -D -m 644 %{SOURCE88} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/dovecot

#install man pages
install -p -D -m 644 %{SOURCE14} $RPM_BUILD_ROOT%{_mandir}/man5/dovecot.conf.5

#install waitonline script
install -p -D -m 755 %{SOURCE15} $RPM_BUILD_ROOT%{_libexecdir}/dovecot/prestartscript

# generate ghost .pem files
mkdir -p $RPM_BUILD_ROOT%{ssldir}/certs
mkdir -p $RPM_BUILD_ROOT%{ssldir}/private
touch $RPM_BUILD_ROOT%{ssldir}/certs/dovecot.pem
chmod 600 $RPM_BUILD_ROOT%{ssldir}/certs/dovecot.pem
touch $RPM_BUILD_ROOT%{ssldir}/private/dovecot.pem
chmod 600 $RPM_BUILD_ROOT%{ssldir}/private/dovecot.pem

%if %{with systemd}
#install -p -D -m 644 %{SOURCE10} $RPM_BUILD_ROOT%{_tmpfilesdir}/dovecot.conf
install -p -D -m 644 %{SOURCE10} $RPM_BUILD_ROOT/etc/tmpfiles.d/dovecot.conf
%else
install -p -D -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_initddir}/dovecot
install -p -D -m 600 %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/dovecot
%endif

%if %{with pidfile}
%else
perl -pi -e's, --pidfile \$pidfile,,' $RPM_BUILD_ROOT%{_initddir}/dovecot
perl -pi -e's, -p \$pidfile,,' $RPM_BUILD_ROOT%{_initddir}/dovecot
touch -r %{SOURCE1} $RPM_BUILD_ROOT%{_initddir}/dovecot
%endif

mkdir -p $RPM_BUILD_ROOT/var/run/dovecot/{login,empty}
chmod 755 $RPM_BUILD_ROOT/var/run/dovecot
chmod 750 $RPM_BUILD_ROOT/var/run/dovecot/login
mkdir -p $RPM_BUILD_ROOT/var/cache/dovecot/indexes

# Install dovecot configuration and dovecot-openssl.cnf
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/dovecot/conf.d
install -p -m 644 docinstall/example-config/dovecot.conf $RPM_BUILD_ROOT%{_sysconfdir}/dovecot
install -p -m 644 docinstall/example-config/conf.d/*.conf $RPM_BUILD_ROOT%{_sysconfdir}/dovecot/conf.d
install -p -m 644 docinstall/example-config/conf.d/*.conf.ext $RPM_BUILD_ROOT%{_sysconfdir}/dovecot/conf.d
install -p -m 644 doc/dovecot-openssl.cnf $RPM_BUILD_ROOT%{ssldir}/dovecot-openssl.cnf

install -p -m755 doc/mkcert.sh $RPM_BUILD_ROOT%{_libexecdir}/%{name}/mkcert.sh

mkdir -p $RPM_BUILD_ROOT/var/lib/dovecot

#remove the libtool archives
#find $RPM_BUILD_ROOT%{_libdir}/%{name}/ -name '*.la' | xargs rm -f

#remove what we don't want
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/dovecot/README
pushd docinstall
#rm -f dovecot-initd.sh dovecot-openssl.cnf Makefile* 
rm -f securecoding.txt thread-refs.txt
popd


%clean
rm -rf $RPM_BUILD_ROOT


%pre
#dovecot uig and gid are reserved, see /usr/share/doc/setup-*/uidgid 
getent group dovecot >/dev/null || groupadd -r --gid 97 dovecot
getent passwd dovecot >/dev/null || \
useradd -r -u 97 -g dovecot -d /usr/libexec/dovecot -s /sbin/nologin -c "Dovecot IMAP server" dovecot

getent group dovenull >/dev/null || groupadd -r dovenull
getent passwd dovenull >/dev/null || \
useradd -r -g dovenull -d /usr/libexec/dovecot -s /sbin/nologin -c "Dovecot's unauthorized user" dovenull

# do not let dovecot run during upgrade rhbz#134325
if [ "$1" = "2" ]; then
  rm -f %restart_flag
%if %{with systemd}
  /bin/systemctl is-active %{name}.service >/dev/null 2>&1 && touch %restart_flag ||:
  /bin/systemctl stop %{name}.service >/dev/null 2>&1
%else
  /sbin/service %{name} status >/dev/null 2>&1 && touch %restart_flag ||:
  /sbin/service %{name} stop >/dev/null 2>&1
%endif
fi

%post
if [ $1 -eq 1 ]; then
%if %{with systemd}
  %systemd_post dovecot.service
%else
  /sbin/chkconfig --add %{name}
%endif
fi
# create a ssl cert
if [ -f %{ssldir}/%{name}.pem -a ! -e %{ssldir}/certs/%{name}.pem ]; then
    mv  %{ssldir}/%{name}.pem %{ssldir}/certs/%{name}.pem
else
    if [ -f /usr/share/ssl/certs/dovecot.pem -a ! -e %{ssldir}/certs/%{name}.pem ]; then
        mv /usr/share/ssl/certs/dovecot.pem %{ssldir}/certs/%{name}.pem
    fi
    if [ -f /usr/share/ssl/private/dovecot.pem -a ! -e %{ssldir}/private/%{name}.pem ]; then
        mv /usr/share/ssl/private/dovecot.pem %{ssldir}/private/%{name}.pem
    fi
fi
if [ ! -f %{ssldir}/certs/%{name}.pem ]; then
    SSLDIR=%{ssldir} OPENSSLCONFIG=%{ssldir}/dovecot-openssl.cnf \
         %{_libexecdir}/%{name}/mkcert.sh &> /dev/null
fi

if [ ! -f /var/lib/dovecot/ssl-parameters.dat ]; then
    %{_libexecdir}/dovecot/ssl-params &>/dev/null
fi

[ -x /sbin/restorecon ] && /sbin/restorecon -R /var/run/dovecot

%preun
if [ $1 = 0 ]; then
%if %{with systemd}
    /bin/systemctl disable dovecot.service dovecot.socket >/dev/null 2>&1 || :
    /bin/systemctl stop dovecot.service dovecot.socket >/dev/null 2>&1 || :
%else
    /sbin/service %{name} stop > /dev/null 2>&1
    /sbin/chkconfig --del %{name}
%endif
fi

%postun
%if %{with systemd}
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
%endif

if [ "$1" -ge "1" -a -e %restart_flag ]; then
%if %{with systemd}
    /bin/systemctl start dovecot.service >/dev/null 2>&1 || :
%else
    /sbin/service %{name} start >/dev/null 2>&1 || :
%endif
rm -f %restart_flag
fi

%posttrans
# dovecot should be started again in %postun, but it's not executed on reinstall
# if it was already started, restart_flag won't be here, so it's ok to test it again
if [ -e %restart_flag ]; then
%if %{with systemd}
    /bin/systemctl start dovecot.service >/dev/null 2>&1 || :
%else
    /sbin/service %{name} start >/dev/null 2>&1 || :
%endif
rm -f %restart_flag
fi


%check
make check

%files
%defattr(-,root,root,-)
%doc docinstall/* AUTHORS ChangeLog COPYING COPYING.LGPL COPYING.MIT NEWS README
%{_sbindir}/dovecot

%{_bindir}/doveadm
%{_bindir}/doveconf
%{_bindir}/dsync

%if %{with systemd}
#%{_tmpfilesdir}/dovecot.conf
/etc/tmpfiles.d/dovecot.conf
%{_unitdir}/dovecot.service
%{_unitdir}/dovecot.socket
%else
%{_initddir}/dovecot
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/dovecot
%endif

%dir %{_sysconfdir}/dovecot
%dir %{_sysconfdir}/dovecot/conf.d
%config(noreplace) %{_sysconfdir}/dovecot/dovecot.conf
%config(noreplace) %{_sysconfdir}/dovecot/conf.d/*

%config(noreplace) %{_sysconfdir}/pam.d/dovecot
%config(noreplace) %{_sysconfdir}/logrotate.d/dovecot
%config(noreplace) %{ssldir}/dovecot-openssl.cnf

%dir %{ssldir}
%dir %{ssldir}/certs
%dir %{ssldir}/private
%attr(0600,root,root) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{ssldir}/certs/dovecot.pem
%attr(0600,root,root) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{ssldir}/private/dovecot.pem
%dir %{_libdir}/dovecot
%{_libdir}/dovecot/auth
%{_libdir}/dovecot/dict
%{_libdir}/dovecot/doveadm
%{_libdir}/dovecot/*_plugin.so
%{_libdir}/dovecot/*.so.*
%{_libdir}/dovecot/libdriver_*.so
%{_libdir}/dovecot/libssl_iostream_openssl.so
%{_libdir}/dovecot/libfs_compress.so
%dir %{_libdir}/dovecot/stats
%{_libdir}/dovecot/stats/libstats_mail.so
%{_libdir}/dovecot/stats/libstats_auth.so

%dir %{_libexecdir}/dovecot
%{_libexecdir}/dovecot/*
%attr(2755,root,mail) %{_libexecdir}/dovecot/deliver

%dir %{_datadir}/dovecot/stopwords
%{_datadir}/dovecot/stopwords/*.txt

%attr(0755,root,dovecot) %dir /var/run/dovecot
%attr(0755,root,root) %dir /var/run/dovecot/empty
%attr(0750,root,dovenull) %dir /var/run/dovecot/login
%attr(0750,dovecot,dovecot) %dir /var/lib/dovecot

%{_mandir}/man1/deliver.1.gz
%{_mandir}/man1/doveadm*.1.gz
%{_mandir}/man1/doveconf.1.gz
%{_mandir}/man1/dovecot*.1.gz
%{_mandir}/man1/dsync.1.gz
%{_mandir}/man7/doveadm*.7.gz
%{_mandir}/man5/dovecot.conf.5.gz

%dir /var/cache/dovecot
%attr(1777,root,dovecot) %dir /var/cache/dovecot/indexes

%files devel
%defattr(-,root,root,-)
%{_libdir}/dovecot/*.la
%{_libdir}/dovecot/stats/*.la
%{_includedir}/dovecot
%{_datadir}/aclocal/dovecot.m4
%{_libdir}/dovecot/libdovecot*.so
%{_libdir}/dovecot/dovecot-config

%changelog
* Sun Jan  5 2014 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.2.10-1_14
- Update to 2.2.10.

* Sun Oct  6 2013 Kim Bisgaard <kim+j2@alleroedderne.adsl.dk> - 1:2.2.6-2_141
- Update to 2.2.6
- Fix historic dates

* Sat Aug 10 2013 Kim Bisgaard <kim+j2@alleroedderne.adsl.dk> - 1:2.2.5-2_140
- update to 2.2.5
- sasl conflict applied upstream, so removed here

* Sat Jul 13 2013 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.2.4-2_139
- fix name conflict with cyrus-sasl (RH #975869) by Michal Hlavinka.

* Wed Jun 26 2013 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.2.4-0_138
- Update to 2.2.4.

* Mon Jun 10 2013 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.2.2-2_136
- Update to 2.2.2.

* Wed May 15 2013 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.2.1-0_134
- Update to 2.2.1.

* Wed May 15 2013 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.1.16-1_133
- Update to 2.1.16.
- Sync with F18.

* Sun Nov 13 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.1-0_131_beta1
- Update to 2.1.beta1.

* Fri Sep  9 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.1-0_130_alpha1
- Update to 2.1.alpha1.

* Wed Jun  8 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.13-1_129
- Fix typo in %%post script (Kim Bisgaard).

* Tue May 17 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.13-1_128
- Update to 2.0.13.

* Wed Apr 27 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.12-2_127
- Update to 2.0.12.

* Thu Mar 17 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.11-1_126
- Update to 2.0.11.

* Sun Jan 30 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.9-1_125
- Update to 2.0.9.

* Mon Jan  3 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.8-3_124
- Update to 2.0.8.

* Sat Nov 13 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.7-1_123
- Update to 2.0.7.

* Wed Oct 27 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.6-1_122
- Keep libtool libs, they are currenlty needed from proper passing of
  rpath flags.

* Mon Oct 25 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.6-0_121
- Update to 2.0.6.

* Mon Oct 18 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.5-1_120
- Update to 2.0.5.

* Thu Sep 30 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.4-1_119
- Update to 2.0.4.

* Sat Aug 28 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.1-1_118
- Update to 2.0.1.
- Automate removal of pidfile switches in init file.

* Fri Aug 20 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0.0-1_117
- Update to 2.0.0.

* Sat Aug 14 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0-0.20_116_rc6
- Update to 2.0.rc6.

* Thu Aug 12 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0-0.20_115_rc5
- Update to 2.0.rc5.

* Wed Jul 21 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0-0.18_114_rc3
- Update to 2.0.rc3.

* Sun Jul  4 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0-0.15_113_rc1
- Update to 2.0.rc1.

* Fri Jun 18 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0-0.12_111_beta6
- Update to 2.0.beta6.

* Tue May 25 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:2.0-0.12_109_beta5
- Update to 2.0.beta5.

* Sat Apr  3 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2.11-3_108
- Update to 1.2.11.
- Disable bzlib/zlib, they are buggy in 1.x and will be fixed only in 2.x.

* Mon Jan 25 2010 Angel Marin <anmar@anmar.eu.org> - 1:1.2.10-2_107
- Update to 1.2.10.
- Update managesieve patch to 0.11.11.

* Mon Dec 21 2009 Angel Marin <anmar@anmar.eu.org> - 1:1.2.9-0_105
- No need for two copies of dovecot-config
- header files are now installed by dovecot, so we start with that
  copy then figure out the rest out of the Makefile
- find all .a files and copy them (some are multiple levels depth
  into the src dir)
- Update managesieve patch to 0.11.10

* Thu Dec 17 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2.9-0_104
- Update to 1.2.9.

* Fri Nov 20 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2.8-0_103
- Update to 1.2.8.
- sync with rawhide.

* Fri Nov 13 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2.7-0_102
- Update to 1.2.7.

* Tue Oct  6 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2.6-0_101
- Update to 1.2.6.

* Fri Sep 18 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2.5-0_100
- Update to 1.2.5.

* Tue Aug 18 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2.4-0_99
- Update to 1.2.4.

* Wed Aug  5 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2.3-0_97
- Update to 1.2.3.

* Tue Jul 14 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2.1-0_96
- Update to 1.2.1.

* Sun Jul  5 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2.0-0_95
- Update to 1.2.0.

* Tue Jun 23 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2-0_94_rc6
- Update to 1.2rc6.

* Sat Jun 13 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2-0_93_rc5
- Update to 1.2rc5.

* Sat Apr 18 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.2-0_92_rc3
- Update to 1.2rc3.
- Add managesieve support.

* Wed Mar 25 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.13-0_91
- Update to 1.1.13.

* Wed Feb  4 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.11-0_90
- Update to 1.1.11.

* Sat Jan 31 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.10-0_89
- Update to 1.1.10.

* Sat Jan 24 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.9-0_86
- Update to 1.1.9.

* Sat Jan 10 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.8-0_85
- Update to 1.1.8.

* Sun Nov 30 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.7-0_84
- Update to 1.1.7.

* Thu Oct 30 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.6-0_83
- Update to 1.1.6.

* Mon Oct 27 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.5-0_82
- Update to 1.1.5.

* Wed Oct  8 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.4-0_81
- Update to 1.1.4.

* Wed Sep  3 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.3-0_78
- Update to 1.1.3.

* Thu Jul 24 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.2-2_77
- Update to 1.1.2.

* Thu Jun 26 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.1-0_75
- Update to 1.1.1.

* Sat Jun 21 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.0-0_74
- Update to 1.1.0.

* Sat Jun 14 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.rc10-0_73
- Update to 1.1rc10.

* Tue Jun 10 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.rc9-0_72
- Update to 1.1rc9.

* Tue Jun  3 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.rc8-0_71
- Update to 1.1.0rc8.

* Wed May 14 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.1.rc5-0_70
- Update to 1.1.rc5.

* Wed Apr 30 2008 Angel Marin <anmar@anmar.eu.org> - 1:1.1.rc4-0_69
- Update to 1.1.rc4
- Update default-settings patch to 1.1.rc4
- Drop winbind patch (included upstream)

* Thu Mar 13 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.0.13-0_68
- Update to 1.0.13.

* Fri Mar  7 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.0.12-0_67
- Update to 1.0.12.

* Mon Dec 31 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.0.10-0_66
- Update to 1.0.10.

* Wed Dec 12 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.0.9-0_65
- Update to 1.0.9.

* Sun Dec  9 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.0.8-0_64
- Update to 1.0.8.

* Sun Nov  4 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.0.7-0_63
- Update to 1.0.7.

* Mon Oct 29 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.0.6-0_62
- Update to 1.0.6.

* Sun Oct  7 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1:1.0.5-15_61
- Update to 1.0.5.

* Thu Aug  2 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0.3-13_60
- Update to 1.0.3.

* Fri Jul 20 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0.2-13_59
- Update to 1.0.2.

* Fri Jun 15 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0.1-1_57
- Update to 1.0.1.
- Autodetect pam_stack usage.

* Fri Apr 13 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0.0-8_56
- Update to 1.0.0 final.

* Fri Apr  6 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-7_54.rc30
- Update to 1.0.rc30.

* Sat Mar 31 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-7_53.rc29
- Update to 1.0.rc29.

* Mon Mar 26 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-7_52.rc28
- Sync with rawhide's version.

* Sat Mar 24 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-3_51.rc28
- Update to 1.0.rc28.

* Tue Mar 13 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-3_50.rc27
- Update to 1.0.rc27.

* Wed Mar  7 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-3_49.rc26
- Update to 1.0.rc26.

* Thu Mar  1 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-3_48.rc25
- Update to 1.0.rc25.

* Thu Feb 22 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-3_47.rc24
- Update to 1.0.rc24.
- Extend devel to cover plugins (bug #105, Ben Shakal <ben@sixg.com>).

* Tue Feb 20 2007 Troy Engel <tengel@fluid.com> - 1.0-3_46.rc23
- rework default settings patch

* Tue Feb 20 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-3_46.rc23
- Update to 1.0.rc23.

* Tue Feb 06 2007 Troy Engel <tengel@fluid.com> - 1.0-2_45.rc22
- rework default settings patch to be rc21+ friendly
- remove pam-tty patch, implemented upstream
- add logrotate.d script

* Tue Feb  6 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-2_44.rc22
- Update to 1.0.rc22.

* Mon Feb  5 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-2_43.rc21
- *Really* update to 1.0.rc21 ...

* Fri Feb  2 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-1_42.rc21
- Update to 1.0.rc21.

* Fri Feb  2 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-1_41.rc20
- Update to 1.0.rc20.

* Tue Jan 23 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-1_40.rc19
- Update to 1.0.rc19.

* Tue Jan 23 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-1_39.rc18
- Update to 1.0.rc18.

* Sun Jan  7 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-1_37.rc17
- Update to 1.0.rc17.

* Sat Jan  6 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-1_36.rc16
- Update to 1.0.rc16.

* Thu Dec 21 2006 Tomas Janousek <tjanouse@redhat.com>
- reenabled GSSAPI (#220377)

* Mon Dec 18 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_34.rc15
- Sync with rawhide.

* Sun Nov 19 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_33.rc15
- Update to 1.0rc15.

* Mon Nov 13 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_32.rc14
- Update to 1.0rc14.

* Wed Nov  8 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_31.rc13
- Update to 1.0rc13.

* Wed Nov  8 2006 Angel Marin <anmar@anmar.eu.org> - 1.0-0_30.rc12
- Added -devel package with .a, .la and .h files needed for
  building plugins

* Sun Nov  5 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_29.rc12
- Update to 1.0rc12.

* Sun Nov  5 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_28.rc11
- Update to 1.0rc11.

* Mon Oct 16 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_27.rc10
- Update to 1.0rc10.

* Sat Oct 14 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_26.rc9
- Update to 1.0rc9.

* Tue Oct 10 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_25.rc8
- fix %%_libexec to %%_libexecdir.

* Mon Oct  9 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_24.rc8
- Update to 1.0rc8.

* Wed Sep 20 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_23.rc7
- Fix libexec references and unowned directories.

* Wed Aug 30 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_21.rc7
- Some systems (like RHEL4) need to be told to use quota v2. Found by
  Magnus Stenman <stone@hkust.se>.

* Fri Aug 18 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_20.rc7
- Update to 1.0rc7.

* Wed Aug  9 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 1.0-0_19.rc6
- Update to 1.0rc6.

* Thu Aug  3 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 1.0rc5.

* Thu Jul  6 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 1.0rc2.

* Wed Jun 28 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 1.0rc1.

* Sun Jun 18 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 1.0beta9.

* Fri Jun  9 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 1.0beta8.

* Wed Apr 12 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 1.0beta7.

* Wed Apr 12 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 1.0beta6.
- Remove lib64 patch, upstream handles 64 bits now.
- Update to 1.0beta7.
- Remove sqlite patch, handled upstream now.

* Tue Apr  4 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 1.0beta5.

* Mon Apr  3 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 1.0beta4.

* Fri Mar 17 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Add sqlite support.

* Wed Mar  8 2006 Bill Nottingham <notting@redhat.com> - 1.0-0.beta2.7
- fix scriplet noise some more

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 1.0-0.beta2.6
- fix scriptlet error (mitr, #184151)

* Mon Feb 27 2006 Petr Rockai <prockai@redhat.com> - 1.0-0.beta2.5
- fix #182240 by looking in lib64 for libs first and then lib
- fix comment #1 in #182240 by copying over the example config files
  to documentation directory

* Sun Feb 12 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Use ssl-build-param instead of dovecot --build-ssl-parameters
  (by Russell Odom <russ@gloomytrousers.co.uk> bug #727 c11)

* Sat Feb 11 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 1.0 beta3.

* Thu Feb 09 2006 Petr Rockai <prockai@redhat.com> - 1.0-0.beta2.4
- enable inotify as it should work now (#179431)

* Sun Feb  5 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Sync with rawhide.

* Thu Feb 02 2006 Petr Rockai <prockai@redhat.com> - 1.0-0.beta2.3
- change the compiled-in defaults and adjust the default's configfile
  commented-out example settings to match compiled-in defaults,
  instead of changing the defaults only in the configfile, as per #179432
- fix #179574 by providing a default uidl_format for pop3
- half-fix #179620 by having plaintext auth enabled by default... this
  needs more thinking (which one we really want) and documentation
  either way

* Tue Jan 31 2006 Petr Rockai <prockai@redhat.com> - 1.0-0.beta2.2
- update URL in description
- call dovecot --build-ssl-parameters in postinst as per #179430

* Mon Jan 30 2006 Petr Rockai <prockai@redhat.com> - 1.0-0.beta2.1
- fix spec to work with BUILD_DIR != SOURCE_DIR
- forward-port and split pam-nocred patch

* Mon Jan 23 2006 Petr Rockai <prockai@redhat.com> - 1.0-0.beta2
- new upstream version, hopefully fixes #173928, #163550
- fix #168866, use install -p to install documentation

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Sat Nov 12 2005 Tom Lane <tgl@redhat.com> - 0.99.14-10.fc5
- Rebuild due to mysql update.

* Wed Nov  9 2005 Tomas Mraz <tmraz@redhat.com> - 0.99.14-9.fc5
- rebuilt with new openssl

* Fri Sep 30 2005 Tomas Mraz <tmraz@redhat.com> - 0.99.14-8.fc5
- use include instead of pam_stack in pam config

* Wed Jul 27 2005 John Dennis <jdennis@redhat.com> - 0.99.14-7.fc5
- fix bug #150888, log authenication failures with ip address

* Fri Jul 22 2005 John Dennis <jdennis@redhat.com> - 0.99.14-6.fc5
- fix bug #149673, add dummy PAM_TTY

* Thu Apr 28 2005 John Dennis <jdennis@redhat.com> - 0.99.14-5.fc4
- fix bug #156159 insecure location of restart flag file

* Fri Apr 22 2005 John Dennis <jdennis@redhat.com> - 0.99.14-4.fc4
- openssl moved its certs, CA, etc. from /usr/share/ssl to /etc/pki

* Tue Apr 12 2005 Tom Lane <tgl@redhat.com> 0.99.14-3.fc4
- Rebuild for Postgres 8.0.2 (new libpq major version).

* Mon Mar  7 2005 John Dennis <jdennis@redhat.com> 0.99.14-2.fc4
- bump rev for gcc4 build

* Mon Feb 14 2005 John Dennis <jdennis@redhat.com> - 0.99.14-1.fc4
- fix bug #147874, update to 0.99.14 release
  v0.99.14 2005-02-11  Timo Sirainen <tss at iki.fi>
  - Message address fields are now parsed differently, fixing some
    issues with spaces. Affects only clients which use FETCH ENVELOPE
    command.
  - Message MIME parser was somewhat broken with missing MIME boundaries
  - mbox: Don't allow X-UID headers in mails to override the UIDs we
    would otherwise set. Too large values can break some clients and
    cause other trouble.
  - passwd-file userdb wasn't working
  - PAM crashed with 64bit systems
  - non-SSL inetd startup wasn't working
  - If UID FETCH notices and skips an expunged message, don't return
    a NO reply. It's not needed and only makes clients give error
    messages.

* Wed Feb  2 2005 John Dennis <jdennis@redhat.com> - 0.99.13-4.devel
- fix bug #146198, clean up temp kerberos tickets

* Mon Jan 17 2005 John Dennis <jdennis@redhat.com> 0.99.13-3.devel
- fix bug #145214, force mbox_locks to fcntl only
- fix bug #145241, remove prereq on postgres and mysql, allow rpm auto
  dependency generator to pick up client lib dependency if needed.

* Thu Jan 13 2005 John Dennis <jdennis@redhat.com> 0.99.13-2.devel
- make postgres & mysql conditional build
- remove execute bit on migration example scripts so rpm does not pull
  in additional dependences on perl and perl modules that are not present
  in dovecot proper.
- add REDHAT-FAQ.txt to doc directory

* Thu Jan  6 2005 John Dennis <jdennis@redhat.com> 0.99.13-1.devel
- bring up to date with latest upstream, 0.99.13, bug #143707
  also fix bug #14462, bad dovecot-uid macro name

* Thu Jan  6 2005 John Dennis <jdennis@redhat.com> 0.99.11-10.devel
- fix bug #133618, removed LITERAL+ capability from capability string

* Wed Jan  5 2005 John Dennis <jdennis@redhat.com> 0.99.11-9.devel
- fix bug #134325, stop dovecot during installation

* Wed Jan  5 2005 John Dennis <jdennis@redhat.com> 0.99.11-8.devel
- fix bug #129539, dovecot starts too early,
  set chkconfig to 65 35 to match cyrus-imapd
- also delete some old commented out code from SSL certificate creation

* Thu Dec 23 2004 John Dennis <jdennis@redhat.com> 0.99.11-7.devel
- add UW to Dovecot migration documentation and scripts, bug #139954
  fix SSL documentation and scripts, add missing documentation, bug #139276

* Fri Dec 17 2004 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 1.0-test58.

* Tue Dec  7 2004 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 1.0-test56.

* Mon Nov 15 2004 Warren Togami <wtogami@redhat.com> 0.99.11-2.FC4.1
- rebuild against MySQL4

* Thu Oct 21 2004 John Dennis <jdennis@redhat.com>
- fix bug #136623
  Change License field from GPL to LGPL to reflect actual license

* Thu Sep 30 2004 John Dennis <jdennis@redhat.com> 0.99.11-1.FC3.3
- fix bug #124786, listen to ipv6 as well as ipv4

* Wed Sep  8 2004 John Dennis <jdennis@redhat.com> 0.99.11-1.FC3.1
- bring up to latest upstream,
  comments from Timo Sirainen <tss at iki.fi> on release v0.99.11 2004-09-04  
  + 127.* and ::1 IP addresses are treated as secured with
    disable_plaintext_auth = yes
  + auth_debug setting for extra authentication debugging
  + Some documentation and error message updates
  + Create PID file in /var/run/dovecot/master.pid
  + home setting is now optional in static userdb
  + Added mail setting to static userdb
  - After APPENDing to selected mailbox Dovecot didn't always notice the
    new mail immediately which broke some clients
  - THREAD and SORT commands crashed with some mails
  - If APPENDed mail ended with CR character, Dovecot aborted the saving
  - Output streams sometimes sent data duplicated and lost part of it.
    This could have caused various strange problems, but looks like in
    practise it rarely caused real problems.

* Wed Aug  4 2004 John Dennis <jdennis@redhat.com>
- change release field separator from comma to dot, bump build number

* Mon Aug  2 2004 John Dennis <jdennis@redhat.com> 0.99.10.9-1,FC3,1
- bring up to date with latest upstream, fixes include:
- LDAP support compiles now with Solaris LDAP library
- IMAP BODY and BODYSTRUCTURE replies were wrong for MIME parts which
  didn't contain Content-Type header.
- MySQL and PostgreSQL auth didn't reconnect if connection was lost
  to SQL server
- Linking fixes for dovecot-auth with some systems
- Last fix for disconnecting client when downloading mail longer than
  30 seconds actually made it never disconnect client. Now it works
  properly: disconnect when client hasn't read _any_ data for 30
  seconds.
- MySQL compiling got broken in last release
- More PostgreSQL reconnection fixing


* Mon Jul 26 2004 John Dennis <jdennis@redhat.com> 0.99.10.7-1,FC3,1
- enable postgres and mySQL in build
- fix configure to look for mysql in alternate locations
- nuke configure script in tar file, recreate from configure.in using autoconf

- bring up to latest upstream, which included:
- Added outlook-pop3-no-nuls workaround to fix Outlook hang in mails with NULs.
- Config file lines can now contain quoted strings ("value ")
- If client didn't finish downloading a single mail in 30 seconds,
  Dovecot closed the connection. This was supposed to work so that
  if client hasn't read data at all in 30 seconds, it's disconnected.
- Maildir: LIST now doesn't skip symlinks


* Wed Jun 30 2004 John Dennis <jdennis@redhat.com>
- bump rev for build
- change rev for FC3 build

* Fri Jun 25 2004 John Dennis <jdennis@redhat.com> - 0.99.10.6-1
- bring up to date with upstream,
  recent change log comments from Timo Sirainen were:
  SHA1 password support using OpenSSL crypto library
  mail_extra_groups setting
  maildir_stat_dirs setting
  Added NAMESPACE capability and command
  Autocreate missing maildirs (instead of crashing)
  Fixed occational crash in maildir synchronization
  Fixed occational assertion crash in ioloop.c
  Fixed FreeBSD compiling issue
  Fixed issues with 64bit Solaris binary

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu May 27 2004 David Woodhouse <dwmw2@redhat.com> 0.99.10.5-1
- Update to 0.99.10.5 to fix maildir segfaults (#123022)

* Fri May 07 2004 Warren Togami <wtogami@redhat.com> 0.99.10.4-4
- default auth config that is actually usable
- Timo Sirainen (author) suggested functionality fixes
  maildir, imap-fetch-body-section, customflags-fix

* Mon Feb 23 2004 Tim Waugh <twaugh@redhat.com>
- Use ':' instead of '.' as separator for chown.

* Tue Feb 17 2004 Jeremy Katz <katzj@redhat.com> - 0.99.10.4-3
- restart properly if it dies (#115594)

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Nov 24 2003 Jeremy Katz <katzj@redhat.com> 0.99.10.4-1
- update to 0.99.10.4

* Mon Oct  6 2003 Jeremy Katz <katzj@redhat.com> 0.99.10-7
- another patch from upstream to fix returning invalid data on partial 
  BODY[part] fetches
- patch to avoid confusion of draft/deleted in indexes

* Tue Sep 23 2003 Jeremy Katz <katzj@redhat.com> 0.99.10-6
- add some patches from upstream (#104288)

* Thu Sep  4 2003 Jeremy Katz <katzj@redhat.com> 0.99.10-5
- fix startup with 2.6 with patch from upstream (#103801)

* Tue Sep  2 2003 Jeremy Katz <katzj@redhat.com> 0.99.10-4
- fix assert in search code (#103383)

* Tue Jul 22 2003 Nalin Dahyabhai <nalin@redhat.com> 0.99.10-3
- rebuild

* Thu Jul 17 2003 Bill Nottingham <notting@redhat.com> 0.99.10-2
- don't run by default

* Thu Jun 26 2003 Jeremy Katz <katzj@redhat.com> 0.99.10-1
- 0.99.10

* Mon Jun 23 2003 Jeremy Katz <katzj@redhat.com> 0.99.10-0.2
- 0.99.10-rc2 (includes ssl detection fix)
- a few tweaks from fedora
  - noreplace the config file
  - configure --with-ldap to get LDAP enabled

* Mon Jun 23 2003 Jeremy Katz <katzj@redhat.com> 0.99.10-0.1
- 0.99.10-rc1
- add fix for ssl detection
- add zlib-devel to BuildRequires
- change pam service name to dovecot
- include pam config

* Thu May  8 2003 Jeremy Katz <katzj@redhat.com> 0.99.9.1-1
- update to 0.99.9.1
- add patch from upstream to fix potential bug when fetching with 
  CR+LF linefeeds
- tweak some things in the initscript and config file noticed by the 
  fedora folks

* Sun Mar 16 2003 Jeremy Katz <katzj@redhat.com> 0.99.8.1-2
- fix ssl dir
- own /var/run/dovecot/login with the correct perms
- fix chmod/chown in post

* Fri Mar 14 2003 Jeremy Katz <katzj@redhat.com> 0.99.8.1-1
- update to 0.99.8.1

* Tue Mar 11 2003 Jeremy Katz <katzj@redhat.com> 0.99.8-2
- add a patch to fix quoting problem from CVS

* Mon Mar 10 2003 Jeremy Katz <katzj@redhat.com> 0.99.8-1
- 0.99.8
- add some buildrequires
- fixup to build with openssl 0.9.7
- now includes a pop3 daemon (off by default)
- clean up description and %%preun
- add dovecot user (uid/gid of 97)
- add some buildrequires
- move the ssl cert to %%{_datadir}/ssl/certs
- create a dummy ssl cert in %%post
- own /var/run/dovecot
- make the config file a source so we get default mbox locks of fcntl

* Sun Dec  1 2002 Seth Vidal <skvidal@phy.duke.edu>
- 0.99.4 and fix startup so it starts imap-master not vsftpd :)

* Tue Nov 26 2002 Seth Vidal <skvidal@phy.duke.edu>
- first build
