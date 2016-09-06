from cement.core import handler, controller

from .dbr import ToolkitETLController, ToolkitFilterDBR

def load(app):
    handler.register(ToolkitETLController)

    handler.register(ToolkitFilterDBR)