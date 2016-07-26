from cement.core import handler, output

from cement.utils.misc import minimal_logger

LOG = minimal_logger(__name__)

class ZephyrOutputHandler(output.CementOutputHandler):
    class Meta:
        interface = output.IOutput
        label = 'zephyr'
        overridable = True

    def __init__(self, *args, **kw):
        super(ZephyrOutputHandler, self).__init__(*args, **kw)

    def _setup(self, app):
        super(ZephyrOutputHandler, self)._setup(app)

    def render(self, ddh, *args, **kwargs):
        LOG.debug("Rendering a DDH as a CSV")
        return ddh.to_csv()

def load(app):
    handler.register(ZephyrOutputHandler)
