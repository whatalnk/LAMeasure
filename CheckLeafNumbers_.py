from __future__ import with_statement

import sys
import os.path
import fnmatch
import datetime
import codecs

import java.lang.Float as JFloat

from ij import IJ, ImagePlus
from ij.process import ImageProcessor, AutoThresholder
from ij.plugin.filter import ThresholdToSelection
from ij.plugin.filter import ParticleAnalyzer as PA
from ij.measure import ResultsTable, Calibration

sys.path.append(IJ.getDirectory("plugins") + "/LAMeasure")

from LAMeasure_ import PAResult

def readPAResults(f):
    rows = f.readlines()
    header = rows[0]
    ret = []
    for row in rows[1:]:
        cols = row.rstrip("\n").split(",")
        filename = cols[0].decode("utf-8")
        paResult = map(float, cols[1:])
        ret.append(PAResult(filename, paResult))
    return (header, ret)

def checkLeafNumbers(dir):
    maskdir = os.path.join(dir, "mask")
    resdir = os.path.join(dir, "res")

    with open(os.path.join(dir, "leafnumbers.csv")) as f:
        leafnumbers = [tuple(s.rstrip("\n").split(",")) for s in f.readlines()]

    for filename, n in leafnumbers:
        n = int(n)
        ip = IJ.openImage(os.path.join(maskdir, "mask_%s" % filename.decode('utf-8')))
        ip.show()
        ans = int(IJ.getNumber("Number of Leaf", n))
        if ans < n:
            with open(os.path.join(resdir, "res_%s.csv" % os.path.splitext(filename)[0].decode("utf-8")), "r") as f:
                header, paResults = readPAResults(f)
            paResults = sorted(paResults, key=lambda x: x.area, reverse=True)
            with codecs.open(os.path.join(resdir, "res_%s.csv" % os.path.splitext(filename)[0].decode("utf-8")), "w", "utf-8") as f:
                table = [header]
                table += [row.asRow() for row in paResults[:ans]]
                f.writelines(table)
        ip.close()

if __name__ == '__main__':
    dir = IJ.getDirectory("Path to directory")
    checkLeafNumbers(dir)