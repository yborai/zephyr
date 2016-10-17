from cement.core import handler, output

from cement.utils.misc import minimal_logger

LOG = minimal_logger(__name__)

class OutputHandler(output.CementOutputHandler):
    class Meta:
        interface = output.IOutput
        overridable = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _setup(self, app):
        super()._setup(app)

class CSVOutputHandler(OutputHandler):
    class Meta:
        label = 'csv'

    def render(self, ddh, *args, **kwargs):
        LOG.debug("Rendering a DDH as a CSV")
        return ddh.to_csv(*args, **kwargs)

class DefaultOutputHandler(OutputHandler):
    class Meta:
        label = 'default'

    def render(self, ddh, *args, **kwargs):
        return ddh.to_table(*args, **kwargs)

class JSONOutputHandler(OutputHandler):
    class Meta:
        label = 'json'

    def render(self, ddh, *args, **kwargs):
        LOG.debug("Rendering a DDH as JSON")
        return ddh.to_json(*args, **kwargs)

def load(app):
    handler.register(CSVOutputHandler)
    handler.register(DefaultOutputHandler)
    handler.register(JSONOutputHandler)
