import csv

from cement.core import controller


class ToolkitETLController(controller.CementBaseController):
    class Meta:
        label = "etl"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Generate single table reports for an account."
        arguments = controller.CementBaseController.Meta.arguments + [(
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
                )
        )]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()


class ToolkitFilterDBR(ToolkitETLController):
    class Meta:
        label = "dbr-ri"
        stacked_on = "etl"
        stacked_type = "nested"
        description = "Filter the DBR for only reserved instances."

        arguments = ToolkitETLController.Meta.arguments

    @controller.expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        infile = self.app.pargs.infile
        outfile = self.app.pargs.outfile
        no_tags = self.app.pargs.no_tags
        self.app.log.info("Using input file: {infile}".format(infile=infile))
        self.app.log.info("Using output file: {outfile}".format(outfile=outfile))
        with open(infile, "r") as dbrin, open(outfile, "w") as dbrout:
            reader = csv.DictReader(dbrin)
            header = reader.fieldnames
            if no_tags:
                header = [col for col in header if ":" not in col]
            print(header)
            writer = csv.DictWriter(dbrout, fieldnames=header, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for row in reader:
                if row["ReservedInstance"] != "Y":
                    continue
                out = {col:row[col] for col in header}
                writer.writerow(out)
