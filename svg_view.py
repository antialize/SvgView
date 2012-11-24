#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtSvg,QtCore,QtGui,Qt
import sys, signal, os
from argparse import ArgumentParser

class JvgWidget(QtGui.QGraphicsView):
    def updateLocation(self, pos):
        pass

    def updateViewBox(self):
        #w = self.scale * size.width()
        #h = self.scale * size.height()
        #r = QtCore.QRectF(self.center_x - w/2, self.center_y - h/2,
        #                 w, h)
        #p=self.mapToScene(self.center_x, self.center_y)
        #self.centerOn(float(p.x()), float(p.y()))
       
        #t = QtGui.QTransform()
        #self.setTransform(t)
        #self.fitInView(r)
        #self.scale(1,-1)
        #self.setSceneRect(r)
        #self.updateSceneRect(r)
        pass

    def center(self):
        #self.scale=max(float(self.defViewBox.width())/self.width(),
        #float(self.defViewBox.height())/self.height())
        #self.center_x = self.defViewBox.center().x()
        #self.center_y = self.defViewBox.center().y()
        #self.updateViewBox(self.size())
        #self.repaint()
        pass
    
    def __init__(self, path):
        scene = QtGui.QGraphicsScene()

        self.ds = None
        self.scale = 1
        self.center_x = 0
        self.center_y = 0
        self.defViewBox = (0, 0, 1, 1)
        
        f = open(path, "r")
        l1 = f.readline()
        if l1 != "jvg 1 0\n": print "bad"
        pen = QtGui.QPen()
        for line in f:
            line=line.strip().split(" ")
            if line[0] == 'width':
                #pen.setWidth(float(line[1]))
                pass
            elif line[0] == 'color':
                pen.setColor(QtGui.QColor(int(line[1]), int(line[2]), int(line[3])))
            elif line[0] == 'line':
                n = int(line[1])
                if (len(line) != 2 + 2 * n):
                    print "Line error: ", line
                    continue
                for i in range(1, n):
                    scene.addLine(float(line[2*i]), float(line[2*i+1]), float(line[2*i+2]), float(line[2*i+3]), pen)
            elif line[0] == 'rect':
                scene.addRect(float(line[1]), float(line[2]), 
                              float(line[3]) - float(line[1]), float(line[4]) - float(line[2]), pen)
            elif line[0] == 'viewBox':
                self.defViewBox = QtCore.QRectF(
                    float(line[1]), float(line[2]), 
                    float(line[3]) - float(line[1]), float(line[4]) - float(line[2]))
            elif line[0] == 'point':
                scene.addEllipse(float(line[1])-1, float(line[2])-1, 2, 2, pen, pen.color())
            else:
                print line
        QtGui.QGraphicsView.__init__(self, scene)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform);

        #self.center()
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        


        
    def wheelEvent(self, evt):      
        #dx = evt.pos().x() - self.width()/2
        #dy = evt.pos().y() - self.height()/2
        #center_x = self.center_x + dx*self.scale
        #center_y = self.center_y + dy*self.scale
        s=1.0025**(evt.delta())
        QtGui.QGraphicsView.scale(self, s, s)
        #self.scale = self.scale * 1.0025**(-evt.delta());
        #self.center_x = center_x - dx*self.scale
        #self.center_y = center_y - dy*self.scale
        #self.updateViewBox()
        #self.updateLocation(evt.pos())
        #self.repaint()

    # def mousePressEvent(self, evt):
    #     self.ds = evt.posF()
    #     self.start_center_x = self.center_x
    #     self.start_center_y = self.center_y
        
    # def mouseMoveEvent(self, evt):
    #     self.updateLocation(evt.posF())
    #     if not self.ds: return
    #     dx = evt.posF().x() - self.ds.x()
    #     dy = evt.posF().y() - self.ds.y()
    #     self.center_x = self.start_center_x - dx*self.scale
    #     self.center_y = self.start_center_y - dy*self.scale
    #     self.updateViewBox(self.size())
    #     self.repaint()

    # def mouseReleaseEvent(self, evt):
    #     self.mouseMoveEvent(evt)
    #     self.ds = None


class SvgWidget(QtSvg.QSvgWidget):
    location_changed = QtCore.pyqtSignal(QtCore.QPointF)
    
    def updateViewBox(self, size):
        w = self.scale * size.width()
        h = self.scale * size.height()
        r = QtCore.QRectF(self.center_x - w/2, self.center_y - h/2,
                         w, h)
        self.renderer().setViewBox(r)
        
    def center(self):
        self.scale=max(float(self.defViewBox.width())/self.width(),
                       float(self.defViewBox.height())/self.height())
        self.center_x = self.defViewBox.center().x()
        self.center_y = self.defViewBox.center().y()
        self.updateViewBox(self.size())
        self.repaint()
        
    def reload(self, path=None):
        QtSvg.QSvgWidget.load(self, self.path)
        self.defViewBox = self.renderer().viewBoxF()
        self.updateViewBox(self.size())
        
    def resizeEvent(self, evt):
        self.updateViewBox( evt.size())
        QtSvg.QSvgWidget.resizeEvent(self, evt)
        
    def __init__(self, path):
        QtSvg.QSvgWidget.__init__(self)
        self.path = path
        self.watch = QtCore.QFileSystemWatcher(self)
        self.watch.addPath(self.path)
        self.watch.fileChanged.connect(self.reload)

        self.setMouseTracking(True)
        self.ds = None
        self.scale = 0
        self.center_x = 0
        self.center_y = 0
        self.setPalette( QtGui.QPalette( QtCore.Qt.white ) );
        self.setAutoFillBackground(True)
        QtSvg.QSvgWidget.load(self, path)
        self.defViewBox = self.renderer().viewBoxF()
        self.center()
        
    def updateLocation(self, pos):
        self.location_changed.emit(QtCore.QPointF(
                (pos.x() - self.width()/2)*self.scale + self.center_x, 
                (pos.y() - self.height()/2)*self.scale + self.center_y))

    def wheelEvent(self, evt):      
        dx = evt.pos().x() - self.width()/2
        dy = evt.pos().y() - self.height()/2
        center_x = self.center_x + dx*self.scale
        center_y = self.center_y + dy*self.scale
        self.scale = self.scale * 1.0025**(-evt.delta());
        self.center_x = center_x - dx*self.scale
        self.center_y = center_y - dy*self.scale
        
        
        self.updateViewBox(self.size())
        self.updateLocation(evt.pos())
        self.repaint()

    def mousePressEvent(self, evt):
        self.ds = evt.posF()
        self.start_center_x = self.center_x
        self.start_center_y = self.center_y
        
    def mouseMoveEvent(self, evt):
        self.updateLocation(evt.posF())
        if not self.ds: return
        dx = evt.posF().x() - self.ds.x()
        dy = evt.posF().y() - self.ds.y()
        self.center_x = self.start_center_x - dx*self.scale
        self.center_y = self.start_center_y - dy*self.scale
        self.updateViewBox(self.size())
        self.repaint()

    def mouseReleaseEvent(self, evt):
        self.mouseMoveEvent(evt)
        self.ds = None

def tr(s):
    return QtGui.QApplication.translate("SvgViewer", s, None, QtGui.QApplication.UnicodeUTF8)

class MainWindow(QtGui.QMainWindow):
    def showLocation(self, point):
        self.statusbar.showMessage("%f %f"%(point.x(), point.y()))

    def load(self, path):
        if os.path.splitext(str(path))[1] == '.jvg':
            view = JvgWidget(path)
        else:
            view = SvgWidget(path)
        #view.location_changed.connect(self.showLocation)
        self.tabs.setCurrentIndex( self.tabs.addTab(view, os.path.basename("%s"%path)))
        
    def closeTab(self):
        if not self.tabs.currentWidget(): return
        self.tabs.removeTab(self.tabs.currentIndex())

    def center(self):
        if not self.tabs.currentWidget(): return
        self.tabs.currentWidget().center()

    def reload(self):
        if not self.tabs.currentWidget(): return
        self.tabs.currentWidget().reload()

    def nextTab(self):
        if not self.tabs.currentWidget(): return
        self.tabs.setCurrentIndex( (self.tabs.currentIndex() + 1)%self.tabs.count());
 
    def prevTab(self):
        if not self.tabs.currentWidget(): return
        self.tabs.setCurrentIndex( (self.tabs.currentIndex() - 1)%self.tabs.count());

    def open(self):
        path = QtGui.QFileDialog.getOpenFileName(
            self, "Open File", filter=tr("Svg documents (*.svg);;Any files (*.*)"))
        if path: self.load(path)

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        self.setCentralWidget(self.tabs)
        self.resize(800, 600)
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        
        self.menubar = QtGui.QMenuBar(self)
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.setMenuBar(self.menubar)
        
        self.actionOpen = QtGui.QAction(self)
        self.actionOpen.setShortcuts(QtGui.QKeySequence.Open);
        self.actionQuit = QtGui.QAction(self)
        self.actionQuit.setShortcuts(QtGui.QKeySequence.Quit);
        self.actionClose = QtGui.QAction(self)
        self.actionClose.setShortcuts(QtGui.QKeySequence.Close)
        self.actionCenter = QtGui.QAction(self)
        self.actionCenter.setShortcuts(QtGui.QKeySequence(tr("Space")));
        self.actionReload = QtGui.QAction(self)
        self.actionReload.setShortcuts(QtGui.QKeySequence(tr("F5")));

        self.actionNext = QtGui.QAction(self)
        self.actionNext.setShortcuts(QtGui.QKeySequence(tr("Page Down")));
        self.actionPrev = QtGui.QAction(self)
        self.actionPrev.setShortcuts(QtGui.QKeySequence(tr("Page Up")));
 
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction(self.actionQuit)
        self.menuEdit.addAction(self.actionCenter)
        self.menuEdit.addAction(self.actionReload)
        self.menuEdit.addAction(self.actionNext)
        self.menuEdit.addAction(self.actionPrev)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.actionCenter.triggered.connect(self.center)
        self.actionReload.triggered.connect(self.reload)
        self.actionNext.triggered.connect(self.nextTab)
        self.actionPrev.triggered.connect(self.prevTab)
        self.actionQuit.triggered.connect(self.close)
        self.actionOpen.triggered.connect(self.open)
        self.actionClose.triggered.connect(self.closeTab)

        self.setWindowTitle(tr("Svg Viewer"))
        self.menuFile.setTitle(tr("&File"))
        self.menuEdit.setTitle(tr("&Edit"))
        self.actionOpen.setText(tr("&Open"))
        self.actionClose.setText(tr("&Close Tab"))
        self.actionQuit.setText(tr("&Quit"))
        self.actionCenter.setText(tr("&Center"))
        self.actionReload.setText(tr("&Reload"))
        self.actionNext.setText(tr("&Next Tab"))
        self.actionPrev.setText(tr("&Prev Tab"))
        
def handleIntSignal(signum, frame):
    QtGui.qApp.closeAllWindows()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    
    parser = ArgumentParser(description="Display SVG files.")
    parser.add_argument("-v", "--version", 
                        help="show version information", default=False, action='store_const', const=True);
    parser.add_argument("documents", nargs='*')
    
    
#opt_parser.add_option("-q", dest="quickly", action="store_true",
#    help="Do it quickly (default=False)")
#(options, args) = opt_

    parser.parse_args(map(str, app.arguments()))

    if  '-h' in app.arguments()[1:] or '--help' in app.arguments()[1:]:
        print "Usage: svg_view.py <path_to_svg_file>?"
        exit

    window = MainWindow()
    window.show()

    for path in app.arguments()[1:]:
        window.load(path);

    #This is a hack to let the interperter run once every 1/2 second to catch sigint
    timer = QtCore.QTimer()
    timer.start(500)  
    timer.timeout.connect(lambda: None)
    signal.signal(signal.SIGINT, handleIntSignal)
    
    sys.exit(app.exec_())



