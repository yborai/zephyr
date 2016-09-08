from cement.core import handler, output

from cement.utils.misc import minimal_logger

LOG = minimal_logger(__name__)

class CSVOutputHandler(output.CementOutputHandler):
    class Meta:
        interface = output.IOutput
        label = 'csv'
        overridable = True

    def __init__(self, *args, **kw):
        super(CSVOutputHandler, self).__init__(*args, **kw)

    def _setup(self, app):
        super(CSVOutputHandler, self)._setup(app)

    def render(self, ddh, *args, **kwargs):
        LOG.debug("Rendering a DDH as a CSV")
        return ddh.to_csv(*args, **kwargs)

class JSONOutputHandler(output.CementOutputHandler):
    class Meta:
        interface = output.IOutput
        label = 'json'
        overridable = True

    def __init__(self, *args, **kw):
        super(JSONOutputHandler, self).__init__(*args, **kw)

    def _setup(self, app):
        super(JSONOutputHandler, self)._setup(app)

    def render(self, ddh, *args, **kwargs):
        LOG.debug("Rendering a DDH as JSON")
        return ddh.to_json(*args, **kwargs)

def load(app):
    handler.register(CSVOutputHandler)
    handler.register(JSONOutputHandler)
