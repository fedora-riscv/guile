Summary: A GNU implementation of Scheme for application extensibility
Name: guile
%define mver 1.8
Version: 1.8.5
Release: 1%{?dist}
Source: ftp://ftp.gnu.org/pub/gnu/guile/guile-%{version}.tar.gz
URL: http://www.gnu.org/software/guile/
Patch1: guile-1.8.4-multilib.patch
Patch2: guile-1.8.4-testsuite.patch
Patch3: guile-1.8.5-conts.patch
Patch4: guile-1.8.1-deplibs.patch
License: GPLv2+ and LGPLv2+
Group: Development/Languages
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: libtool libtool-ltdl-devel gmp-devel readline-devel
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info
Requires: coreutils
Epoch: 5

%description
GUILE (GNU's Ubiquitous Intelligent Language for Extension) is a library
implementation of the Scheme programming language, written in C.  GUILE
provides a machine-independent execution platform that can be linked in
as a library during the building of extensible programs.

Install the guile package if you'd like to add extensibility to programs
that you are developing.

%package devel
Summary: Libraries and header files for the GUILE extensibility library
Group: Development/Libraries
Requires: guile = %{epoch}:%{version} gmp-devel
Requires: pkgconfig

%description devel
The guile-devel package includes the libraries, header files, etc.,
that you'll need to develop applications that are linked with the
GUILE extensibility library.

You need to install the guile-devel package if you want to develop
applications that will be linked to GUILE.  You'll also need to
install the guile package.

%prep
%setup -q
%patch1 -p1 -b .multilib
%patch2 -p1 -b .testsuite
%patch3 -p1 -b .conts
%patch4 -p1 -b .deplibs

%build

%configure --disable-static --disable-error-on-warning

# Remove RPATH
sed -i 's|" $sys_lib_dlsearch_path "|" $sys_lib_dlsearch_path %{_libdir} "|' \
    {,guile-readline/}libtool

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

make DESTDIR=$RPM_BUILD_ROOT install

mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/guile/site

rm -f ${RPM_BUILD_ROOT}%{_libdir}/libguile*.la
rm -f ${RPM_BUILD_ROOT}%{_infodir}/dir

# Compress large documentation
bzip2 NEWS

for i in $RPM_BUILD_ROOT%{_infodir}/goops.info; do
    iconv -f iso8859-1 -t utf-8 < $i > $i.utf8 && mv -f ${i}{.utf8,}
done

touch $RPM_BUILD_ROOT%{_datadir}/guile/%{mver}/slibcat
ln -s ../../slib $RPM_BUILD_ROOT%{_datadir}/guile/%{mver}/slib

%check
make %{?_smp_mflags} check

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
/sbin/install-info  %{_infodir}/guile.info.gz %{_infodir}/dir
/sbin/install-info  %{_infodir}/r5rs.info.gz %{_infodir}/dir
/sbin/install-info  %{_infodir}/goops.info.gz %{_infodir}/dir
/sbin/install-info  %{_infodir}/guile-tut.info.gz %{_infodir}/dir
:

%postun -p /sbin/ldconfig

%preun
if [ "$1" = 0 ]; then
    /sbin/install-info --delete %{_infodir}/guile.info.gz %{_infodir}/dir
    /sbin/install-info --delete %{_infodir}/r5rs.info.gz %{_infodir}/dir
    /sbin/install-info --delete %{_infodir}/goops.info.gz %{_infodir}/dir
    /sbin/install-info --delete %{_infodir}/guile-tut.info.gz %{_infodir}/dir
fi
:

%triggerin -- slib
# Remove files created in guile < 1.8.3-2
rm -f %{_datadir}/guile/site/slib{,cat}

ln -sfT ../../slib %{_datadir}/guile/%{mver}/slib
rm -f %{_datadir}/guile/%{mver}/slibcat
export SCHEME_LIBRARY_PATH=%{_datadir}/slib/
umask 0022

# Build SLIB catalog
for pre in \
    "(use-modules (ice-9 slib))" \
    "(load \"%{_datadir}/slib/guile.init\")"
do
    %{_bindir}/guile -c "$pre
        (set! implementation-vicinity (lambda () \"%{_datadir}/guile/%{mver}/\"))
        (require 'new-catalog)" &> /dev/null && break
    rm -f %{_datadir}/guile/%{mver}/slibcat
done
:

%triggerun -- slib
if [ "$2" = 0 ]; then
    rm -f %{_datadir}/guile/%{mver}/slib{,cat}
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING* ChangeLog HACKING NEWS.bz2 README THANKS
%{_bindir}/guile
%{_bindir}/guile-tools
%{_libdir}/libguile*.so.*
%{_libdir}/libguilereadline-*.so
%{_libdir}/libguile-srfi-srfi-*.so
%dir %{_datadir}/guile
%dir %{_datadir}/guile/%{mver}
%{_datadir}/guile/%{mver}/ice-9
%{_datadir}/guile/%{mver}/lang
%{_datadir}/guile/%{mver}/oop
%{_datadir}/guile/%{mver}/scripts
%{_datadir}/guile/%{mver}/srfi
%{_datadir}/guile/%{mver}/guile-procedures.txt
%ghost %{_datadir}/guile/%{mver}/slibcat
%ghost %{_datadir}/guile/%{mver}/slib
%dir %{_datadir}/guile/site
%{_infodir}/*

%files devel
%defattr(-,root,root,-)
%{_bindir}/guile-config
%{_bindir}/guile-snarf
%{_datadir}/aclocal/*
%{_libdir}/libguile.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/guile
%{_includedir}/libguile
%{_includedir}/libguile.h

%changelog
* Wed Jul 23 2008 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.5-1.fc8
- update to 1.8.5
- fix continuations on ia64

* Tue Apr 15 2008 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.4-1
- update to 1.8.4
- add %%check
- support slib-3a5
- move slibcat and slib symlink out of site directory
- set umask in scriptlet (#242936)

* Wed Aug 22 2007 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.2-2
- update license tag
- redirect guile output in triggerin script

* Tue Jul 17 2007 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.2-1
- update to 1.8.2
- remove dot from -devel summary, convert goops.info to UTF-8

* Mon Mar 19 2007 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.1-3
- spec cleanup

* Tue Jan 23 2007 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.1-2
- support slib-3a4
- make scriptlets safer (#223701)

* Fri Oct 13 2006 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.1-1
- update to 1.8.1

* Tue Sep 05 2006 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.0-8.20060831cvs
- make triggerin scriptlet a bit safer

* Fri Sep 01 2006 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.0-7.20060831cvs
- update from CVS

* Wed Jul 12 2006 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.0-6.20060712cvs
- update from CVS
- fix requires (#196016)
- link libguile with pthread (#198215)

* Wed May 24 2006 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.0-5
- remove dependency on slib, provide support through triggers
- fix multilib -devel conflicts in guile-snarf and scmconfig.h (#192684)

* Thu May 18 2006 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.0-4
- add gmp-devel to requires for devel package (#192107)
- fix guile-config link (#191595)

* Tue May 16 2006 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.0-3
- don't package .la files and static libraries (#191595)
- move module .so files from devel to main package

* Tue May 09 2006 Bill Nottingham <notting@redhat.com> - 5:1.8.0-2
- don't package %%{_infodir}/dir

* Tue May 09 2006 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.8.0-1
- update to guile-1.8.0
- fix slib.scm for slib-3a3
- install guile-tut info
- move guile.m4 to devel package
- spec cleanup

* Tue Feb 28 2006 Miroslav Lichvar <mlichvar@redhat.com> - 5:1.6.7-6
- move .la files for modules from devel to main package (#182242)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 5:1.6.7-5.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 5:1.6.7-5.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Feb 06 2006 Miroslav Lichvar <mlichvar@redhat.com> 5:1.6.7-5
- Avoid marking qthreads library as requiring executable stack (#179274)

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Sep 02 2005 Phil Knirsch <pknirsch@redhat.com> 5:1.6.7-4
- Fix dynamic linking on 64bit archs (#159971)

* Wed Mar 02 2005 Phil Knirsch <pknirsch@redhat.com> 5:1.6.7-2
- bump release and rebuild with gcc 4
- Fixed problem with ltdl and gcc 4 rebuild
- Add BuildPreReq for libtool-ltdl-devel

* Wed Feb 09 2005 Phil Knirsch <pknirsch@redhat.com> 5:1.6.7-1
- Update to guile-1.6.7
- Dropped ia64 patch, stuff looks fixed in upstream code

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
- Fixed some things in the %%files section.

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
- Fixed some more %%file lib related errors ().

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
- Fixed %%files bug #20134 where the /usr/lib/libguilereadline.so didn't get
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
- readline is needed for %%post

* Tue Feb  8 2000 Nalin Dahyabhai <nalin@redhat.com>
- use the same catalog as umb-scheme

* Thu Sep  2 1999 Jeff Johnson <jbj@redhat.com>
- fix broken %%postun

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
- added %%attr(-, root, root) for %%doc, 
- in %%post, %%postun ldconfig runed as parameter "-p",
- removed /bin/sh from requires,
- added %%description,
- changes in %%files.

* Fri Jul 11 1997 Tomasz Koczko <kloczek@rudy.mif.pg.gda.pl>  (1.2-2)
- all rewrited for using Buildroot,
- added %%postun,
- removed making buid logs,
- removed "--inclededir", added "--enable-dynamic-linking" to configure
  parameters,
- added striping shared libs and /usr/bin/guile,
- added "Requires: /bin/sh" (for guile-snarf) in guile package and
  "Requires: m4" for guile-devel,
- added macro %%{PACKAGE_VERSION} in "Source:" and %%files,
- added %%attr macros in %%files.
