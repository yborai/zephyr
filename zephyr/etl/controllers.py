from cement.core.controller import CementBaseController, expose

from .dbr_ri import filter_ri_dbr

class ZephyrETL(CementBaseController):
    class Meta:
        label = "etl"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Perform Extract-Transform-Load operations on data."
        arguments = CementBaseController.Meta.arguments

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

class ZephyrDBRRI(ZephyrETL):
    class Meta:
        label = "dbr-ri"
        stacked_on = "etl"
        description = "Filter the DBR for only reserved instances."

        arguments = ZephyrETL.Meta.arguments + [
            (
                ["--infile"], dict(
                    type=str,
                    help="Path to input file.",
                    required=True,
                ),
            ),
            (
                ["--outfile"], dict(
                    type=str,
                    help="Path to output file.",
                    required=True,
                ),
            ),
            (
                ["--no-tags"], dict(
                     action="store_true",
                     help="Removes tags in output file."
                ),
            ),
        ]

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        infile = self.app.pargs.infile
        outfile = self.app.pargs.outfile
        no_tags = self.app.pargs.no_tags
        self.app.log.info("Using input file: {infile}".format(infile=infile))
        self.app.log.info("Using output file: {outfile}".format(outfile=outfile))
        filter_ri_dbr(infile, outfile, no_tags)

__ALL__ = [
    ZephyrETL,
    ZephyrDBRRI
]
