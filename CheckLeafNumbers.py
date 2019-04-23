from __future__ import with_statement

import sys
import os.path
import codecs

from ij import IJ, ImagePlus

from fiji.util.gui import GenericDialogPlus

from LAMeasure import PAResult


class CheckLeafNumbers(object):
    def __init__(self):
        self.dir = IJ.getDirectory("Path to directory")
        self.run()

    def readPAResults(self, f):
        rows = f.readlines()
        header = rows[0]
        ret = []
        for row in rows[1:]:
            cols = row.rstrip("\n").split(",")
            filename = cols[0].decode("utf-8")
            paResult = map(float, cols[1:])
            ret.append(PAResult(filename, paResult))
        return (header, ret)

    def run(self):
        maskdir = os.path.join(self.dir, "mask")
        resdir = os.path.join(self.dir, "res")

        with open(os.path.join(self.dir, "leafnumbers.csv")) as f:
            leafnumbers = [tuple(s.rstrip("\n").split(",")) for s in f.readlines()]

        for filename, n in leafnumbers:
            n = int(n)
            ip = IJ.openImage(os.path.join(maskdir, "mask_%s" % filename.decode('utf-8')))
            ip.show()
            gd = GenericDialogPlus("Check number of leaves")
            gd.addNumericField("Number of Leaf", n, 0)
            gd.addCheckbox("Remeasure ?", False)
            gd.showDialog()
            if gd.wasCanceled():
                sys.exit(0)
            ans = int(gd.getNextNumber())
            remeasure = gd.getNextBoolean()
            if remeasure:
                IJ.log("Remeasure: %s" % filename)
            self.leafnumbers_.append([filename, str(n), str(ans), str(remeasure)])
            if ans < n:
                with open(os.path.join(resdir, "res_%s.csv" % os.path.splitext(filename)[0].decode("utf-8")), "r") as f:
                    header, paResults = self.readPAResults(f)
                paResults = sorted(paResults, key=lambda x: x.area, reverse=True)
                with codecs.open(os.path.join(resdir, "res_%s.csv" % os.path.splitext(filename)[0].decode("utf-8")), "w", "utf-8") as f:
                    table = [header]
                    table += [row.asRow() for row in paResults[:ans]]
                    f.writelines(table)
            ip.close()


if __name__ == '__main__':
    CheckLeafNumbers()
