from __future__ import with_statement

import os.path
import fnmatch
import datetime

import java.lang.Float as JFloat

from ij import IJ, ImagePlus
from ij.process import ImageProcessor, AutoThresholder
from ij.plugin.filter import ThresholdToSelection
from ij.plugin.filter import ParticleAnalyzer as PA
from ij.measure import ResultsTable, Calibration

# PA args and options
MINSIZE = 1000
MAXSIZE = JFloat.POSITIVE_INFINITY
options = PA.SHOW_NONE

DistPixel = IJ.getNumber("Distance in pixel", 600)
DistCm = IJ.getNumber("Distance in cm", 2.54)
cal = Calibration()
cal.setUnit("cm")
cal.pixelWidth = DistCm / DistPixel
cal.pixelHeight = DistCm / DistPixel
ImagePlus().setGlobalCalibration(cal)

dir = IJ.getDirectory("Path to directory")

filenames = [os.path.join(dir, file) for file in os.listdir(dir) if fnmatch.fnmatch(file, '*.jpg')]
filecounter = 0

maskdir = os.path.join(dir, "mask")
resdir = os.path.join(dir, "res")

for p in [maskdir, resdir]:
    if not os.path.exists(p):
        os.makedirs(p)

for filename in filenames:
    ip = IJ.openImage(filename).getProcessor().convertToByteProcessor()
    IJ.log("Input file: %s" % filename)

    ip.setAutoThreshold("Minimum")

    roi = ThresholdToSelection().convert(ip)
    ip.setRoi(roi)
    mask = ip.getMask()

    rt = ResultsTable()

    pa = PA(options, PA.AREA + PA.PERIMETER + PA.CIRCULARITY, rt, MINSIZE, MAXSIZE) 
    pa.analyze(ImagePlus(), mask)

    filebasename = os.path.basename(filename)

    nrow = rt.size()
    for i in range(nrow):
        rt.setValue("Filename", i, filebasename)

    outfilename = os.path.join(resdir, "res_%s.csv" % os.path.splitext(filebasename)[0])
    rt.save(outfilename)
    IJ.log("Result: %s" % outfilename)

    maskfilename = os.path.join(maskdir, "mask_%s" % filebasename)
    IJ.save(ImagePlus(filebasename, mask), maskfilename)
    IJ.log("Mask image: %s" % maskfilename)
    