import datetime
import io
import os

import xlsxwriter

from shutil import copyfile

from . import aws
from .client import Client

FORMATTING = {
    "book_options" : {
        "strings_to_numbers": True,
    },
}

class Book(Client):
    def __init__(
        self,
        config,
        label,
        sheets,
        account,
        date,
        expire_cache,
        log=None,
        in_memory=None,
    ):
        super().__init__(config, log=log)
        self.account = account
        self.config = config
        self.date = date
        self.expire_cache = expire_cache
        self.has_data = False
        self.in_memory = in_memory
        self.label = label
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
        if self.in_memory:
            self.filename = io.BytesIO()

    def cache(self):
        cache_key = self.cache_key(self.label, self.account, self.date)
        cache_local = os.path.join(self.ZEPHYR_CACHE_ROOT, cache_key)
        copyfile(self.filename, cache_local)
        # Cache result to local cache and S3
        self.log.info(cache_local, cache_key)
        s3 = self.s3  # This is a bit kludgy. TODO: Fix this.
        if self.ZEPHYR_S3_BUCKET:
            aws.put_s3(self.s3, cache_local, self.ZEPHYR_S3_BUCKET, cache_key)

    def cache_key(self, slug, account, date):
        month = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
        filename = "{slug}.{account}.{date}.xlsx".format(
            account=account, date=date, slug=slug
        )
        return os.path.join(account, month, filename)

    def collate(self):
        account = self.account
        config = self.config
        date = self.date
        expire_cache = self.expire_cache
        out = dict()
        for sheet in self.sheets:
            out[sheet.name] = sheet.to_xlsx(self.book)
            if not out[sheet.name]:
                self.log.info(
                    "{} is empty and will be skipped."
                    .format(sheet.title)
                )
        return out

    def slug_valid(self, slug):
        return all([
            api.get_account_by_slug(slug)
            for api in self.slug_validators()
        ])

    def slug_validators(self):
        """
        For each client in each sheet in a book,
        collect the unique slug validation methods.
        """
        out = {
            client.get_account_by_slug.__func__: client
            for sheet in self.sheets
            for client in getattr(sheet, "clients", [])
        }
        return out.values()


    def to_xlsx(self):
        options = FORMATTING["book_options"]
        if self.in_memory:
            options.update(dict(in_memory=True))
        with xlsxwriter.Workbook(self.filename, options) as self.book:
            report = self.collate()
        if(report and not self.in_memory):
            self.cache()
        return report
