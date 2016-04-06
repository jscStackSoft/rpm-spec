%bcond_with rhel4
%bcond_with pam_stack
%bcond_with systemd
%bcond_with libdb

Summary: The exim mail transfer agent
Name: exim
Version: 4.86.2
Release: 2%{?dist}
License: GPLv2+
Url: http://www.exim.org/
Group: System Environment/Daemons
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root
Provides: MTA smtpd smtpdaemon server(smtp)
Requires(post): /sbin/restorecon %{_sbindir}/alternatives
Requires(preun): %{_sbindir}/alternatives
Requires(pre): %{_sbindir}/groupadd, %{_sbindir}/useradd
Requires(postun): %{_sbindir}/alternatives
%if %{with systemd}
Requires(post): systemd systemd-sysv
Requires(preun): systemd
Requires(postun): systemd
%else
Requires(post): /sbin/chkconfig /sbin/service
Requires(preun): /sbin/chkconfig /sbin/service
%endif
Source0: ftp://ftp.exim.org/pub/exim/exim4/old/exim-%{version}.tar.gz
Source2: exim.init
Source3: exim.sysconfig
Source4: exim.logrotate
Source5: exim-tidydb.sh
Source11: exim.pam-system-auth
Source211: exim.pam-stacked
Source311: exim.pam
Source20: exim-greylist.conf.inc
Source21: mk-greylist-db.sql
Source22: greylist-tidy.sh
Source23: trusted-configs
Source24: exim.service
Source25: exim-gen-cert

#Patch1: localscan_dlopen_exim_4.20_or_better.patch
Patch4: exim-rhl.patch
Patch6: exim-4.80-config.patch
Patch7: exim-4.80.1-config-atrpms.patch
Patch9: exim-4.73-pcre.patch
Patch8: exim-4.24-libdir.patch
Patch12: exim-4.33-cyrus.patch
#Patch13: exim-4.63-pamconfig.patch
Patch13: exim-4.43-pamconfig.patch
Patch14: exim-4.50-spamdconf.patch
Patch18: exim-4.71-dlopen-localscan.patch
Patch19: exim-4.63-procmail.patch
Patch20: exim-4.63-allow-filter.patch
Patch21: exim-4.63-localhost-is-local.patch
Patch22: exim-4.66-greylist-conf.patch
Patch23: exim-4.67-smarthost-config.patch
Patch25: exim-4.69-dynlookup-config.patch

%if ! %{with rhel4}
Requires: /etc/pki/tls/certs /etc/pki/tls/private
%endif
Requires: /etc/aliases
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
%if %{with libdb}
BuildRequires: libdb-devel
%else
BuildRequires: db4-devel
%endif
BuildRequires: openssl-devel openldap-devel pam-devel
BuildRequires: pcre-devel sqlite-devel perl-ExtUtils-Embed
BuildRequires: cyrus-sasl-devel openldap-devel openssl-devel
BuildRequires: /usr/include/tcpd.h
BuildRequires: mysql-devel, postgresql-devel
BuildRequires: libXaw-devel libXmu-devel libXext-devel libX11-devel libSM-devel
BuildRequires: libICE-devel libXpm-devel libXt-devel
%if %{with systemd}
BuildRequires: systemd-units
%endif
BuildRequires: libgsasl-devel
BuildRequires: libspf2-devel, libsrs2-devel
BuildRequires: libdomainkeys-devel libdomainkeys

Obsoletes: exim-sysvinit


%description
Exim is a message transfer agent (MTA) developed at the University of
Cambridge for use on Unix systems connected to the Internet. It is
freely available under the terms of the GNU General Public Licence. In
style it is similar to Smail 3, but its facilities are more
general. There is a great deal of flexibility in the way mail can be
routed, and there are extensive facilities for checking incoming
mail. Exim can be installed in place of sendmail, although the
configuration of exim is quite different to that of sendmail.

%package mysql
Summary: MySQL lookup support for Exim
Group: System Environment/Daemons
Requires: exim = %{version}-%{release}

%description mysql
This package contains the MySQL lookup module for Exim

%package pgsql
Summary: PostgreSQL lookup support for Exim
Group: System Environment/Daemons
Requires: exim = %{version}-%{release}

%description pgsql
This package contains the PostgreSQL lookup module for Exim

%package mon
Summary: X11 monitor application for Exim
Group: Applications/System

%description mon
The Exim Monitor is an optional supplement to the Exim package. It
displays information about Exim's processing in an X window, and an
administrator can perform a number of control actions from the window
interface.

%package greylist
Summary: Example configuration for greylisting using Exim
Group: System Environment/Daemons
Requires: sqlite exim %{_sysconfdir}/cron.daily

%description greylist
This package contains a simple example of how to do greylisting in Exim's
ACL configuration. It contains a cron job to remove old entries from the
greylisting database, and an ACL subroutine which needs to be included
from the main exim.conf file.

To enable greylisting, install this package and then uncomment the lines
in Exim's configuration /etc/exim.conf which enable it. You need to
uncomment at least two lines -- the '.include' directive which includes
the new ACL subroutine, and the line which invokes the new subroutine.

By default, this implementation only greylists mails which appears
'suspicious' in some way. During normal processing of the ACLs we collect
a list of 'offended' which it's committed, which may include having
SpamAssassin points, lacking a Message-ID: header, coming from a blacklisted
host, etc. There are examples of these in the default configuration file,
mostly commented out. These should be sufficient for you to you trigger
greylisting for whatever 'offences' you can dream of, or even to make 
greylisting unconditional.

%prep
%setup -q
# patch sa
#patch1 -p1 -b .localscan_dlopen_exim

%patch4 -p1 -b .rhl
%patch6 -p1 -b .config
%patch8 -p1 -b .libdir
%patch12 -p1 -b .cyrus
%patch13 -p1 -b .pam
%patch14 -p1 -b .spamd
%patch18 -p1 -b .dl
%patch19 -p1 -b .procmail
%patch20 -p1 -b .filter
%patch21 -p1 -b .localhost
%patch22 -p1 -b .grey
%patch23 -p1 -b .smarthost
%patch25 -p1 -b .dynconfig

%patch7 -p1 -b .moreconfig

cp src/EDITME Local/Makefile
%patch9 -p1 -b .pcre

sed -i 's@^# LOOKUP_MODULE_DIR=.*@LOOKUP_MODULE_DIR=%{_libdir}/exim/%{version}-%{release}/lookups@' Local/Makefile
sed -i 's@^# AUTH_LIBS=-lsasl2@AUTH_LIBS=-lsasl2@' Local/Makefile
cp exim_monitor/EDITME Local/eximon.conf


%build
%ifnarch s390 s390x sparc sparcv9 sparcv9v sparc64 sparc64v
	export PIE=-fpie
%else
	export PIE=-fPIE
%endif
#make CFLAGS="$RPM_OPT_FLAGS -DSPF -DSRS $PIE" LFLAGS=-pie _lib=%{_lib} FULLECHO=
make LFLAGS=-pie _lib=%{_lib} FULLECHO=

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_sbindir}
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_libdir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/exim

cd build-`scripts/os-type`-`scripts/arch-type`
install -m 4775 exim $RPM_BUILD_ROOT%{_sbindir}

for i in eximon eximon.bin exim_dumpdb exim_fixdb exim_tidydb \
	exinext exiwhat exim_dbmbuild exicyclog exim_lock \
	exigrep eximstats exipick exiqgrep exiqsumm \
	exim_checkaccess convert4r4
do
	install -m 0755 $i $RPM_BUILD_ROOT%{_sbindir}
done

mkdir -p $RPM_BUILD_ROOT%{_libdir}/exim/%{version}-%{release}/lookups
for i in mysql.so pgsql.so
do 
	install -m755 lookups/$i \
	 $RPM_BUILD_ROOT%{_libdir}/exim/%{version}-%{release}/lookups
done

cd ..

install -m 0644 src/configure.default $RPM_BUILD_ROOT%{_sysconfdir}/exim/exim.conf
%if %{with pam_stack}
install -m 0644 %SOURCE211 $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/exim
%else
if test -f %{_sysconfdir}/pam.d/password-auth; then
  install -m 0644 %SOURCE311 $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/exim
else
  install -m 0644 %SOURCE11 $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/exim
fi
%endif

mkdir -p $RPM_BUILD_ROOT/usr/lib
pushd $RPM_BUILD_ROOT/usr/lib
ln -sf ../sbin/exim sendmail.exim
popd

pushd $RPM_BUILD_ROOT%{_sbindir}/
ln -sf exim sendmail.exim
popd

pushd $RPM_BUILD_ROOT%{_bindir}/
ln -sf ../sbin/exim mailq.exim
ln -sf ../sbin/exim runq.exim
ln -sf ../sbin/exim rsmtp.exim
ln -sf ../sbin/exim rmail.exim
ln -sf ../sbin/exim newaliases.exim
popd

install -d -m 0750 $RPM_BUILD_ROOT%{_var}/spool/exim
install -d -m 0750 $RPM_BUILD_ROOT%{_var}/spool/exim/db
install -d -m 0750 $RPM_BUILD_ROOT%{_var}/spool/exim/input
install -d -m 0750 $RPM_BUILD_ROOT%{_var}/spool/exim/msglog
install -d -m 0750 $RPM_BUILD_ROOT%{_var}/log/exim

mkdir -p $RPM_BUILD_ROOT%{_mandir}/man8
install -m644 doc/exim.8 $RPM_BUILD_ROOT%{_mandir}/man8/exim.8
pod2man --center=EXIM --section=8 \
       $RPM_BUILD_ROOT/usr/sbin/eximstats \
       $RPM_BUILD_ROOT%{_mandir}/man8/eximstats.8

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 644 %SOURCE3 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/exim

%if ! %{with systemd}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
install %SOURCE2 $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/exim
%endif

%if %{with systemd}
# Systemd
mkdir -p %{buildroot}%{_unitdir}
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}
install -m644 %{SOURCE24} %{buildroot}%{_unitdir}
install -m755 %{SOURCE25} %{buildroot}%{_libexecdir}
%endif

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -m 0644 %SOURCE4 $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/exim

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily
install -m 0755 %SOURCE5 $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/exim-tidydb

# generate ghost .pem file
mkdir -p $RPM_BUILD_ROOT/etc/pki/tls/{certs,private}
touch $RPM_BUILD_ROOT/etc/pki/tls/{certs,private}/exim.pem
chmod 600 $RPM_BUILD_ROOT/etc/pki/tls/{certs,private}/exim.pem

# generate alternatives ghosts
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
for i in %{_sbindir}/sendmail %{_bindir}/{mailq,runq,rsmtp,rmail,newaliases} \
       /usr/lib/sendmail %{_sysconfdir}/pam.d/smtp %{_mandir}/man1/mailq.1.gz
do
       touch $RPM_BUILD_ROOT$i
done

# Set up the greylist subpackage
install -m644 %{SOURCE20} $RPM_BUILD_ROOT/%_sysconfdir/exim/exim-greylist.conf.inc
install -m644 %{SOURCE21} $RPM_BUILD_ROOT/%_sysconfdir/exim/mk-greylist-db.sql
mkdir -p $RPM_BUILD_ROOT/%_sysconfdir/cron.daily
install -m755 %{SOURCE22} $RPM_BUILD_ROOT/%_sysconfdir/cron.daily/greylist-tidy.sh
install -m644 %{SOURCE23} $RPM_BUILD_ROOT/%_sysconfdir/exim/trusted-configs
touch $RPM_BUILD_ROOT/%_var/spool/exim/db/greylist.db

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%{_sbindir}/groupadd -g 93 exim 2>/dev/null
%{_sbindir}/useradd -d %{_var}/spool/exim -s /sbin/nologin -G mail -M -r -u 93 -g exim exim 2>/dev/null
# Copy TLS certs from old location to new -- don't move them, because the
# config file may be modified and may be pointing to the old location.
if [ ! -f /etc/pki/tls/certs/exim.pem -a -f %{_datadir}/ssl/certs/exim.pem ] ; then
   cp -a %{_datadir}/ssl/certs/exim.pem /etc/pki/tls/certs/exim.pem
   cp -a %{_datadir}/ssl/private/exim.pem /etc/pki/tls/private/exim.pem
fi
exit 0

%post
%if %{with systemd}
%systemd_post %{name}.service
%else
/sbin/chkconfig --add exim
%endif

%{_sbindir}/alternatives --install %{_sbindir}/sendmail mta %{_sbindir}/sendmail.exim 10 \
	--slave %{_bindir}/mailq mta-mailq %{_bindir}/mailq.exim \
	--slave %{_bindir}/runq mta-runq %{_bindir}/runq.exim \
	--slave %{_bindir}/rsmtp mta-rsmtp %{_bindir}/rsmtp.exim \
	--slave %{_bindir}/rmail mta-rmail %{_bindir}/rmail.exim \
	--slave /etc/pam.d/smtp mta-pam /etc/pam.d/exim \
	--slave %{_bindir}/newaliases mta-newaliases %{_bindir}/newaliases.exim \
	--slave /usr/lib/sendmail mta-sendmail /usr/lib/sendmail.exim \
	--slave %{_mandir}/man1/mailq.1.gz mta-mailqman %{_mandir}/man8/exim.8.gz \
	--initscript exim

%preun
%if %{with systemd}
%systemd_preun %{name}.service
%endif
if [ $1 = 0 ]; then
%if ! %{with systemd}
	/sbin/service exim stop > /dev/null 2>&1
	/sbin/chkconfig --del exim
%endif
	%{_sbindir}/alternatives --remove mta %{_sbindir}/sendmail.exim
fi

%postun
%if %{with systemd}
%systemd_postun_with_restart %{name}.service
%endif
if [ $1 -ge 1 ]; then
%if ! %{with systemd}
	/sbin/service exim  condrestart > /dev/null 2>&1
%endif
        mta=`readlink /etc/alternatives/mta`
        if [ "$mta" == "%{_sbindir}/sendmail.exim" ]; then
                /usr/sbin/alternatives --set mta %{_sbindir}/sendmail.exim
        fi
fi

%global sysv2systemdnvr 4.76-6

%if %{with systemd}
%triggerun -- exim < %{sysv2systemdnvr}
%{_bindir}/systemd-sysv-convert --save exim >/dev/null 2>&1 ||:
/bin/systemctl enable exim.service >/dev/null 2>&1
/sbin/chkconfig --del exim >/dev/null 2>&1 || :
/bin/systemctl try-restart exim.service >/dev/null 2>&1 || :
%else
%triggerpostun -- exim < %{sysv2systemdnvr}
/sbin/chkconfig --add exim >/dev/null 2>&1 || :
%endif

%post greylist
if [ ! -r %{_var}/spool/exim/db/greylist.db ]; then
   sqlite3 %{_var}/spool/exim/db/greylist.db < %{_sysconfdir}/exim/mk-greylist-db.sql
   chown exim.exim %{_var}/spool/exim/db/greylist.db
   chmod 0660 %{_var}/spool/exim/db/greylist.db
fi

%files
%defattr(-,root,root)
%attr(4755,root,root) %{_sbindir}/exim
%{_sbindir}/exim_dumpdb
%{_sbindir}/exim_fixdb
%{_sbindir}/exim_tidydb
%{_sbindir}/exinext
%{_sbindir}/exiwhat
%{_sbindir}/exim_dbmbuild
%{_sbindir}/exicyclog
%{_sbindir}/exigrep
%{_sbindir}/eximstats
%{_sbindir}/exipick
%{_sbindir}/exiqgrep
%{_sbindir}/exiqsumm
%{_sbindir}/exim_lock
%{_sbindir}/exim_checkaccess
%{_sbindir}/convert4r4
%{_sbindir}/sendmail.exim
%{_bindir}/mailq.exim
%{_bindir}/runq.exim
%{_bindir}/rsmtp.exim
%{_bindir}/rmail.exim
%{_bindir}/newaliases.exim
/usr/lib/sendmail.exim
%{_mandir}/*/*
%dir %{_libdir}/exim
%dir %{_libdir}/exim/%{version}-%{release}
%dir %{_libdir}/exim/%{version}-%{release}/lookups

%defattr(-,exim,exim)
%dir %{_var}/spool/exim
%dir %{_var}/spool/exim/db
%dir %{_var}/spool/exim/input
%dir %{_var}/spool/exim/msglog
%dir %{_var}/log/exim

%defattr(-,root,root)
%dir %{_sysconfdir}/exim
%config(noreplace) %{_sysconfdir}/exim/exim.conf
%config(noreplace) %{_sysconfdir}/exim/trusted-configs
%config(noreplace) %{_sysconfdir}/sysconfig/exim
%if %{with systemd}
%{_unitdir}/exim.service
%{_libexecdir}/exim-gen-cert
%else
%{_sysconfdir}/rc.d/init.d/exim
%endif
%config(noreplace) %{_sysconfdir}/logrotate.d/exim
%config(noreplace) %{_sysconfdir}/pam.d/exim
%{_sysconfdir}/cron.daily/exim-tidydb

%doc ACKNOWLEDGMENTS LICENCE NOTICE README.UPDATING README 
%doc doc util/unknownuser.sh

%if %{with rhel4}
%dir /etc/pki
%dir /etc/pki/tls
%dir /etc/pki/tls/certs
%dir /etc/pki/tls/private
%endif
%attr(0600,root,root) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) /etc/pki/tls/certs/exim.pem
%attr(0600,root,root) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) /etc/pki/tls/private/exim.pem

%attr(0755,root,root) %ghost %{_sbindir}/sendmail
%attr(0755,root,root) %ghost %{_bindir}/mailq
%attr(0755,root,root) %ghost %{_bindir}/runq
%attr(0755,root,root) %ghost %{_bindir}/rsmtp
%attr(0755,root,root) %ghost %{_bindir}/rmail
%attr(0755,root,root) %ghost %{_bindir}/newaliases
%attr(0755,root,root) %ghost /usr/lib/sendmail
%ghost %{_sysconfdir}/pam.d/smtp
%ghost %{_mandir}/man1/mailq.1.gz

%files mysql
%defattr(-,root,root,-)
%{_libdir}/exim/%{version}-%{release}/lookups/mysql.so

%files pgsql
%defattr(-,root,root,-)
%{_libdir}/exim/%{version}-%{release}/lookups/pgsql.so

%files mon
%defattr(-,root,root)
%{_sbindir}/eximon
%{_sbindir}/eximon.bin

%files greylist
%defattr(-,root,root,-)
%config %{_sysconfdir}/exim/exim-greylist.conf.inc
%ghost %{_var}/spool/exim/db/greylist.db
%{_sysconfdir}/exim/mk-greylist-db.sql
%{_sysconfdir}/cron.daily/greylist-tidy.sh

%changelog
* Wed May 15 2013 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.80.1-49
- Update to 4.80.1.

* Fri Oct 28 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.77-48
- Update to 4.77.

* Tue May 10 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.76-47
- Update to 4.76.

* Thu May  5 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.75-46
- Update to 4.75.
- pcre-prerelease patch is upstream now.

* Sun Feb 12 2011 John Robinson <john.robinson@yuiop.co.uk> - 4.73-45
- Update to 4.74.

* Tue Jan 11 2011 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.73-42
- Update to 4.73.

* Fri Jul  2 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.72-41
- Update to 4.72.
- Sync with F13: alternatives support and init script.

* Sun Feb 14 2010 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.71-40
- Sync with rawhide.

* Tue Nov 24 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.71-39
- Update to 4.71.

* Mon Nov 16 2009 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.70-38
- Sync with rawhide.
- Update to 4.70.

* Tue Jul 22 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.69-34
- Sync with rawhide.

* Thu Jan 10 2008 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.69-33
- Update to 4.69.

* Sun Apr 22 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.67-32
- Update to 4.67.

* Sun Apr  1 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.66-31
- Sync with rawhide, but not the clamav subpackage.

* Mon Feb 12 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.66-30
- Use required pam_stack when include is not available (#1127).

* Wed Jan 17 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.66-29
- Update to 4.66.

* Tue Jan  2 2007 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.65-28
- Update to 4.65.

* Wed Dec 20 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.64-27
- Update to 4.64.

* Sun Aug 13 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.63-26
- Adjust pamconfig patch.

* Tue Aug  1 2006 Axel Thimm <Axel.Thimm@ATrpms.net> - 4.63-25
- Update to 4.63.

* Wed Jul 19 2006 Thomas Woerner <twoerner@redhat.com> - 4.62-6
- final version
- changed permissions of /etc/pki/tls/*/exim.pem to 0600
- config(noreplace) for /etc/logrotate.d/exim, /etc/pam.d/exim and
  /etc/sysconfig/exim

* Mon Jul 17 2006 Thomas Woerner <twoerner@redhat.com> - 4.62-5
- fixed certs path
- fixed permissions for some binaries
- fixed pam file to use include instead of pam_stack

* Fri May  5 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 4.62.

* Fri Apr  7 2006 David Woodhouse <dwmw2@redhat.com> 4.61-2
- Define LDAP_DEPRECATED to ensure ldap functions are all declared.

* Tue Apr  4 2006 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 4.61.

* Tue Mar 21 2006 David Woodhouse <dwmw2@redhat.com> 4.60-4
- Actually enable Postgres

* Sun Dec  4 2005 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 4.60.

* Wed Oct  5 2005 David Woodhouse <dwmw2@redhat.com> 4.54-1
- Update to Exim 4.54
- Enable sqlite support

* Thu Aug 25 2005 David Woodhouse <dwmw2@redhat.com> 4.52-2
- Use system PCRE

* Mon Jul  4 2005 Axel Thimm <Axel.Thimm@ATrpms.net>
- Add domainkeys support.

* Sat Jul  2 2005 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 4.52.

* Thu Jun 16 2005 David Woodhouse <dwmw2@redhat.com> 4.51-2
- Update CSA patch

* Thu May  5 2005 Axel Thimm <Axel.Thimm@ATrpms.net>
- Update to 4.51.

* Wed May  4 2005 David Woodhouse <dwmw2@redhat.com>
- Include Tony's CSA support patch

* Tue Feb 22 2005 David Woodhouse <dwmw2@redhat.com> 4.50-2
- Move exim-doc into a separate package

* Tue Feb 22 2005 David Woodhouse <dwmw2@redhat.com> 4.50-1
- Update to Exim 4.50 and sa-exim 4.2
- Default headers_charset to utf-8
- Add sample spamd stuff to default configuration like exiscan-acl used to

* Sat Feb 12 2005 Axel Thimm <Axel.Thimm@ATrpms.net>
- Add spf/srs support.

* Sat Jan 15 2005 David Woodhouse <dwmw2@redhat.com> 4.44-1
- Update to Exim 4.44 and exiscan-acl-4.44-28

* Fri Jan  7 2005 Axel Thimm <Axel.Thimm@ATrpms.net>
- Enable mysql lookups.

* Tue Jan  4 2005 David Woodhouse <dwmw2@redhat.com> 4.43-4
- Fix buffer overflows in host_aton() and SPA authentication

* Thu Dec 16 2004 David Woodhouse <dwmw2@redhat.com> 4.43-3
- Demonstrate SASL auth configuration in default config file
- Enable TLS and provide certificate if necessary
- Don't reject all GB2312 charset mail by default

* Thu Oct  7 2004 Thomas Woerner <twoerner@redhat.com> 4.43-1
- new version 4.43 with sasl support
- new exiscan-acl-4.43-28
- new config.samples and FAQ-html (added publication date)
- new BuildRequires for cyrus-sasl-devel openldap-devel openssl-devel
  and PreReq for cyrus-sasl openldap openssl

* Fri Aug 27 2004 Thomas Woerner <twoerner@redhat.com> 4.42-1
- new version 4.42

* Mon Aug  2 2004 Thomas Woerner <twoerner@redhat.com> 4.41-1
- new version 4.41

* Fri Jul  2 2004 Thomas Woerner <twoerner@redhat.com> 4.34-3
- added pre-definition of local_delivery using Cyrus-IMAP (#122912)
- added BuildRequires for pam-devel (#124555)
- fixed format string bugs (#125117)
- fixed sa-exim code placed wrong in spec file (#127102)
- extended postun with alternatives call

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed May 12 2004 David Woodhouse <dwmw2@redhat.com> 4.34-1
- Update to Exim 4.34, exiscan-acl 4.34-21

* Sat May 8 2004 David Woodhouse <dwmw2@redhat.com> 4.33-2
- fix buffer overflow in header_syntax check

* Wed May 5 2004 David Woodhouse <dwmw2@redhat.com> 4.33-1
- Update to Exim 4.33, exiscan-acl 4.33-20 to
  fix crashes both in exiscan-acl and Exim itself.

* Fri Apr 30 2004 David Woodhouse <dwmw2@redhat.com> 4.32-2
- Enable IPv6 support, Cyrus saslauthd support, iconv.

* Thu Apr 15 2004 David Woodhouse <dwmw2@redhat.com> 4.32-1
- update to Exim 4.32, exiscan-acl 4.32-17, sa-exim 4.0
- Fix Provides: and Source urls.
- include exiqgrep, exim_checkaccess, exipick
- require /etc/aliases instead of setup

* Tue Feb 24 2004 Thomas Woerner <twoerner@redhat.com> 4.30-6.1
- rebuilt

* Mon Feb 23 2004 Tim Waugh <twaugh@redhat.com>
- Use ':' instead of '.' as separator for chown.

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sun Feb  8 2004 Axel Thimm <Axel.Thimm@ATrpms.net>
- Fix localscan_dlopen config.
- Split sa-exim into its own package.

* Tue Jan 27 2004 Thomas Woerner <twoerner@redhat.com> 4.30-5
- /usr/lib/sendmail is in alternatives, now
- /etc/alises is now in setup: new Requires for setup >= 2.5.31-1

* Tue Jan 13 2004 Thomas Woerner <twoerner@redhat.com> 4.30-4
- fixed group test in init script
- fixed config patch: use /etc/exim/exim.conf instead of /usr/exim/exim4.conf

* Wed Dec 10 2003 Nigel Metheringham <Nigel.Metheringham@InTechnology.co.uk> - 4.30-3
- Use exim.8 manpage from upstream
- Add eximstats.8 man page (from pod)
- Fixed mailq(1) man page alternatives links

* Mon Dec 08 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- do not package /etc/aliases. We currently require sendmail rpm until
  /etc/aliases moves into a more suitable rpm like "setup" or something else.

* Thu Dec  4 2003 Thomas Woerner <twoerner@redhat.com> 4.30-1
- new version 4.30
- new exiscan-acl-4.30-14
- disabled pie for s390 and s390x

* Wed Dec  3 2003 Tim Waugh <twaugh@redhat.com>
- Fixed PIE support to make it actually work.

* Wed Dec  3 2003 Thomas Woerner <twoerner@redhat.com> 4.24-1.2
- added -fPIE to CFLAGS

* Sat Nov 15 2003 Thomas Woerner <twoerner@redhat.com> 4.24-1.1
- fixed useradd in pre
- fixed alternatives in post

* Thu Nov 13 2003 Thomas Woerner <twoerner@redhat.com> 4.24-1
- new version 4.24 with LDAP and perl support
- added SpamAssassin sa plugin

* Mon Sep 23 2002 Bernhard Rosenkraenzer <bero@redhat.com> 3.36-1
- 3.36, fixes security bugs

* Thu Jun 21 2001 Tim Waugh <twaugh@redhat.com> 3.22-14
- Bump release number.

* Tue Jun 12 2001 Tim Waugh <twaugh@redhat.com> 3.22-13
- Remove pam-devel build dependency in order to share package between
  Guinness and Seawolf.

* Fri Jun  8 2001 Tim Waugh <twaugh@redhat.com> 3.22-12
- Fix format string bug.

* Wed May  2 2001 Tim Waugh <twaugh@redhat.com> 3.22-11
- SIGALRM patch from maintainer (bug #20908).
- There's no README.IPV6 any more (bug #32378).
- Fix logrotate entry for exim's pidfile scheme (bug #35436).
- ignore_target_hosts crash fix from maintainer.
- Make the summary start with a capital letter.
- Add reload entry to initscript; use $0 in strings.

* Sun Mar  4 2001 Tim Waugh <twaugh@redhat.com> 3.22-10
- Make sure db ownership is correct on upgrade, since we don't run as
  root when running as a daemon any more.

* Fri Mar  2 2001 Tim Powers <timp@redhat.com>
- rebuilt against openssl-0.9.6-1

* Sat Feb 17 2001 Tim Waugh <twaugh@redhat.com>
- Run as user mail, group mail when we drop privileges (bug #28193).

* Tue Feb 13 2001 Tim Powers <timp@redhat.com>
- added conflict with postfix

* Thu Jan 25 2001 Tim Waugh <twaugh@redhat.com>
- Avoid using zero-length salt in crypteq expansion.

* Tue Jan 23 2001 Tim Waugh <twaugh@redhat.com>
- Redo initscript internationalisation.
- Initscript uses bash not sh.

* Mon Jan 22 2001 Tim Waugh <twaugh@redhat.com>
- Okay, the real bug was in libident.

* Mon Jan 22 2001 Tim Waugh <twaugh@redhat.com>
- Revert the RST patch for now; if it's needed, it's a pidentd bug
  and should be fixed there.

* Mon Jan 22 2001 Tim Waugh <twaugh@redhat.com>
- 3.22.
- Build requires XFree86-devel.

* Mon Jan 15 2001 Tim Waugh <twaugh@redhat.com>
- New-style prereqs.
- Initscript internationalisation.

* Thu Jan 11 2001 Tim Waugh <twaugh@redhat.com>
- Security patch no longer required; 3.20 and later have a hide feature
  to do the same thing.
- Mark exim.conf noreplace.
- Better libident (RST) patch.

* Wed Jan 10 2001 Tim Waugh <twaugh@redhat.com>
- Fix eximconfig so that it tells the user the correct place to look
  for documentation
- Fix configure.default to deliver mail as group mail so that local
  delivery works

* Tue Jan 09 2001 Tim Waugh <twaugh@redhat.com>
- 3.21

* Mon Jan 08 2001 Tim Waugh <twaugh@redhat.com>
- Enable TLS support (bug #23196)

* Mon Jan 08 2001 Tim Waugh <twaugh@redhat.com>
- 3.20 (bug #21895).  Absorbs configure.default patch
- Put URLs in source tags where applicable
- Add build requirement on pam-devel

* Wed Oct 18 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Fix up eximconfig's header generation (we're not Debian), Bug #18068
- BuildRequires db2-devel (Bug #18089)
- Fix typo in logrotate script (Bug #18308)
- Local delivery must be setuid to work (Bug #18314)
- Don't send TCP RST packages to ident (Bug #19048)

* Wed Oct 18 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 3.16
- fix security bug
- some specfile cleanups
- fix handling of RPM_OPT_FLAGS

* Fri Aug 18 2000 Tim Powers <timp@redhat.com>
- fixed bug #16535, logrotate script changes

* Thu Aug 17 2000 Tim Powers <timp@redhat.com>
- fixed bug #16460
- fixed bug #16458
- fixed bug #16476

* Wed Aug 2 2000 Tim Powers <timp@redhat.com>
- fixed bug #15142

* Fri Jul 28 2000 Than Ngo <than@redhat.de>
- add missing restart function in startup script
- add rm -rf $RPM_BUILD_ROOT in install section
- use %%{_tmppath}

* Fri Jul 28 2000 Tim Powers <timp@redhat.com>
- fixed initscript so that condrestart doesn't return 1 when the test fails

* Mon Jul 24 2000 Prospector <prospector@redhat.com>
- rebuilt

* Mon Jul 17 2000 Tim Powers <timp@redhat.com>
- inits bakc to rc.d/init.d, using service to start inits

* Thu Jul 13 2000 Tim Powers <timp@redhat.com>
- applied patch from bug #13890

* Mon Jul 10 2000 Tim Powers <timp@redhat.com>
- rebuilt

* Thu Jul 06 2000 Tim Powers <timp@redhat.com>
- added patch submitted by <Chris.Keane@comlab.ox.ac.uk>, fixes bug #13539

* Thu Jul 06 2000 Tim Powers <timp@redhat.com>
- fixed broken prereq to require /etc/init.d

* Tue Jun 27 2000 Tim Powers <timp@redhat.com>
- PreReq initscripts >= 5.20

* Mon Jun 26 2000 Tim Powers <timp@redhat.com>
- fix init.d script location
- add condrestart to init.d script

* Wed Jun 14 2000 Nalin Dahyabhai <nalin@redhat.com>
- migrate to system-auth setup

* Tue Jun 6 2000 Tim Powers <timp@redhat.com>
- fixed man page location

* Tue May 9 2000 Tim Powers <timp@redhat.com>
- rebuilt for 7.0

* Fri Feb 04 2000 Tim Powers <timp@redhat.com>
- fixed the groups to be in Red Hat groups.
- removed Vendor header since it is going to be marked Red Hat in our build
	system.
- quiet setups
- strip binaries
- fixed so that man pages can be auto gzipped by new RPM (in files list
	/usr/man/*/* )
- built for Powertools 6.2

* Tue Jan 18 2000 Mark Bergsma <mark@mbergsma.demon.nl>
- Upgraded to exim 3.13
- Removed i386 specialization
- Added syslog support

* Wed Dec 8 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Upgraded to exim 3.12
- Procmail no longer used as the delivery agent

* Wed Dec 1 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Upgraded to exim 3.11

* Sat Nov 27 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added /etc/pam.d/exim

* Wed Nov 24 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Upgraded to exim 3.10

* Thu Nov 11 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added eximconfig script, thanks to Mark Baker
- Exim now uses the Berkeley DB library.

* Fri Aug 4 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Upgraded to version 3.03
- Removed version number out of the spec file name.

* Fri Jul 23 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added embedded Perl support.
- Added tcp_wrappers support.
- Added extra documentation in a new doc subpackage.

* Mon Jul 12 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added /usr/sbin/sendmail as a link to exim.
- Fixed wrong filenames in logrotate entry. 

* Sun Jul 11 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Now using the '%%changelog' tag.
- Removed the SysV init links - let chkconfig handle them. 
- Replaced install -d with mkdir -p

* Sat Jul 10 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Fixed owner of the exim-mon files - the owner is now root

* Thu Jul 08 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Removed executable permission bits of /etc/exim.conf
- Removed setuid permission bits of all programs except exim
- Changed spool/log directory owner/groups to 'mail'
- Changed the default configuration file to make exim run
      as user and group 'mail'.

* Thu Jul 08 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added the /usr/bin/rmail -> /usr/sbin/exim symlink.
- Added the convert4r3 script.
- Added the transport-filter.pl script to the documentation.

* Thu Jul 08 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added procmail transport and director, and made that the
      default.
- Added the unknownuser.sh script to the documentation.

* Thu Jul 08 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added manpage for exim.
- Fixed symlinks pointing to targets under Buildroot.
- The exim logfiles will now only be removed when uninstalling,
      not upgrading.

* Wed Jul 07 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added 'Obsoletes' header.
- Added several symlinks to /usr/sbin/exim.

* Wed Jul 07 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- First RPM packet release.
- Not tested on other architectures/OS'es than i386/Linux..
