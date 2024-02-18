from . import MPGrid
import os

def get_include():
    return os.path.join(os.path.dirname(__file__), 'include')

class new(MPGrid.new):
    pass

class read(MPGrid.read):
    pass

class copy(MPGrid.copy):
    pass

class clone(MPGrid.clone):
    pass

BoundInsulate = MPGrid.BoundInsulate
BoundPeriodic = MPGrid.BoundPeriodic
InterCond = MPGrid.InterCond
InterTrans = MPGrid.InterTrans
