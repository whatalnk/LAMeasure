from __future__ import with_statement

import sys
import os.path
import fnmatch
import datetime
import codecs

import java.lang.Float as JFloat

from ij import IJ, ImagePlus, Prefs
from ij.process import ImageProcessor, AutoThresholder, ImageConverter
from ij.plugin.filter import ThresholdToSelection
from ij.plugin.filter import ParticleAnalyzer as PA
from ij.measure import ResultsTable, Calibration

from fiji.util.gui import GenericDialogPlus
from fiji.threshold import Auto_Threshold


class ScanedImage(object):
    def __init__(self, filename):
        self.filename = filename

    def measure(self):
        imp = IJ.openImage(self.filename)
        IJ.log("Input file: %s" % self.filename)

        ImageConverter(imp).convertToGray8()

        res = Auto_Threshold().exec(imp, myMethod, noWhite, noBlack, doIwhite, doIset, doIlog, doIstackHistogram)

        rt = ResultsTable()
        rt.showRowNumbers(False)
        pa = PA(options, PA.AREA + PA.PERIMETER + PA.CIRCULARITY, rt, MINSIZE, MAXSIZE)
        pa.analyze(imp)
        self.result = self.rtToResult(rt)
        self.mask = imp

    def rtToResult(self, rt):
        result = []
        nrow = rt.size()
        for i in range(nrow):
            area = rt.getValue("Area", i)
            perim = rt.getValue("Perim.", i)
            circ = rt.getValue("Circ.", i)
            ar = rt.getValue("AR", i)
            round = rt.getValue("Round", i)
            solidity = rt.getValue("Solidity", i)
            result.append(PAResult((area, perim, circ, ar, round, solidity)))
        return result

    def saveMask(self):
        imp = self.mask
        imp.getProcessor().invert()
        filebasename = os.path.basename(self.filename)
        maskfilename = os.path.join(maskdir, "mask_%s" % filebasename)
        IJ.save(imp, maskfilename)
        IJ.log("Mask image: %s\n" % maskfilename)

    def saveResult(self):
        filebasename = os.path.basename(self.filename)
        resfilename = os.path.join(resdir, "res_%s.csv" % os.path.splitext(filebasename)[0])
        with codecs.open(resfilename, "w", "utf-8") as f:
            table = [",".join(header) + "\n"]
            table += ["%s, %s\n" % (filebasename, row.asRow()) for row in self.result]
            f.writelines(table)
        IJ.log("Result: %s" % resfilename)


class PAResult(object):
    def __init__(self, paResult):
        self.area, self.perim, self.circ, self.ar, self.round, self.solidity = paResult

    def asRow(self):
        return "%f, %f, %f, %f, %f, %f" % (self.area, self.perim, self.circ, self.ar, self.round, self.solidity)


class LeafNumbers(object):
    def __init__(self):
        self.leafnumbers = []

    def add(self, filebasename, leafnumber):
        self.leafnumbers.append((filebasename, leafnumber))

    def save(self):
        with codecs.open(os.path.join(dir, "leafnumbers.csv"), "w", "utf-8") as f:
            f.writelines(["%s, %d\n" % fn for fn in self.leafnumbers])


class LAMeasure(object):
    def __init__(self):
        # Save current background value
        bb = Prefs.blackBackground
        Prefs.blackBackground = False

        # PA args and options
        distPixel, distCm, MINSIZE, dir = self.getSettings()
        MAXSIZE = JFloat.POSITIVE_INFINITY
        options = PA.SHOW_NONE

        # Auto_Threshold args
        myMethod = "Minimum"
        noWhite = False
        noBlack = False
        doIwhite = False
        doIset = False
        doIlog = True
        doIstackHistogram = False

        header = ["Filename", "Area", "Perim.", "Circ", "AR", "Round", "Solidity"]

        self.setScale(distCm, distPixel)

        maskdir = os.path.join(dir, "mask")
        resdir = os.path.join(dir, "res")

        for p in [maskdir, resdir]:
            if not os.path.exists(p):
                os.makedirs(p)

        filenames = [os.path.join(dir, file) for file in os.listdir(dir) if fnmatch.fnmatch(file, '*.jpg')]

        leafnumbers = LeafNumbers()

        for filename in filenames:
            filebasename = os.path.basename(filename)
            scanedImage = ScanedImage(filename)
            scanedImage.measure()
            leafnumbers.add(filebasename, len(scanedImage.result))
            scanedImage.saveMask()
            scanedImage.saveResult()

        leafnumbers.save()

        # Reset background value
        Prefs.blackBackground = bb

    def getSettings(self):
        gd = GenericDialogPlus("Settings")
        gd.addNumericField("Distance in pixel", 600, 0)
        gd.addNumericField("Distance in cm", 2.54, 2)
        gd.addNumericField("Min. size (cm^2)", 0.5, 2)
        gd.addDirectoryField("Directory", IJ.getDirectory("home"))
        gd.showDialog()

        if gd.wasCanceled():
            sys.exit()
        else:
            distPixel = gd.getNextNumber()
            distCm = gd.getNextNumber()
            minSize = gd.getNextNumber() * (distPixel / distCm) ** 2
            imageDir = gd.getNextString()

        return (distPixel, distCm, minSize, imageDir)

    def setScale(self, distCm, distPixel):
        cal = Calibration()
        cal.setUnit("cm")
        cal.pixelWidth = distCm / distPixel
        cal.pixelHeight = distCm / distPixel
        ImagePlus().setGlobalCalibration(cal)


if __name__ == '__main__':
    LAMeasure()
