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
        self.app.log.info("Collecting client metadata.")
        self.line_width = int(self.app.config.get("zephyr", "line_width"))
        aws_config_keys = (
            "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "s3_bucket",
        )
        sf_config_keys = ("SF_USERNAME", "SF_PASSWD", "SF_TOKEN")
        aws_config = [
            self.app.config.get("lw-aws", key)
            for key in aws_config_keys
        ]
        sf_config = [
            self.app.config.get("lw-sf", key)
            for key in sf_config_keys
        ]
        cache = os.path.expanduser(self.app.config.get("zephyr", "cache"))
        expire_cache = self.app.pargs.expire_cache
        database = meta.get_local_db_connection(
            cache,
            expire_cache,
            log=self.app.log,
            aws_config=aws_config,
            sf_config=sf_config,
        )
        self.app.render(meta.get_all_projects(database), line_width=self.line_width)

__ALL__ = [
    ZephyrCLI,
    ZephyrMeta,
]
