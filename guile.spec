Summary: A GNU implementation of Scheme for application extensibility.
Name: guile
Version: 1.3.4
Release: 19a
Source: ftp://ftp.gnu.org/gnu/guile-%{version}.tar.gz
URL: http://www.gnu.org/software/guile
Patch: guile-1.3.4-inet_aton.patch
Patch1: guile-1.3.4-sizet.patch
License: GPL
Group: Development/Languages
Buildroot: %{_tmppath}/%{name}-root
Prereq: /sbin/install-info, readline, umb-scheme >= 3.2-21
Epoch: 3

%description
GUILE (GNU's Ubiquitous Intelligent Language for Extension) is a library
implementation of the Scheme programming language, written in C.  GUILE
provides a machine-independent execution platform that can be linked in
as a library during the building of extensible programs.

Install the guile package if you'd like to add extensibility to programs
that you are developing.

%package devel
Summary: Libraries and header files for the GUILE extensibility library.
Group: Development/Libraries
Requires: guile = %{PACKAGE_VERSION}

%description devel
The guile-devel package includes the libraries, header files, etc.,
that you'll need to develop applications that are linked with the
GUILE extensibility library.

You need to install the guile-devel package if you want to develop
applications that will be linked to GUILE.  You'll also need to
install the guile package.

%prep
%setup -q
%patch -p1 -b .inet_aton
%patch1 -p1 -b .sizet

%build
%ifarch ia64 alpha s390 s390x
%ifarch ia64
libtoolize --copy --force
export CFLAGS="-O0"
%endif
%configure
%else
%configure --with-threads
%endif
make

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%{makeinstall}

strip ${RPM_BUILD_ROOT}%{_bindir}/guile
chmod +x ${RPM_BUILD_ROOT}%{_libdir}/libguile.so.*.0.0
gzip -9nf ${RPM_BUILD_ROOT}%{_infodir}/data-rep*
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/guile/site
ln -s ../../share/umb-scheme/slib ${RPM_BUILD_ROOT}%{_datadir}/guile/slib
ln -s ../../share/umb-scheme/slibcat ${RPM_BUILD_ROOT}%{_datadir}/guile/slibcat

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig

%postun -p /sbin/ldconfig

%post devel
/sbin/install-info %{_infodir}/data-rep.info.gz %{_infodir}/dir

%preun devel
if [ "$1" = 0 ]; then
    /sbin/install-info --delete %{_infodir}/data-rep.info.gz %{_infodir}/dir
fi

%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog GUILE-VERSION HACKING NEWS README TODO
%doc SNAPSHOTS ANON-CVS THANKS
%{_bindir}/guile
%{_libdir}/libguilereadline*
%{_libdir}/libguile.so.*
%ifnarch ia64 alpha s390 s390x
%{_libdir}/libqthreads.so.*
%endif
%dir %{_datadir}/guile
%dir %{_datadir}/guile/site
%dir %{_datadir}/guile/%{PACKAGE_VERSION}
%{_datadir}/guile/%{PACKAGE_VERSION}/ice-9
%{_datadir}/aclocal/*
%{_datadir}/guile/slib
%{_datadir}/guile/slibcat

%files devel
%defattr(-,root,root)
%{_bindir}/guile-config
%{_bindir}/guile-snarf
%ifnarch ia64 alpha s390 s390x
%{_libdir}/libqthreads.so
%endif
%{_libdir}/libguile.so
%{_libdir}/libguile.a
%{_includedir}/guile
%{_includedir}/libguile
%{_includedir}/libguile.h
%{_infodir}/data-rep*

%changelog
* Wed Apr 03 2002 Phil Knirsch <pknirsch@redhat.com> 1.3.4-19/3
- Added missing libqthreads.so for devel package.

* Tue Mar 26 2002 Phil Knirsch <pknirsch@redhat.com> 1.3.4-18/3
- Removed --with-threads on all but i386 as it doesn't work.
- Added URL tag (#61582)
- Copyright: -> License:

* Thu Jan 24 2002 Phil Knirsch <pknirsch@redhat.com> 1.3.4-17/3
- Enabled --with-threads and removed --enable-dynamic-linking for configure
  (bug #58597)

* Mon Sep  3 2001 Philipp Knirsch <pknirsch@redhat.de> 1.3.4-16/3
- Fixed problem with read-only /usr pollution of /usr/share/umb-scheme/slibcat
  (#52742)

* Wed Aug 22 2001 Philipp Knirsch <pknirsch@redhat.de> 1.3.4-15/2
- Fixed /tmp buildroot pollution (#50398)

* Mon Jun 12 2001 Florian La Roche <Florian.LaRoche@redhat.de> 1.3.4-14/1
- size_t patch from <oliver.paukstadt@millenux.com>

* Fri May 11 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.3.4-13/1
- Rebuild with new readline

* Wed Feb 28 2001 Philipp Knirsch <pknirsch@redhat.de>
- Fixed missing devel version dependancy.
- Fixed bug #20134 for good this time.

* Mon Jan 22 2001 Than Ngo <than@redhat.com>
- disable optimization on ia64 (compiler bug) (bug #23186)

* Tue Dec 12 2000 Philipp Knirsch <Philipp.Knirsch@redhat.de>
- Fixed %files bug #20134 where the /usr/lib/libguilereadline.so didn't get
  installed for the non devel version.

* Fri Jul 14 2000 Nalin Dahyabhai <nalin@redhat.com>
- Add version number to prereq for umb-scheme to get the post-install to
  work properly.

* Thu Jul 13 2000 Nalin Dahyabhai <nalin@redhat.com>
- Add an Epoch = 1 in case anyone happened to have 1.4 installed.

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Tue Jul 11 2000 Nalin Dahyabhai <nalin@redhat.com>
- Back down to 1.3.4.
- Fix to actually link against the version of libguile in the package.

* Sun Jun  4 2000 Nalin Dahyabhai <nalin@redhat.com>
- FHS fixups using the %%{makeinstall} macro.

* Sun Mar 26 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- fix preun-devel
- call ldconfig directly in postun

* Fri Mar 24 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- rebuild with new readline
- update to 1.3.4

* Mon Feb 28 2000 Nalin Dahyabhai <nalin@redhat.com>
- using the same catalog as umb-scheme makes umb-scheme a prereq

* Thu Feb 17 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- readline is needed for %post

* Tue Feb  8 2000 Nalin Dahyabhai <nalin@redhat.com>
- use the same catalog as umb-scheme

* Thu Sep  2 1999 Jeff Johnson <jbj@redhat.com>
- fix broken %postun

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 6)

* Wed Mar 17 1999 Michael Johnson <johnsonm@redhat.com>
- added .ansi patch to fix #endif

* Wed Feb 10 1999 Cristian Gafton <gafton@redhat.com>
- add patch for the scm stuff

* Sun Jan 17 1999 Jeff Johnson <jbj@redhat.com>
- integrate changes from rhcn version (#640)

* Tue Jan 12 1999 Cristian Gafton <gafton@redhat.com>
- call libtoolize first to get it to compile on the arm

* Sat Jan  9 1999 Todd Larason <jtl@molehill.org>
- Added "Requires: guile" at suggestion of Manu Rouat <emmanuel.rouat@wanadoo.fr>

* Fri Jan  1 1999 Todd Larason <jtl@molehill.org>
- guile-devel does depend on guile
- remove devel dependancy on m4
- move guile-snarf from guile to guile-devel
- Converted to rhcn

* Wed Oct 21 1998 Jeff Johnson <jbj@redhat.com>
- update to 1.3.
- don't strip libguile.so.*.0.0. (but set the execute bits).

* Thu Sep 10 1998 Cristian Gafton <gafton@redhat.com>
- spec file fixups

* Wed Sep  2 1998 Michael Fulbright <msf@redhat.com>
- Updated for RH 5.2

* Mon Jan 26 1998 Marc Ewing <marc@redhat.com>
- Started with spec from Tomasz Koczko <kloczek@idk.com.pl>
- added slib link

* Thu Sep 18 1997 Tomasz Koczko <kloczek@idk.com.pl>          (1.2-3)
- added %attr(-, root, root) for %doc, 
- in %post, %postun ldconfig runed as parameter "-p",
- removed /bin/sh from requires,
- added %description,
- changes in %files.

* Fri Jul 11 1997 Tomasz Koczko <kloczek@rudy.mif.pg.gda.pl>  (1.2-2)
- all rewrited for using Buildroot,
- added %postun,
- removed making buid logs,
- removed "--inclededir", added "--enable-dynamic-linking" to configure
  parameters,
- added striping shared libs and /usr/bin/guile,
- added "Requires: /bin/sh" (for guile-snarf) in guile package and
  "Requires: m4" for guile-devel,
- added macro %{PACKAGE_VERSION} in "Source:" and %files,
- added %attr macros in %files.
