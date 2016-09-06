from cement.core import handler, controller

from .dbr_ri import ToolkitETLController, ToolkitFilterDBR

def load(app):
    handler.register(ToolkitETLController)

    handler.register(ToolkitFilterDBR)