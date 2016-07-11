from __future__ import with_statement

import os.path
import fnmatch
import datetime
import codecs

import java.lang.Float as JFloat
from org.apache.commons.math3.ml.clustering import KMeansPlusPlusClusterer, Clusterable

from ij import IJ, ImagePlus
from ij.process import ImageProcessor, AutoThresholder
from ij.plugin.filter import ThresholdToSelection
from ij.plugin.filter import ParticleAnalyzer as PA
from ij.measure import ResultsTable, Calibration

class PAResult(Clusterable):
    def __init__(self, filename, paResult):
        self.filename = filename 
        self.area, self.perim, self.circ, self.ar, self.round, self.solidity = paResult

    def asRow(self):
        return "%s, %f, %f, %f, %f, %f, %f\n" % (self.filename, self.area, self.perim, self.circ, self.ar, self.round, self.solidity)

    def getPoint(self):
        return [self.area]

def analyze(filename):
    ip = IJ.openImage(filename).getProcessor().convertToByteProcessor()
    IJ.log("Input file: %s" % filename)

    ip.setAutoThreshold("Minimum")

    roi = ThresholdToSelection().convert(ip)
    ip.setRoi(roi)
    mask = ip.getMask()

    rt = ResultsTable()
    rt.showRowNumbers(False)
    pa = PA(options, PA.AREA + PA.PERIMETER + PA.CIRCULARITY, rt, MINSIZE, MAXSIZE) 
    pa.analyze(ImagePlus(), mask)

    filebasename = os.path.basename(filename)

    paResults = [] 
    nrow = rt.size()
    for i in range(nrow):
        area = rt.getValue("Area", i)
        perim = rt.getValue("Perim.", i)
        circ = rt.getValue("Circ.", i)
        ar = rt.getValue("AR", i)
        round = rt.getValue("Round", i)
        solidity = rt.getValue("Solidity", i)
        paResults.append(PAResult(filebasename, [area, perim, circ, ar, round, solidity]))
    return (filebasename, mask, paResults)


if __name__ == '__main__':
    # PA args and options
    MINSIZE = 0
    MAXSIZE = JFloat.POSITIVE_INFINITY
    options = PA.SHOW_NONE
    CLUSTERSIZE = 2

    header = ["Filename", "Area", "Perim.", "Circ", "AR", "Round", "Solidity"]

    DistPixel = IJ.getNumber("Distance in pixel", 600)
    DistCm = IJ.getNumber("Distance in cm", 2.54)
    cal = Calibration()
    cal.setUnit("cm")
    cal.pixelWidth = DistCm / DistPixel
    cal.pixelHeight = DistCm / DistPixel
    ImagePlus().setGlobalCalibration(cal)

    dir = IJ.getDirectory("Path to directory")

    filenames = [os.path.join(dir, file) for file in os.listdir(dir) if fnmatch.fnmatch(file, '*.jpg')]

    maskdir = os.path.join(dir, "mask")
    resdir = os.path.join(dir, "res")

    for p in [maskdir, resdir]:
        if not os.path.exists(p):
            os.makedirs(p)

    leafnumbers = []

    for filename in filenames:
        filebasename, mask, paResults = analyze(filename)
        clusterer = KMeansPlusPlusClusterer(CLUSTERSIZE)
        clusterResults = clusterer.cluster(paResults)
        cl1, cl2 = [clusterResults.get(i).getPoints() for i in range(CLUSTERSIZE)]
        sum1, sum2 = [sum([point.area for point in cl]) for cl in [cl1, cl2]]
 
        if sum1 > sum2:
            paResults = cl1
        else:
            paResults = cl2

        outfilename = os.path.join(resdir, "res_%s.csv" % os.path.splitext(filebasename)[0])
        with codecs.open(outfilename, "w", "utf-8") as f:
            table = [",".join(header) + "\n"]
            table += [row.asRow() for row in paResults]
            f.writelines(table)
        IJ.log("Result: %s" % outfilename)

        maskfilename = os.path.join(maskdir, "mask_%s" % filebasename)
        IJ.save(ImagePlus(filebasename, mask), maskfilename)
        IJ.log("Mask image: %s" % maskfilename)
        
        leafnumbers.append((filebasename, len(paResults)))

    with codecs.open(os.path.join(dir, "leafnumbers.csv"), "w", "utf-8") as f:
        f.writelines(["%s, %d\n" % fn for fn in leafnumbers])