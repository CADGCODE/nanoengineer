#!/bin/sh -x

# Usage: Run ./buildMac.sh from the packaging directory.

DIST_VERSION=NanoEngineer-1_1.0.0b2

# Set up path variables
cd ..
TOP_LEVEL=`pwd`
DIST_ROOT=$TOP_LEVEL/cad/src/dist
DIST_CONTENTS=$DIST_ROOT/NanoEngineer-1.app/Contents

# Build the base .app directory contents
if [ ! -e "$TOP_LEVEL/cad/src" ]; then exit; fi
cd $TOP_LEVEL/cad/src
sudo rm -rf dist build
cp $TOP_LEVEL/packaging/MacOSX/setup.py .
python setup.py py2app --frameworks=/usr/local/BerkeleyDB.4.5/lib/libdb-4.5.dylib,/usr/local/lib/libopenbabel.1.0.2.dylib,/usr/local/lib/openbabel/APIInterface.so,/usr/local/lib/openbabel/CSRformat.so,/usr/local/lib/openbabel/PQSformat.so,/usr/local/lib/openbabel/alchemyformat.so,/usr/local/lib/openbabel/amberformat.so,/usr/local/lib/openbabel/balstformat.so,/usr/local/lib/openbabel/bgfformat.so,/usr/local/lib/openbabel/boxformat.so,/usr/local/lib/openbabel/cacaoformat.so,/usr/local/lib/openbabel/cacheformat.so,/usr/local/lib/openbabel/carformat.so,/usr/local/lib/openbabel/cccformat.so,/usr/local/lib/openbabel/chem3dformat.so,/usr/local/lib/openbabel/chemdrawformat.so,/usr/local/lib/openbabel/chemtoolformat.so,/usr/local/lib/openbabel/cmlreactlformat.so,/usr/local/lib/openbabel/copyformat.so,/usr/local/lib/openbabel/crkformat.so,/usr/local/lib/openbabel/cssrformat.so,/usr/local/lib/openbabel/dmolformat.so,/usr/local/lib/openbabel/fastsearchformat.so,/usr/local/lib/openbabel/featformat.so,/usr/local/lib/openbabel/fhformat.so,/usr/local/lib/openbabel/fingerprintformat.so,/usr/local/lib/openbabel/freefracformat.so,/usr/local/lib/openbabel/gamessformat.so,/usr/local/lib/openbabel/gaussformat.so,/usr/local/lib/openbabel/ghemicalformat.so,/usr/local/lib/openbabel/gromos96format.so,/usr/local/lib/openbabel/hinformat.so,/usr/local/lib/openbabel/inchiformat.so,/usr/local/lib/openbabel/jaguarformat.so,/usr/local/lib/openbabel/mdlformat.so,/usr/local/lib/openbabel/mmodformat.so,/usr/local/lib/openbabel/mmpformat.so,/usr/local/lib/openbabel/mol2format.so,/usr/local/lib/openbabel/mopacformat.so,/usr/local/lib/openbabel/mpdformat.so,/usr/local/lib/openbabel/mpqcformat.so,/usr/local/lib/openbabel/nwchemformat.so,/usr/local/lib/openbabel/pcmodelformat.so,/usr/local/lib/openbabel/pdbformat.so,/usr/local/lib/openbabel/povrayformat.so,/usr/local/lib/openbabel/pubchem.so,/usr/local/lib/openbabel/qchemformat.so,/usr/local/lib/openbabel/reportformat.so,/usr/local/lib/openbabel/rxnformat.so,/usr/local/lib/openbabel/shelxformat.so,/usr/local/lib/openbabel/smilesformat.so,/usr/local/lib/openbabel/tinkerformat.so,/usr/local/lib/openbabel/turbomoleformat.so,/usr/local/lib/openbabel/unichemformat.so,/usr/local/lib/openbabel/viewmolformat.so,/usr/local/lib/openbabel/xcmlformat.so,/usr/local/lib/openbabel/xedformat.so,/usr/local/lib/openbabel/xmlformat.so,/usr/local/lib/openbabel/xyzformat.so,/usr/local/lib/openbabel/yasaraformat.so,/usr/local/lib/openbabel/zindoformat.so --includes=sip --packages=ctypes,bsddb3 --iconfile ../../packaging/MacOSX/nanorex.icns || exit 1
if [ ! -e "$DIST_CONTENTS/Resources/lib/python2.3/lib-dynload/PyQt4/QtOpenGL.so" ]; then exit; fi
cp $TOP_LEVEL/packaging/MacOSX/py2app-Info.plist $DIST_CONTENTS/Info.plist
cd $TOP_LEVEL

# Copy the GAMESS helper script
mkdir $DIST_CONTENTS/bin
cp $TOP_LEVEL/cad/src/rungms $DIST_CONTENTS/bin/
if [ ! -e "$DIST_CONTENTS/bin/rungms" ]; then exit; fi

# Build and copy NanoDynamics-1
cd $TOP_LEVEL/sim/src
cp $TOP_LEVEL/packaging/MacOSX/ND1-Makefile ./Makefile
make clean || exit 1
make || exit 1
make pyx || exit 1
cp simulator $DIST_CONTENTS/bin/
if [ ! -e "$DIST_CONTENTS/bin/simulator" ]; then exit; fi
cp sim.so $DIST_CONTENTS/bin/
if [ ! -e "$DIST_CONTENTS/bin/sim.so" ]; then exit; fi
cd $TOP_LEVEL

# Copy the gnuplot and AquaTerm binaries
cp /usr/local/bin/gnuplot $DIST_CONTENTS/bin/
cp -R /Applications/AquaTerm.app $DIST_CONTENTS/bin/
cp -R /Library/Frameworks/AquaTerm.framework $DIST_CONTENTS/Frameworks/
if [ ! -e "$DIST_CONTENTS/Frameworks/AquaTerm.framework" ]; then exit; fi

# Copy and arrange the OpenBabel binaries
cp /usr/local/bin/babel $DIST_CONTENTS/bin/ || exit 1
cd $DIST_CONTENTS/Frameworks
ln -s libopenbabel.1.0.2.dylib libopenbabel.1.dylib
mkdir openbabel || exit 1
mv *format.so openbabel/
mv APIInterface.so openbabel/
mv pubchem.so openbabel/
cd $TOP_LEVEL

# Copy the doc/ files
mkdir $DIST_CONTENTS/doc
cp cad/doc/keyboardshortcuts-mac.htm $DIST_CONTENTS/doc/
cp cad/doc/mousecontrols-mac.htm $DIST_CONTENTS/doc/

# Copy partlib tree to a user-visible location and make a symbolic link to it
# for NE1 to use.
cp -R $TOP_LEVEL/cad/partlib $DIST_ROOT/
cd $DIST_CONTENTS
ln -s ../../partlib partlib
if [ ! -e "$DIST_CONTENTS/partlib" ]; then exit; fi
cd $TOP_LEVEL

# Copy images
cd $TOP_LEVEL
DIST_IMAGES_DIR=$DIST_CONTENTS/src/ui/
mkdir -p $DIST_IMAGES_DIR/actions
cp -R cad/src/ui/actions/Edit $DIST_IMAGES_DIR/actions/ 
cp -R cad/src/ui/actions/File $DIST_IMAGES_DIR/actions/
cp -R cad/src/ui/actions/Help $DIST_IMAGES_DIR/actions/
cp -R cad/src/ui/actions/Insert $DIST_IMAGES_DIR/actions/
cp -R cad/src/ui/actions/Properties\ Manager $DIST_IMAGES_DIR/actions/
cp -R cad/src/ui/actions/Simulation $DIST_IMAGES_DIR/actions/
cp -R cad/src/ui/actions/Toolbars $DIST_IMAGES_DIR/actions/
cp -R cad/src/ui/actions/Tools $DIST_IMAGES_DIR/actions/
cp -R cad/src/ui/actions/View $DIST_IMAGES_DIR/actions/
cp -R cad/src/ui/border $DIST_IMAGES_DIR
cp -R cad/src/ui/confcorner $DIST_IMAGES_DIR
cp -R cad/src/ui/cursors $DIST_IMAGES_DIR
cp -R cad/src/ui/dialogs $DIST_IMAGES_DIR
cp -R cad/src/ui/exprs $DIST_IMAGES_DIR
cp -R cad/src/ui/images $DIST_IMAGES_DIR
cp -R cad/src/ui/modeltree $DIST_IMAGES_DIR
cd $TOP_LEVEL

# Copy the ReadeMe.html file and Licenses/ files
cp $TOP_LEVEL/cad/src/ReadMe.html $DIST_ROOT/
mkdir $DIST_ROOT/Licenses
cp $TOP_LEVEL/cad/src/LICENSE $DIST_ROOT/Licenses/NanoEngineer-1_License.txt
cp $TOP_LEVEL/cad/licenses-common/Gnuplot_License $DIST_ROOT/Licenses/Gnuplot_License.txt
cp $TOP_LEVEL/cad/licenses-common/NanoKids_Attribution $DIST_ROOT/Licenses/NanoKids_Attribution.txt
cp $TOP_LEVEL/cad/licenses-common/OpenGL_License.doc $DIST_ROOT/Licenses/
cp $TOP_LEVEL/cad/licenses-common/OpenGL_LicenseOverview $DIST_ROOT/Licenses/OpenGL_LicenseOverview.txt
cp $TOP_LEVEL/cad/licenses-common/PyOpenGL_License $DIST_ROOT/Licenses/PyOpenGL_License.txt
cp $TOP_LEVEL/cad/licenses-common/Python_License $DIST_ROOT/Licenses/Python_License.txt
cp $TOP_LEVEL/cad/licenses-Mac/AquaTerm_License $DIST_ROOT/Licenses/AquaTerm_License.txt
cp $TOP_LEVEL/cad/licenses-Mac/PyQt_License $DIST_ROOT/Licenses/PyQt_License.txt
cp $TOP_LEVEL/cad/licenses-Mac/Qt_License $DIST_ROOT/Licenses/Qt_License.txt
cp $TOP_LEVEL/packaging/MacOSX/ctypes_License.txt $DIST_ROOT/Licenses/
cp $TOP_LEVEL/packaging/MacOSX/numarray_License.txt $DIST_ROOT/Licenses/
cp $TOP_LEVEL/packaging/MacOSX/NumPy_License.txt $DIST_ROOT/Licenses/
cp $TOP_LEVEL/packaging/MacOSX/PythonImagingLibrary_License.txt $DIST_ROOT/Licenses/
cp $TOP_LEVEL/packaging/MacOSX/OracleBerkeleyDB_License.txt $DIST_ROOT/Licenses/
cp $TOP_LEVEL/packaging/MacOSX/bsddb3_License.txt $DIST_ROOT/Licenses/
cp $TOP_LEVEL/packaging/MacOSX/OpenBabel_License.txt $DIST_ROOT/Licenses/

# Plugins
#
mkdir $DIST_CONTENTS/plugins

# Build and copy the CoNTub plugin
#cd $TOP_LEVEL/cad/plugins/CoNTub
#make
#cp -R ../CoNTub $DIST_CONTENTS/plugins/
#if [ ! -e "$DIST_CONTENTS/plugins/CoNTub/bin/HJ" ]; then exit; fi
#cd $TOP_LEVEL

# Copy the DNA plugin files
cp -R $TOP_LEVEL/cad/plugins/DNA $DIST_CONTENTS/plugins/
cp -R $TOP_LEVEL/cad/plugins/NanoDynamics-1 $DIST_CONTENTS/plugins/
mkdir $DIST_CONTENTS/plugins/GROMACS
cp -R $TOP_LEVEL/cad/plugins/GROMACS/Pam5Potential.xvg $DIST_CONTENTS/plugins/GROMACS/
cd $TOP_LEVEL

#
# End Plugins

# Remove cruft
rm -rf `find $DIST_ROOT -name CVS`
rm -rf $DIST_ROOT/partlib/*/CVS
rm -rf $DIST_ROOT/partlib/*/*/CVS
rm -rf $DIST_CONTENTS/Resources/lib/python2.3/bsddb3/tests || exit 1
rm -rf $DIST_CONTENTS/Resources/lib/python2.3/ctypes/test || exit 1
rm -rf $DIST_CONTENTS/Resources/lib/python2.3/numpy/doc || exit 1
#rm -rf $DIST_CONTENTS/Resources/lib/python2.3/numpy/testing || exit 1
rm -rf $DIST_CONTENTS/Resources/lib/python2.3/numpy/tests || exit 1
rm -rf $DIST_CONTENTS/Resources/lib/python2.3/OpenGL/tests || exit 1
for file in `find $DIST_ROOT -name *.py`; do
  if [ -e ${file}c ]; then
    rm $file
  fi
done

# Prepare package hierarchy
cd $TOP_LEVEL/packaging/MacOSX
tar xf NE1-folder.tar
cd $TOP_LEVEL
ditto --rsrc $TOP_LEVEL/packaging/MacOSX/NE1-folder $DIST_ROOT/$DIST_VERSION
mv $DIST_ROOT/Licenses $DIST_ROOT/$DIST_VERSION/
mv $DIST_ROOT/NanoEngineer-1.app $DIST_ROOT/$DIST_VERSION/
mv $DIST_ROOT/partlib $DIST_ROOT/$DIST_VERSION/
mv $DIST_ROOT/ReadMe.html $DIST_ROOT/$DIST_VERSION/
cp $TOP_LEVEL/cad/src/LICENSE $TOP_LEVEL/packaging/MacOSX/License.txt
cp $TOP_LEVEL/packaging/MacOSX/background.jpg $DIST_ROOT/$DIST_VERSION/NanoEngineer-1.app/Contents/Resources/
chmod -R 775 $DIST_ROOT/$DIST_VERSION
chmod ugo-x $DIST_ROOT/$DIST_VERSION/partlib/*/*.mmp
chmod ugo-x $DIST_ROOT/$DIST_VERSION/partlib/*/*/*.mmp
chmod ugo-x $DIST_ROOT/$DIST_VERSION/Licenses/*
chmod ugo-x $DIST_ROOT/$DIST_VERSION/ReadMe.html
sudo chown -R root:admin $DIST_ROOT/$DIST_VERSION

# Create package
sudo /Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker -build -p $TOP_LEVEL/cad/src/build/$DIST_VERSION.pkg -f $DIST_ROOT -s -ds -v -r $TOP_LEVEL/packaging/MacOSX -i $TOP_LEVEL/packaging/MacOSX/PackageMaker-Info.plist -d $TOP_LEVEL/packaging/MacOSX/Description.plist

# Create the disk image
mkdir $TOP_LEVEL/cad/src/build/$DIST_VERSION
mv $TOP_LEVEL/cad/src/build/$DIST_VERSION.pkg $TOP_LEVEL/cad/src/build/$DIST_VERSION/
sudo hdiutil create -srcfolder $TOP_LEVEL/cad/src/build/$DIST_VERSION -format UDZO $TOP_LEVEL/cad/src/build/${DIST_VERSION}.dmg

cd $TOP_LEVEL/packaging

# Prepare the disk image (for drag-n-drop install)
#mkdir -p $DIST_ROOT/$DIST_VERSION/$DIST_VERSION
#mv $DIST_ROOT/Licenses $DIST_ROOT/$DIST_VERSION/$DIST_VERSION/
#mv $DIST_ROOT/NanoEngineer-1.app $DIST_ROOT/$DIST_VERSION/$DIST_VERSION/
#mv $DIST_ROOT/partlib $DIST_ROOT/$DIST_VERSION/$DIST_VERSION/
#mv $DIST_ROOT/ReadMe.html $DIST_ROOT/$DIST_VERSION/$DIST_VERSION/
#ln -s /Applications $DIST_ROOT/$DIST_VERSION/Applications
#cp $TOP_LEVEL/packaging/MacOSX/install-background.png $DIST_ROOT/$DIST_VERSION/
#cp $TOP_LEVEL/cad/src/ReadMe.html $DIST_ROOT/$DIST_VERSION/
#cp $TOP_LEVEL/cad/src/LICENSE $DIST_ROOT/$DIST_VERSION/License.txt

# For the plain-Jane installer
#hdiutil create -srcfolder $DIST_ROOT/$DIST_VERSION -format UDZO $DIST_ROOT/${DIST_VERSION}.dmg

