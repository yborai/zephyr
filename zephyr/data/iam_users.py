import json

from cement.core import controller

from ..cli.controllers import ZephyrData
from .common import DDH

class ZephyrIAMUsers(ZephyrData):
    class Meta:
        label = "iam-users"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the IAM Users meta information"

        arguments = ZephyrData.Meta.arguments #+ [(
        #    ["--cc_api_key"], dict(
        #        type=str,
        #        help="The CloudCheckr API key to use."
        #    )
        #)]

    @controller.expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if (not cache):
            raise NotImplementedError # We will add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = json.load(f)
        user_details = response.get("IamUsersDetails")
        headers = ["Username", "Has MFA", "Console Last Used", 
                   "Access Key 1 Last Used", "Access Key 2 Last Used"]
        data = [[
            user["UserName"],
            user["HasMfa"],
            user["LastUsed"],
            user["UserCredential"]["AccessKey1LastUsedDate"],
            user["UserCredential"]["AccessKey2LastUsedDate"],
            ]
                for user in user_details]
        out = DDH(headers=headers, data=data)
        self.app.render(out)
        return out
