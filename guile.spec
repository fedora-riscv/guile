%define qthreads_archs i386 sparc
# Once 'as' is fixed on alpha, that arch should be added to qthreads_archs

Summary: A GNU implementation of Scheme for application extensibility.
Name: guile
Version: 1.6.4
Release: 18
Source: ftp://ftp.gnu.org/gnu/guile-%{version}.tar.gz
Source2: http://ai.king.net.pl/guile-1.6-missing-tools.tar.gz
Patch1: guile-1.6.0-libtool.patch
Patch2: guile-1.4.1-rpath.patch
Patch3: guile-1.6.0-unknown_arch.patch
Patch4: guile-1.6.0-ia64.patch
Patch5: guile-1.6.0-ppc64.patch
License: GPL
Group: Development/Languages
Buildroot: %{_tmppath}/%{name}-root
BuildPrereq: libtool
Prereq: /sbin/install-info
Prereq: readline
Prereq: slib >= 3a1-1
Epoch: 5

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
Requires: guile = %{epoch}:%{PACKAGE_VERSION}

%description devel
The guile-devel package includes the libraries, header files, etc.,
that you'll need to develop applications that are linked with the
GUILE extensibility library.

You need to install the guile-devel package if you want to develop
applications that will be linked to GUILE.  You'll also need to
install the guile package.

%prep
%setup -q
%patch1 -p1 -b .libtool
%patch2 -p1 -b .rpath
%patch3 -p1 -b .unknown_arch
%patch4 -p1 -b .ia64
%patch5 -p1 -b .ppc64

%build

WITH_THREADS=--with-threads
%ifnarch %{qthreads_archs}
WITH_THREADS=
%endif

%ifarch ia64
export CFLAGS="$RPM_OPT_FLAGS -O0"
%endif
%configure $WITH_THREADS

# Multilib fix for procedures.txt
perl -pi -e 's|threads.doc||' `find . -name Makefile`

make -C libguile scmconfig.h
# Ouch! guile forgets to set it's onw shard lib path to use shared uninstalled
# apps. It ain't pretty, but it works.
LD_LIBRARY_PATH="`pwd`/libguile/.libs:`pwd`/qt/.libs:`pwd`/libguile-ltdl/.libs" \
	make LDFLAGS="-L`pwd`/libguile/.libs"

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

# Convince guile to be packaged.
perl -p -i -e "s|^libdir.*|libdir='$RPM_BUILD_ROOT%{_libdir}'|g" \
        guile-readline/libguilereadline.la

perl -p -i -e "s|^relink_command.*||g" guile-readline/libguilereadline.la

%{makeinstall}

# Fix up libtool libraries.
find $RPM_BUILD_ROOT -name '*.la' | \
  xargs perl -p -i -e "s|$RPM_BUILD_ROOT||g"

chmod +x ${RPM_BUILD_ROOT}%{_libdir}/libguile.so.*
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/guile/site
ln -s ../../share/slib ${RPM_BUILD_ROOT}%{_datadir}/guile/slib
ln -s ../../share/slib/slibcat ${RPM_BUILD_ROOT}%{_datadir}/guile/slibcat
ln -sf 1.6 ${RPM_BUILD_ROOT}%{_datadir}/guile/%{version}

# Install additional scripts
tar zxvf %{SOURCE2}
pushd guile-1.6-missing-tools
cp -a scripts/* ${RPM_BUILD_ROOT}%{_datadir}/guile/%{version}/scripts
cp -a ice-9/* ${RPM_BUILD_ROOT}%{_datadir}/guile/%{version}/ice-9
popd

# Remove unpackaged files
rm -f ${RPM_BUILD_ROOT}%{_bindir}/guile-doc-snarf
rm -f ${RPM_BUILD_ROOT}%{_bindir}/guile-func-name-check
rm -f ${RPM_BUILD_ROOT}%{_bindir}/guile-snarf.awk
rm -rf ${RPM_BUILD_ROOT}/usr/include/guile-readline
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/info/dir

# Compress large documentation
bzip2 NEWS

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
/sbin/install-info  %{_infodir}/guile.info.gz %{_infodir}/dir
/sbin/install-info  %{_infodir}/r5rs.info.gz %{_infodir}/dir
/sbin/install-info  %{_infodir}/goops.info.gz %{_infodir}/dir

%postun
/sbin/ldconfig
/sbin/install-info --delete %{_infodir}/guile.info.gz %{_infodir}/dir
/sbin/install-info --delete %{_infodir}/r5rs.info.gz %{_infodir}/dir
/sbin/install-info --delete %{_infodir}/goops.info.gz %{_infodir}/dir

%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING ChangeLog GUILE-VERSION HACKING NEWS.bz2 README
%doc SNAPSHOTS ANON-CVS THANKS
%{_bindir}/guile
%{_bindir}/guile-tools
%{_libdir}/libguile.so.*
%{_libdir}/libguile-ltdl.so.*
%{_libdir}/libguilereadline-v-12.so.*
%{_libdir}/libguile-srfi-srfi-*.so.*
%ifarch %{qthreads_archs}
%{_libdir}/libqthreads.so.*
%endif
%dir %{_datadir}/guile
%dir %{_datadir}/guile/site
%{_datadir}/aclocal/*
%{_datadir}/guile/slib
%{_datadir}/guile/slibcat
%{_datadir}/guile/1.6
%{_infodir}/*

%files devel
%defattr(-,root,root,-)
%{_bindir}/guile-config
%{_bindir}/guile-snarf
%{_libdir}/libguile.a
%{_libdir}/libguile.la
%{_libdir}/libguile.so
%{_libdir}/libguile-ltdl.a
%{_libdir}/libguile-ltdl.la
%{_libdir}/libguile-ltdl.so
%{_libdir}/libguilereadline-*.a
%{_libdir}/libguilereadline-*.la
%{_libdir}/libguile-srfi-srfi-*.a
%{_libdir}/libguile-srfi-srfi-*.la
%ifarch %{qthreads_archs}
%{_libdir}/libqthreads.a
%{_libdir}/libqthreads.la
%{_libdir}/libqthreads.so
%endif
%{_includedir}/guile
%{_includedir}/libguile
%{_includedir}/libguile.h

%changelog
* Wed Jan 12 2005 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-18
- rebuilt because of new readline

* Thu Dec 23 2004 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-17
- Fixed wrong post and postun use of /sbin/ldconfig (#143657)

* Tue Dec 21 2004 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-16
- Moved info files to base package as they are not devel related (#139948)
- Moved static guilereadline and guile-srfi-srfi libs to devel package (#140893)
- Fixed guile-tools not finding guile lib dir (#142642)
- Added some nice tools (#142642)
- Removed smp build, seems to be broken atm

* Wed Dec  8 2004 Jindrich Novy <jnovy@redhat.com> 5:1.6.4-15
- remove dependency to umb-scheme and replace it by slib

* Tue Oct 12 2004 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-14
- Fix multilib support for guile

* Tue Aug 03 2004 Phil Knirsch <pknirsch@redhat.com>  5:1.6.4-13
- Enable optimization again for s390.

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Apr 16 2004 Warren Togami <wtogami@redhat.com> 5:1.6.4-11
- Fix post failure and duplicate rpm in database
- Compress NEWS
- other minor cleanups

* Wed Apr 14 2004 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-10
- Fixed info file stuff (#112487)

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Aug 27 2003 Bill Nottingham <notting@redhat.com> 5:1.6.4-8.2
- rebuild (#103148)

* Tue Aug 19 2003 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-8.1
- rebuilt

* Tue Aug 19 2003 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-8
- Moved dynamic loadable libraries out file devel into main (#98392).

* Wed Jul 02 2003 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-7.1
- rebuilt

* Wed Jul 02 2003 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-7
- Added srfi libs (#98392).

* Sun Jun  8 2003 Tim Powers <timp@redhat.com> 5:1.6.4-6.1
- add epoch for versioned requires
- built for RHEL

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri May 16 2003 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-5
- Bumped release and rebuilt.

* Fri May 16 2003 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-4
- Install and package info files, too.

* Fri May 16 2003 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-3
- Bumped release and rebuilt.

* Fri May 16 2003 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-2
- Fixed .la file problem, moved from devel to normal package.

* Tue May 06 2003 Phil Knirsch <pknirsch@redhat.com> 5:1.6.4-1
- Update to 1.6.4

* Thu Feb 13 2003 Elliot Lee <sopwith@redhat.com> 5:1.6.0-5
- Patch7 - fix for ppc64
- Fix qthreads dealie, including actually enabling them

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Fri Dec 06 2002 Phil Knirsch <pknirsch@redhat.com> 5:1.6.0-3
- Included s390 as working arch as well, switch to general unknown arch patch

* Tue Dec  3 2002 Tim Powers <timp@redhat.com> 5:1.6.0-2
- rebuild to fix broken deps
- fix continuations.h on ia64

* Tue Dec 03 2002 Phil Knirsch <pknirsch@redhat.com> 1.6.0-1
- Make it build on x86_64.
- Integrated and fixed Than's update to 1.6.0.
- Fixed some things in the %files section.

* Mon Nov 11 2002 Than Ngo <timp@redhat.com> 1.4.1-2
- fix to build on s390*/x86_64 -> include libguilereadline.so
- fix to link libltdl
- don't use rpath

* Thu Nov 07 2002 Phil Knirsch <pknirsch@redhat.com> 1.4.1-1
- Updated to guile-1.4.1
- libguilereadline.so doesn't work on x86_64 yet, so don't package it.

* Wed Nov 06 2002 Phil Knirsch <pknirsch@redhat.com> 1.4-10
- Fixed unpackaged files.

* Tue Nov  5 2002 Bill Nottingham <notting@redhat.com> 1.4-9
- Remove qthread from x86_64 as well.

* Wed Jul 17 2002 Phil Knirsch <pknirsch@redhat.com> 1.4-8
- Remove qthread from ppc as well.

* Wed Jul 10 2002 Phil Knirsch <pknirsch@redhat.com> 1.4-7
- Fixed some more %file lib related errors ().

* Fri Jun 21 2002 Tim Powers <timp@redhat.com> 1.4-6
- automated rebuild

* Wed Jun 19 2002 Phil Knirsch <pknirsch@redhat.com> 1.4-5
- Don't forcibly strip binaries

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Mon May 06 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- adjust for mainframe and alpha

* Fri Jan 25 2002 Bill Nottingham <notting@redhat.com>
- ship qthread devel links too

* Fri Jan 25 2002 Phil Knirsch <pknirsch@redhat.com>
- Update again to 1.4.
- Disable --with-threads for IA64 as it doesn't work.

* Thu Jan 24 2002 Phil Knirsch <pknirsch@redhat.com> 1.3.4-17/4
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
