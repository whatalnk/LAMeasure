from ij import IJ
from LAMeasure import LAMeasure


if __name__ in ['__main__', '__builtin__']:
    if __name__ is not '__main__':
        msg = "Warning: __name__ is  %s" % __name__
        IJ.log(msg)
    LAMeasure.LAMeasure()
