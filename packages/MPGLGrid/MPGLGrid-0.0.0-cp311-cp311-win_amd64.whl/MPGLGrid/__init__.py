from . import MPGLGrid
import sysconfig
import os

def get_include():
    vars = sysconfig.get_config_vars()
    if 'platbase' in vars:
        return os.path.join(vars['platbase'],
                            'Lib', 'site-packages', 'MPGLGrid', 'include')

class draw(MPGLGrid.draw):
    pass

class model(MPGLGrid.model):
    pass

class colormap(MPGLGrid.colormap):
    pass

class scene(MPGLGrid.scene):
    pass
