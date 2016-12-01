from ..core.client import Client

class Report(Client):
    def __init__(
        self, config, account=None, date=None, expire_cache=None, log=None
    ):
        super().__init__(config)
        client = self.cls(config=config)
        response = client.cache_policy(
            account,
            date,
            None,
            expire_cache,
            log=log,
        )
        client.parse(response)
        self.client = client

    def to_xlsx(self, book, formatting):
        return self._xlsx(
            book,
            self.client.to_ddh(),
            self.title,
            name=self.name,
            formatting=formatting
        )

