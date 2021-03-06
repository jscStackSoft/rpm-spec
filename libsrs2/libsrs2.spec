#
# $Id: aterm.spec,v 1.4 2003/09/24 04:23:47 heinlein Exp $
# $Source: /home/heinlein/projects/specs/RCS/aterm.spec,v $
#
# rpm spec file for aterm
#

Summary: SRS email address rewriting engine
Name: libsrs2
Version: 1.0.18
Release: 3%{?redhatvers:.%{redhatvers}}
License: GPL
Group: System Environment/Libraries
Packager: Shevek <srs@anarres.org>
URL: http://www.libsrs2.org/
Source: http://www.libsrs2.org/srs/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-root

%description
libsrs2 is the next generation SRS library. SPF verifies that the
Sender address of a mail matches (according to some policy) the
client IP address which submits the mail. When a mail is forwarded,
the sender address must be rewritten to comply with SPF policy. The
Sender Rewriting Scheme, or SRS, provides a standard for this
rewriting which is not vulnerable to attacks by spammers.

%package devel
Summary: Libraries and headers for %{name}
Group: Development/Libraries

%description devel
This package contains necessary header files for libsrs2 development.

%prep
%setup -q

%build
CFLAGS="%{optflags}" \
./configure --prefix=%{_prefix} 
make %{?_smp_mflags} RPM_OPT_FLAGS="$RPM_OPT_FLAGS"


%install
if [ ! $RPM_BUILD_ROOT = "/" ]; then
	%{__rm} -rf $RPM_BUILD_ROOT;
	mkdir -p $RPM_BUILD_ROOT%{_prefix}/bin
	mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib
fi
make DESTDIR=%{buildroot} install


%clean
if [ ! %{buildroot} = "/" ]; then %{__rm} -rf %{buildroot}; fi


%files
%defattr(-,root,root)
%doc ChangeLog INSTALL README NEWS AUTHORS COPYING
/usr/lib/libsrs2.so*
/usr/lib/libsrs2.a
/usr/lib/libsrs2.la
%{_bindir}/srs

%files devel
%defattr(-,root,root,-)
%{_prefix}/include/srs2.h
