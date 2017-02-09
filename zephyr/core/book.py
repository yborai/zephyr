import datetime
import os
import xlsxwriter

from shutil import copyfile

from .client import Client
from .utils import ZephyrException

FORMATTING = {
    "book_options" : {
        "strings_to_numbers": True,
    },
}

class Book(Client):
    def __init__(
        self, config, label, sheets, account, date, expire_cache, log=None
    ):
        super().__init__(config)
        self.account = account
        self.config = config
        self.date = date
        self.expire_cache = expire_cache
        self.has_data = False
        self.label = label
        self.log = log
        self.sheets = tuple([Sheet(
            config,
            account=account,
            date=date,
            expire_cache=expire_cache,
            log=log
        ) for Sheet in sheets])
        self.filename = "{slug}.{label}.xlsx".format(
            label=self.label, slug=self.account
        )

    def cache(self):
        cache_key = self.cache_key(self.label, self.account, self.date)
        cache_local = os.path.join(self.ZEPHYR_CACHE_ROOT, cache_key)
        copyfile(self.filename, cache_local)
        # Cache result to local cache and S3
        self.log.info(cache_local, cache_key)
        self.s3.meta.client.upload_file(
            cache_local, self.ZEPHYR_S3_BUCKET, cache_key
        )

    def cache_key(self, slug, account, date):
        month = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
        filename = "{slug}.xlsx".format(slug=slug)
        return os.path.join(account, month, filename)

    def collate(self):
        account = self.account
        config = self.config
        date = self.date
        expire_cache = self.expire_cache
        log = self.log
        out = dict()
        for sheet in self.sheets:
            try:
                out[sheet.name] = sheet.to_xlsx(self.book)
                if not out[sheet.name]:
                    log.info(
                        "{} is empty and will be skipped."
                        .format(sheet.title)
                    )
            except ZephyrException as e:
                message = e.args[0]
                log.error("Error in {sheet}: {message}".format(
                    sheet=sheet.title, message=message
                ))
        return out

    def slug_valid(self, slug):
        return all([
            api.slug_valid(slug)
            for api in self.slug_validators()
        ])

    def slug_validators(self):
        """
        For each client in each sheet in a book,
        collect the unique slug validation methods.
        """
        return {
            call.slug_valid.__func__: call
            for sheet in self.sheets
            for call in getattr(sheet, "clients", [])
        }.values()


    def to_xlsx(self):
        options = FORMATTING["book_options"]
        with xlsxwriter.Workbook(self.filename, options) as self.book:
            report = self.collate()
        if(report):
            self.cache()
        return report
