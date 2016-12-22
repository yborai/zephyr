import os

from cement.core.controller import CementBaseController, expose

from ..core import meta
from ..core.configure import create_config

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
        self.ZEPHYR_LINE_WIDTH = int(self.app.config.get("zephyr", "ZEPHYR_LINE_WIDTH"))
        expire_cache = self.app.pargs.expire_cache
        self.app.log.info("Collecting client metadata.")
        projects = meta.LWProjects(config)
        projects.cache_policy(expire_cache, log=log)
        self.app.render(
            projects.get_all_projects(),
            line_width=self.ZEPHYR_LINE_WIDTH
        )

class ZephyrConfigure(ZephyrCLI):
    class Meta:
        label = "configure"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Gather configuration values."
        arguments = CementBaseController.Meta.arguments + [(
            ["--first-run"], dict(
                action="store_true",
                help=(
                    "Alias for --write --no-prompt."
                    " Initializes a configuration file with empty values."
                ),
            )
        ),
        (
            ["--ini"], dict(
                action="store_true",
                help="Include sections, as in INI format.",
            )
        ),
        (
            ["--no-prompt"], dict(
                action="store_true",
                help="Do not ask for values, but print given values."
            )
        ),
        (
            ["--write"], dict(
                action="store_true",
                help="Write configuration file. This option implies --ini."
            )
        )]


    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        first_run = self.app.pargs.first_run
        write = self.app.pargs.write or first_run # first_run implies write
        # first_run implies no prompt
        no_prompt = self.app.pargs.no_prompt or first_run
        prompt = not no_prompt
        ini = self.app.pargs.ini or write # write implies ini
        create_config(self.app.config, prompt, write, ini)

__ALL__ = [
    ZephyrCLI,
    ZephyrConfigure,
    ZephyrMeta,
]
