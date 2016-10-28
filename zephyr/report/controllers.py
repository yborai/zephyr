from cement.core.controller import CementBaseController, expose

from . import account_review
from .sr import service_request_xlsx

class ZephyrReport(CementBaseController):
    class Meta:
        label = "report"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Generate advanced reports."
        parser_options = {}

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

class ZephyrAccountReview(ZephyrReport):
    class Meta:
        label = "account-review"
        stacked_on = "report"
        stacked_type = "nested"
        description = "Generate an account review for a given account."

        arguments = CementBaseController.Meta.arguments + [(
            ["--cache-folder"], dict(
                 type=str,
                 help="The path to the folder containing the  cached responses."
            )
        )]

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        cache_folder = self.app.pargs.cache_folder
        if(not cache_folder):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache_folder))

class ServiceRequestReport(ZephyrReport):
    class Meta:
        label = "sr"
        stacked_on = "report"
        stacked_type = "nested"
        description = "Generate the service-requests worksheet for a given account."

        arguments = CementBaseController.Meta.arguments + [(
            ["--cache"], dict(
                type=str,
                help="The path to the json cached file."
            )
        )]

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if not cache:
            raise NotImplementedError
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            srs = f.read()
        # 480 x 288 is the default size of the xlsxwriter chart.
        # 64 x 20 is the default size of each cell.
        formatting = {
            "cell_options" : {
                "height" : 20,
                "width" : 64,
            },
            "chart_options" : {
                "height" : 288,
                "width" : 480,
            },
            "chart_type" : {
                "type" : "pie",
            },
            "data_labels": {
                "category": True,
                "percentage": True,
                "position": "outside_end",
            },
            "header_format" : {
                "font_color" : "#000000",
                "bg_color" : "#DCE6F1",
                "bottom" : 2,
                "total_row" : True,
            },
            "label_format" : {
                "bold": True,
                "font_size": 16,
                "font_color": "#000000",
            },
            "legend_options" : {
                "none" : True,
            },
            "table_style" : {
                "style" : "Table Style Light 1",
                "total_row_t" : True,
                "total_row_f" : False
            },
            "titles" : {
                "Service Requests" : "srs",
                "EC2 Details" : "ec2",
            },
            "titles" : {
                "Service Requests" : "srs",
                "EC2 Details" : "ec2",
            },
            "wkbk_options" : {
                "strings_to_numbers": True,
            },
        }
        service_request_xlsx(json_string=srs, formatting=formatting)



__ALL__ = [
    ZephyrReport,
    ZephyrAccountReview,
    ServiceRequestReport
]
