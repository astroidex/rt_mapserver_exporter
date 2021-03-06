from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *
from qgis.core import *
from qgis.gui import *

import sys
import locale
from datetime import datetime
from os import path

import rt_mapserver_exporter
import mapscript

QGIS_PREFIX  = '/usr'
TEST_WD      = path.dirname(path.abspath(__file__))

TEST_PROJECT = path.join(TEST_WD, 'data', 'test.qgs')
SHAPE_PATH   = path.join(TEST_WD, 'data')
TEMP_PATH    = path.join(TEST_WD, '')
MAPFILE_PATH = path.join(TEST_WD, 'test.map')

IMAGE_PATH   = path.join(TEST_WD, 'data')
IMAGE_URL    = ''
IMAGE_SIZE   = (600, 600)
IMAGE_TYPE   = 'PNG'

EXTENT_BUFFER_SIZE = 10

def computeExtent(extents):
    r = extents[0]
    for e in extents:
        r.combineExtentWith(e)

    return r.buffer(EXTENT_BUFFER_SIZE)

QgsApplication.setPrefixPath('/usr', True)  #<-- optional, if you have set QGIS_PREFIX_PATH
QgsApplication.setAuthDbDirPath('/home/me/test')  #<-- need to define where the auth database is created (or exists)
qgs = QgsApplication(sys.argv, False)
qgs.initQgis()

if len(QgsProviderRegistry.instance().providerList()) == 0:
    raise RuntimeError('No data providers available.')

class DummyInterface(object):
    """A mock `QgsLegendInterface` for testing purposes"""

    def __getattr__(self, *args, **kwargs):
        def dummy(*args, **kwargs):
            return self
        return dummy

    def __iter__(self):
        return self

    def next(self):
        raise StopIteration

    def layers(self):
        """Simulate iface.legendInterface().layers()"""
        return QgsMapLayerRegistry.instance().mapLayers().values()

    def symbolLayer(self, layer, symbolLayer):
        """Shortcut to fetch a symbol layer inside a layer's renderer"""
        return self.layers()[layer].rendererV2().symbols()[0].symbolLayer(symbolLayer)


class DummyLegendInterface(object):
    def isLayerVisible(self, layer):
        return True

iface = DummyInterface()

if path.isfile(TEST_PROJECT):
    try:
        open(TEST_PROJECT)
        pass
    except IOError as e:
        print "Unable to open project file."
        exit()

QgsProject.instance().setFileName(TEST_PROJECT)
QgsProject.instance().read(QFileInfo(TEST_PROJECT))

from rt_mapserver_exporter import MapfileExporter

MapfileExporter.export(
    name = str(QgsProject.instance().title()),
    width = IMAGE_SIZE[0],
    height = IMAGE_SIZE[1],
    extent = computeExtent([l.extent() for l in iface.layers()]),
    projection = str(iface.layers()[0].crs().toProj4()),
    shapePath = SHAPE_PATH,
    backgroundColor = QColor(255, 255, 255),
    imageType = IMAGE_TYPE,
    imagePath = IMAGE_PATH,
    imageURL = IMAGE_URL,
    tempPath = TEMP_PATH,
    mapfilePath = MAPFILE_PATH,
    fontsetPath = 'fontset',
    useSLD = False,

    legend = DummyLegendInterface(),
    layers = iface.layers()
)

# This is commented out such that we can manipulate stuff when dropped into the REPL
# QgsApplication.exitQgis()
