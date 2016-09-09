import csv

from cement.core import controller

from ..cli.controllers import ZephyrETL

class ZephyrDBRRI(ZephyrETL):
    class Meta:
        label = "dbr-ri"
        stacked_on = "etl"
        stacked_type = "nested"
        description = "Filter the DBR for only reserved instances."

        arguments = ZephyrETL.Meta.arguments

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
