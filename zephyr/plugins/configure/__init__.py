import errno
import os

from cement.core import handler, controller

def load(app):
    handler.register(ToolkitConfigureController)

class ToolkitConfigureController(controller.CementBaseController):
    class Meta:
        label = 'configure'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Configure zephyr."
    
    @controller.expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        home = os.path.expanduser("~")
        path = os.path.join(home, ".zephyr")
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise
        os.environ["ZEPHYR_DEBUG_LEVEL"] = "INFO"
        os.environ["ZEPHYR_DIR"] = path
        envvs = ["ZEPHYR_DEBUG_LEVEL", "ZEPHYR_DIR"]
        env_file = os.path.join(path, ".env")
        self.app.log.info("Saving environment to {}".format(env_file))
        with open(env_file, "w") as f:
            f.write(
                "\n".join(["{envv}={val}".format(
                    envv=envv,
                    val=os.environ.get(envv),
                ) for envv in envvs])
            )
