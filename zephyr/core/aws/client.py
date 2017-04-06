from ..client import Client
from ..utils import get_config_values, ZephyrException

class AWSPricingAPI(Client):
    name = "AWS Pricing API"

    def __init__(self, config, log=None):
        super().__init__(config, log=log)
        self._AWS_PRICING_API_BASE = None

    @property
    def AWS_PRICING_API_BASE(self):
        if self._AWS_PRICING_API_BASE:
            return self._AWS_PRICING_API_BASE
        self._AWS_PRICING_API_BASE = (
            "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/"
        )
        return self._AWS_PRICING_API_BASE

    def get_account_by_slug(self, slug):
        return True

    def request(self, account):
        raise NotImplementedError
