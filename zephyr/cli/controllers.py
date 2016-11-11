import os

from cement.core.controller import CementBaseController, expose

from ..core import meta

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
        arguments = CementBaseController.Meta.arguments + [(
            ["--expire-cache"], dict(
                action="store_true",
                help="Forces the cached data to be refreshed."
            )
        )]

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        config = self.app.config
        log = self.app.log
        self.line_width = int(self.app.config.get("zephyr", "line_width"))
        expire_cache = self.app.pargs.expire_cache
        self.app.log.info("Collecting client metadata.")
        projects = meta.LWProjects(config)
        projects.cache_policy(expire_cache, log=log)
        self.app.render(
            projects.get_all_projects(),
            line_width=self.line_width
        )

__ALL__ = [
    ZephyrCLI,
    ZephyrMeta,
]
