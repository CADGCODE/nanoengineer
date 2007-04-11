# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
DnaGenerator.py

$Id$

http://en.wikipedia.org/wiki/DNA
http://en.wikipedia.org/wiki/Image:Dna_pairing_aa.gif
"""

__author__ = "Will"

import sys
import os
import env
import re
from math import atan2, sin, cos, pi
from qt import QWhatsThis
from DnaGeneratorDialog import dna_dialog
from chem import Atom
from Utility import Group
from HistoryWidget import redmsg, orangemsg, greenmsg
from VQT import A, V, dot, vlen
from bonds import inferBonds, bond_atoms
from files_mmp import _readmmp
from GeneratorBaseClass import GeneratorBaseClass, PluginBug, UserError
from fusechunksMode import fusechunksBase
from platform import find_plugin_dir

atompat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
numberPattern = re.compile(r"^\s*(\d+)\s*$")

basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    # env.history.message(orangemsg("The DNA generator is not available."))
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

DEBUG = False

class Dna:

    fuseChunksTolerance = 1.5
    
    def make(self, assy, grp, sequence, doubleStrand, position,
             basenameA={'C': 'cytosine',
                        'G': 'guanine',
                        'A': 'adenine',
                        'T': 'thymine',
                        'N': 'unknown',
                        'Y': 'end1',
                        'Z': 'end2'},
             basenameB={'G': 'cytosine',
                        'C': 'guanine',
                        'T': 'adenine',
                        'A': 'thymine',
                        'N': 'unknown',
                        'Y': 'end1',
                        'Z': 'end2'}):
        baseList = [ ]
        def insertmmp(filename, subgroup, tfm, position=position):
            try:
                grouplist  = _readmmp(assy, filename, isInsert=True)
            except IOError:
                raise PluginBug("Cannot read file: " + filename)
            if not grouplist:
                raise PluginBug("No atoms in DNA base? " + filename)
            viewdata, mainpart, shelf = grouplist
            for member in mainpart.members:
                for atm in member.atoms.values():
                    atm._posn = tfm(atm._posn) + position
            del viewdata
            for member in mainpart.members:
                subgroup.addchild(member)
                baseList.append(member)
            shelf.kill()

        def rotateTranslate(v, theta, z):
            c, s = cos(theta), sin(theta)
            x = c * v[0] + s * v[1]
            y = -s * v[0] + c * v[1]
            return V(x, y, v[2] + z)

        if doubleStrand:
            subgroup = Group("strand 1", grp.assy, None)
                #bruce 060714 don't call this the "3' strand" -- there is no such thing.
                # When we look up whether its bases are oriented in 3' to 5' or 5' to 3' direction,
                # maybe we can call it something like "3' to 5'" or "5' to 3'",
                # in order to indicate its direction.
            grp.addchild(subgroup)
        else:
            subgroup = grp
        subgroup.open = False

        if (sequence.isdigit()):
            baseCount = int(sequence)
            sequence = baseCount * "N"
        sequence = self.addEndCaps(sequence)
        theta = 0.0
        z = 0.5 * self.BASE_SPACING * (len(sequence) - 1)
        for i in range(len(sequence)):
            basefile, zoffset, thetaOffset = \
                      self.strandAinfo(basenameA[sequence[i]], i)
            def tfm(v, theta=theta+thetaOffset, z1=z+zoffset):
                return rotateTranslate(v, theta, z1)
            if DEBUG: print basefile
            insertmmp(basefile, subgroup, tfm)
            theta -= self.TWIST_PER_BASE
            z -= self.BASE_SPACING

        if doubleStrand:
            subgroup = Group("strand 2", grp.assy, None) #bruce 060714 don't call this the "5' strand" (more info above)
            subgroup.open = False
            grp.addchild(subgroup)
            theta = 0.0
            z = 0.5 * self.BASE_SPACING * (len(sequence) - 1)
            for i in range(len(sequence)):
                # The 3'-to-5' direction is reversed for strand B.
                basefile, zoffset, thetaOffset = \
                          self.strandBinfo(basenameB[sequence[i]], i)
                def tfm(v, theta=theta+thetaOffset, z1=z+zoffset):
                    # Flip theta, flip z
                    # Cheesy hack: flip theta by reversing the sign of y,
                    # since theta = atan2(y,x)
                    return rotateTranslate(V(v[0], -v[1], -v[2]), theta, z1)
                if DEBUG: print basefile
                insertmmp(basefile, subgroup, tfm)
                theta -= self.TWIST_PER_BASE
                z -= self.BASE_SPACING

        # fuse the bases together into continuous strands
        fcb = fusechunksBase()
        fcb.tol = self.fuseChunksTolerance
        for i in range(len(baseList) - 1):
            fcb.find_bondable_pairs([baseList[i]], [baseList[i+1]])
            fcb.make_bonds(assy)

    def addEndCaps(self, sequence):
        return sequence

class A_Dna(Dna):
    """The geometry for A-DNA is very twisty and funky. I'd probably need to
    take a few days to research it. It's not a simple helix (like B) or an
    alternating helix (like Z).
    """
    geometry = "A-DNA"
    TWIST_PER_BASE = 0  # WRONG
    BASE_SPACING = 0    # WRONG
    def strandAinfo(self, sequence, i):
        raise PluginBug("A-DNA is not yet implemented -- please try B- or Z-DNA");
    def strandBinfo(self, sequence, i):
        raise PluginBug("A-DNA is not yet implemented -- please try B- or Z-DNA");

class A_Dna_BasePseudoAtoms(A_Dna):
    pass

class B_Dna(Dna):
    geometry = "B-DNA"
    TWIST_PER_BASE = -36 * pi / 180   # radians
    BASE_SPACING = 3.391              # angstroms

    def baseFileName(self, basename):
        return os.path.join(basepath, 'bdna-bases', '%s.mmp' % basename)

    def strandAinfo(self, basename, i):
        zoffset = 0.0
        thetaOffset = 0.0
        basefile = self.baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

    def strandBinfo(self, basename, i):
        zoffset = 0.0
        thetaOffset = 210 * (pi / 180)
        basefile = self.baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

class B_Dna_BasePseudoAtoms(B_Dna):
    TWIST_PER_BASE = -33.75 * pi / 180   # radians
    BASE_SPACING = 3.18              # angstroms
    fuseChunksTolerance = 1.0
    def baseFileName(self, basename):
        return os.path.join(basepath, 'bdna-pseudo-bases', '%s.mmp' % basename)
    def addEndCaps(self, sequence):
        if (len(sequence) > 1):
            return 'Y' + sequence[1:-1] + 'Z'
        return sequence

class Z_Dna(Dna):
    geometry = "Z-DNA"
    TWIST_PER_BASE = pi / 6     # in radians
    BASE_SPACING = 3.715        # in angstroms

    def baseFileName(self, basename, suffix):
        return os.path.join(basepath, 'zdna-pseudo-bases', '%s-%s.mmp' % (basename, suffix))

    def strandAinfo(self, basename, i):
        if (i & 1) != 0:
            suffix = 'outer'
            zoffset = 2.045
        else:
            suffix = 'inner'
            zoffset = 0.0
        thetaOffset = 0.0
        basefile = self.baseFileName(basename, suffix)
        return (basefile, zoffset, thetaOffset)

    def strandBinfo(self, basename, i):
        if (i & 1) != 0:
            suffix = 'inner'
            zoffset = -0.055
        else:
            suffix = 'outer'
            zoffset = -2.1
        thetaOffset = 0.5 * pi
        basefile = self.baseFileName(basename, suffix)
        return (basefile, zoffset, thetaOffset)

class Z_Dna_BasePseudoAtoms(Z_Dna):
    def baseFileName(self, basename, suffix):
        return os.path.join(basepath, 'zdna-bases', '%s-%s.mmp' % (basename, suffix))

###############################################################################

# GeneratorBaseClass must come BEFORE the dialog in the list of parents
class DnaGenerator(GeneratorBaseClass, dna_dialog):

    cmd = greenmsg("Insert Dna: ")
    sponsor_keyword = 'DNA'
    prefix = 'DNA-'   # used for gensym

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        dna_dialog.__init__(self, win) # win is parent.  Fixes bug 1089.  Mark 051119.
        GeneratorBaseClass.__init__(self, win)
        QWhatsThis.add(self.dna_type_combox, """<b>DNA Type</b>
        <p>There are three DNA geometries, A-DNA, B-DNA,
        and Z-DNA. Currently we have not yet implemented A-DNA.</p>""")
        QWhatsThis.add(self.endings_combox, """<b>Strand Type</b>
        <p>DNA strands can be single or double.</p>""")
        QWhatsThis.add(self.base_textedit, """<b>Base sequence</b>
        <p>The sequence of DNA bases in the strand.
        The bases are adenine, cytosine, guanine, and thymine.</p>""")
        QWhatsThis.add(self.complement_btn, """<b>Complement</b>
        <p>Swap all the bases with their matching bases.
        Adenine becomes thymine, thymine becomes adenine, cytosine becomes guanine, guanine becomes cytosine.</p>""")
        QWhatsThis.add(self.reverse_btn, """<b>Reverse</b>
        <p>Reverse the order of bases on the DNA strand,
        so GATTACA becomes ACATTAG. If it's a double strand, both are reversed.</p>""")

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters(self):
        if not basepath_ok:
            raise PluginBug("The cad/plugins/DNA directory is missing.")
        (seq, allKnown) = self._get_sequence()
        dnatype = str(self.dna_type_combox.currentText())
        if dnatype == 'A-DNA':
            raise PluginBug("A-DNA is not yet implemented -- please try B- or Z-DNA");
        assert dnatype in ('B-DNA', 'Z-DNA')
        double = str(self.endings_combox.currentText())

        representation = str(self.representation_combox.currentText())
        if (representation == 'Base(experimental)'):
            representation = 'BasePseudoAtom'
        assert representation in ('Atom', 'BasePseudoAtom')
        if (representation == 'Atom' and not allKnown):
            raise UserError("Cannot use unknown bases (N) in Atom representation")

        if (representation == 'BasePseudoAtom' and dnatype == 'Z-DNA'):
            raise PluginBug("Z-DNA not implemented for Base Pseudo Atoms representation.  Use B-DNA.")
        return (seq, dnatype, double, representation)

    def build_struct(self, name, params, position):
        # No error checking in build_struct, do all your error
        # checking in gather_parameters
        seq, dnatype, double, representation = params

        if (representation == 'Atom'):
            doubleStrand = (double == 'Double')
            if dnatype == 'A-DNA':
                dna = A_Dna()
            elif dnatype == 'B-DNA':
                dna = B_Dna()
            elif dnatype == 'Z-DNA':
                dna = Z_Dna()

        elif (representation == 'BasePseudoAtom'):
            doubleStrand = False # a single pseudo strand creates two strands
            if dnatype == 'A-DNA':
                dna = A_Dna_BasePseudoAtoms()
            elif dnatype == 'B-DNA':
                dna = B_Dna_BasePseudoAtoms()
            elif dnatype == 'Z-DNA':
                dna = Z_Dna_BasePseudoAtoms()

        dna.double = doubleStrand
        self.dna = dna  # needed for done msg
        if len(seq) > 30:
            env.history.message(self.cmd + "This may take a moment...")
        grp = Group(self.name, self.win.assy,
                    self.win.assy.part.topnode)
        try:
            dna.make(self.win.assy, grp, seq, doubleStrand, position)
            return grp
        except (PluginBug, UserError):
            grp.kill()
            raise

    def _get_sequence(self, reverse=False, complement=False,
                     cdict={'C':'G', 'G':'C', 'A':'T', 'T':'A', 'N':'N'}):
        seq = ''
        allKnown = True
        match = numberPattern.match(str(self.base_textedit.text()))
        if (match):
            return(match.group(1), False)
        for ch in str(self.base_textedit.text()).upper():
            if ch in 'CGATN':
                if ch == 'N':
                    allKnown = False
                if complement:
                    ch = cdict[ch]
                seq += ch
            elif ch in '\ \t\r\n':
                pass
            else:
                raise UserError('Bogus DNA base: ' + ch + ' (should be C, G, A, or T)')
        assert len(seq) > 0, 'Please enter a valid sequence'
        if reverse:
            seq = list(seq)
            seq.reverse()
            seq = ''.join(seq)
        return (seq, allKnown)

    def show(self):
        self.setSponsor()
        dna_dialog.show(self)

    ###################################################
    # The done message

    def done_msg(self):
        dna = self.dna
        if dna.double:
            dbl = "double "
        else:
            dbl = ""
        return "Done creating a %sstrand of %s." % (dbl, dna.geometry)

    ###################################################
    # Any special controls for this kind of structure

    def complement_btn_clicked(self):
        def thunk():
            (seq, allKnown) = self._get_sequence(complement=True)
            self.base_textedit.setText(seq)
        self.handlePluginExceptions(thunk)

    def reverse_btn_clicked(self):
        def thunk():
            (seq, allKnown) = self._get_sequence(reverse=True)
            self.base_textedit.setText(seq)
        self.handlePluginExceptions(thunk)

    def toggle_nt_parameters_grpbox(self):
        self.toggle_groupbox(self.grpbtn1, self.line2,
                             self.dna_type_label, self.dna_type_combox,
                             self.endings_label, self.endings_combox,
                             self.representation_combox_lbl,
                             self.representation_combox)

    def toggle_mwcnt_grpbox(self):
        self.toggle_groupbox(self.grpbtn2, self.line2_3,
                             self.base_textedit,
                             self.complement_btn,
                             self.reverse_btn)
