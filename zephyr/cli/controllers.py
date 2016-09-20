import os

from cement.core.controller import CementBaseController, expose

from ..core.aws import get_accounts

class ZephyrCLI(CementBaseController):
    class Meta:
        label = "base"
        description = "The zephyr reporting toolkit"

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

class ZephyrMeta(ZephyrCLI):
    class Meta:
        label = "meta"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Gather client meta information."

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        self.app.log.info("Collecting client meta data.")
        key_id = self.app.config.get("lw-aws", "AWS_ACCESS_KEY_ID")
        secret = self.app.config.get("lw-aws", "AWS_SECRET_ACCESS_KEY")
        cache = os.path.expanduser(self.app.config.get("zephyr", "cache"))
        self.app.render(get_accounts(key_id, secret, cache, self.app.log))

__ALL__ = [
    ZephyrCLI,
    ZephyrMeta,
]
