from . import MPGrid
import sysconfig
import os

def get_include():
    vars = sysconfig.get_config_vars()
    if 'platbase' in vars:
        return os.path.join(vars['platbase'],
                            'Lib', 'site-packages', 'MPGrid', 'include')

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
