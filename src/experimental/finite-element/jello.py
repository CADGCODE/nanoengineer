#!/usr/bin/python

from jelloGui import *
import sys
import random
import time
import types
from math import cos, sin

GOT_PYREX = True
try:
    import comp
except ImportError:
    GOT_PYREX = False
print "GOT_PYREX", GOT_PYREX

"""I think this is the correct way to
scale stiffness and viscosity.
"""
N = 3
MASS = 1.0e-5 / N**2
DT = 1.0e-4
STIFFNESS = 1.0e-6 * N
VISCOSITY = 1.0e-6 * N
DTM = (DT ** 2) / MASS

# At some point, DT becomes a tuple with a bad internal state.

A = 1.0e-6

def addvec(u, v):
    return (u[0] + v[0], u[1] + v[1])
def subvec(u, v):
    return (u[0] - v[0], u[1] - v[1])
def scalevec(u, k):
    return (u[0] * k, u[1] * k)

# Keep the old, current and new versions of u
# in here, along with x.
class Computronium:
    def __init__(self, owner):
        self.owner = owner
        # replace all these with Numeric arrays? Use Pyrex?
        self.u = u = N**2 * [ (0.0, 0.0) ]
        self.u_old = N**2 * [ (0.0, 0.0) ]
        self.u_new = N**2 * [ (0.0, 0.0) ]
        self.x = x = [ ]  # nominal positions
        for i in range(N):
            for j in range(N):
                x.append((1. * j / N,
                          1. * i / N))
        if GOT_PYREX:
            comp._setup(self, N)
        else:
            self.forceTerms = [ ]
            # set up the force terms
            for i in range(N):
                for j in range(N - 1):
                    self.forceTerms.append((i * N + j,
                                            i * N + j + 1))
            for i in range(N - 1):
                for j in range(N):
                    self.forceTerms.append((i * N + j,
                                            (i + 1) * N + j))
        self.simTime = 0.0

    def internalForces(self):
        if GOT_PYREX:
            comp._internalForces(STIFFNESS, VISCOSITY/DT, DTM)
            return
        forces = self.zeroForces()
        u, o = self.u, self.u_old
        for i1, i2 in self.forceTerms:
            D = subvec(u[i2], u[i1]) # relative displacement
            P = subvec(o[i2], o[i1]) # previous relative displacement
            f = addvec(scalevec(D, STIFFNESS),
                       scalevec(subvec(D, P), VISCOSITY / DT))
            forces[i1] = addvec(forces[i1], f)
            forces[i2] = subvec(forces[i2], f) 
        self.applyForces(forces)

    def verletMomentum(self):
        if GOT_PYREX:
            comp._verletMomentum()
            return
        self_u, self_uold, self_unew = self.u, self.u_old, self.u_new
        for i in range(N**2):
                self_unew[i] = subvec(scalevec(self_u[i], 2),
                                      self_uold[i])

    def applyForces(self, f):
        if GOT_PYREX:
            comp._applyForces(f, DTM)
            return
        self_unew = self.u_new
        index = 0
        for i in range(N**2):
            unew = self_unew[i]
            fi = f[i]
            self_unew[i] = (unew[0] + DTM * fi[0],
                            unew[1] + DTM * fi[1])

    def zeroForces(self):
        return N**2 * [ (0.0, 0.0) ]

    def positions(self):
        # x is nominal position
        # u is displacement
        p = [ ]
        for i in range(N**2):
            xvec = self.x[i]
            uvec = self.u[i]
            p.append((xvec[0] + uvec[0],
                      xvec[1] + uvec[1]))
        return p

    def rotate(self):
        tmp = self.u_old
        self.u_old = self.u
        self.u = self.u_new
        self.u_new = tmp


class Jello(JelloGui):

    ANIMATION_DELAY = 20   # milliseconds
    COLOR_CHOICES = (
        QColor(Qt.red), QColor(Qt.yellow),
        QColor(Qt.green), QColor(Qt.blue)
        )

    def __init__(self):
        JelloGui.__init__(self, parent=None, name=None, modal=0, fl=0)
        size = self.frame1.size()
        self.width, self.height = size.width(), size.height()
        self.comp = Computronium(self)

        self.simTime = 0.0

        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL('timeout()'), self.timeout)
        self.lastTime = time.time()
        self.timer.start(self.ANIMATION_DELAY)

        self.firstPush = self.comp.zeroForces()
        self.firstPush[0] = (A, -A)
        self.firstPush[N-1] = (A, A)
        self.secondPush = self.comp.zeroForces()
        self.secondPush[N*(N-1)] = (-A, -A)
        self.secondPush[N**2-1] = (-A, A)

    def pushButton1_clicked(self):
        self.quit()

    def quit(self):
        self.app.quit()

    def timeout(self):
        try:
            self.oneFrame()
        except AssertionError, e:
            import traceback
            traceback.print_exc()
            self.quit()
        self.timer.start(self.ANIMATION_DELAY)

    def oneFrame(self):
        # On each step we do verlet, using u_old and u to compute
        # u_new. Then we move each particle from u to u_new. Then
        # we move u to u_old, and u_new to u.
        for i in range(10):
            self.equationsOfMotion()
        self.paintEvent(None)

    def paintEvent(self, e):
        """Draw a colorful collection of lines and circles.
        """
        p = QPainter()
        w, h = self.width, self.height
        w3, h3 = w / 3, h / 3
        radius = 10
        p.begin(self.frame1)
        p.eraseRect(0, 0, w, h)
        p.setPen(QPen(Qt.black))
        p.setBrush(QBrush(Qt.blue))
        i = 0
        for x, y in self.comp.positions():
            if x**2 + y**2 > 5.0:
                self.app.quit()
                p.end()
                return
            x = h3 * (x + 1)
            y = h3 * (y + 1)
            i += 1
            p.drawEllipse(x, y, radius, radius)
        p.end()

    def equationsOfMotion(self):
        #print "move"
        t = self.simTime
        forceTime = 0.1
        comp = self.comp
        comp.verletMomentum()
        self.simTime += DT
        if t > 0 and t < forceTime:
            comp.applyForces(self.firstPush)
        elif t > 2.0 and t < 2.0 + forceTime:
            comp.applyForces(self.secondPush)
        comp.internalForces()
        comp.rotate()

def main():
    app = QApplication(sys.argv)
    cr = Jello()
    cr.app = app
    app.setMainWidget(cr)
    cr.show()
    cr.update()
    app.exec_loop()

if __name__ == "__main__":
    if "profile" in sys.argv[1:]:
        import profile
        profile.run('main()')
    else:
        main()
