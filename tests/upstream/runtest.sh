#!/bin/bash
# vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /CoreOS/guile/Sanity/upstream
#   Description: Upstream test suite
#   Author: Petr Splichal <psplicha@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2011 Red Hat, Inc. All rights reserved.
#
#   This copyrighted material is made available to anyone wishing
#   to use, modify, copy, or redistribute it subject to the terms
#   and conditions of the GNU General Public License version 2.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free
#   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301, USA.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include Beaker environment
. /usr/bin/rhts-environment.sh
. /usr/lib/beakerlib/beakerlib.sh

PACKAGE="guile"

rlJournalStart
    rlPhaseStartSetup
        rlAssertRpm $PACKAGE
        rlRun "TmpDir=\`mktemp -d\`" 0 "Creating tmp directory"
        rlRun "pushd $TmpDir"

        # fetch tests
        rlRun "rlFetchSrcForInstalled $PACKAGE" 0 "Fetching the source rpm"
        rlRun "rpm --define '_topdir $TmpDir' -i *src.rpm" \
                0 "Installing the source rpm"
        rlRun "mkdir BUILD" 0 "Creating BUILD directory"
        rlRun "rpmbuild --nodeps --define '_topdir $TmpDir' \
                -bc $TmpDir/SPECS/*spec" 0 "Preparing sources"
        rlRun "pushd BUILD/guile*"
    rlPhaseEnd

    rlPhaseStartTest
        rlRun "make check" 0 "Dry run of the test suite"
        rlRun "ln -snf /usr/bin/guile libguile/guile" \
                0 "Replacing built guile interpreter with system binary"
        rlRun "pushd test-suite"
        rlRun "make check" 0 "Running the test suite"
        rlRun "popd"
    rlPhaseEnd

    rlPhaseStartCleanup
        rlRun "popd"
        rlRun "rm -r $TmpDir" 0 "Removing tmp directory"
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
