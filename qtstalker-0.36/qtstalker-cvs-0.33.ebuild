# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /cvsroot/qtstalker/qtstalker/qtstalker-cvs-0.33.ebuild,v 1.1 2006/02/05 21:48:58 sstratos Exp $

inherit cvs qt3 eutils

DESCRIPTION="Commodity and stock market charting and technical analysis"
HOMEPAGE="http://qtstalker.sourceforge.net/"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="x86 amd64"
IUSE=""

DEPEND="$(qt_min_version 3.3)"
RDEPEND=""

ECVS_SERVER="cvs.sourceforge.net:/cvsroot/qtstalker"
ECVS_MODULE="qtstalker"
ECVS_TOP_DIR="${DISTDIR}/cvs-src/${PN}"

S=${WORKDIR}/${ECVS_MODULE}

# linking erros about missing lqtstalker lib when -jX
# from MAKEOPTS is being set to anything higher than -j1
MAKEOPTS="${MAKEOPTS} -j1"

src_unpack() {
		ECVS_MODULE_QTSTALKER="${ECVS_MODULE}"
		cvs_src_unpack
		# cd ${S}
		# use perl && epatch ${FILESDIR}/${PN}-perl_plugin.patch
		# use python && epatch ${FILESDIR}/${PN}-python_plugin.patch
}            

src_compile() {
	einfo "Creating national language files in i18n..."
	${QTDIR}/bin/qmake -project -r -o qtstalker_single.pro ../qtstalker
	lupdate qtstalker_single.pro
	einfo "Done"
	einfo "Compiling existing translations..."
	lrelease i18n/qtstalker_??.ts
	einfo "Done"
	${QTDIR}/bin/qmake qtstalker.pro \
		QMAKE_CXXFLAGS_RELEASE="${CXXFLAGS}" \
		QMAKE_RPATH= \
		|| die "qmake qtstalker.pro failed"

		addwrite "${QTDIR}/etc/settings"

		emake || die "make failed"
}

src_install() {
	# we have to export this...
	export INSTALL_ROOT="${D}"
	einstall || die "make install failed"

	# install compressed doc
	cd ${S}/docs
	insinto /usr/share/doc/qtstalker
	gzip AUTHORS BUGS CHANGELOG INSTALL TODO ${S}/README
	doins *.gz ${S}/*.gz
		
	# install only needed langpacks
	cd ${S}/i18n
	insinto /usr/share/qtstalker/i18n
	for i in ${LINGUAS}; do
	    if [ -f ${PN}_${i}.qm ]; then
	        doins ${PN}_${i}.qm
	    fi
	done
}
