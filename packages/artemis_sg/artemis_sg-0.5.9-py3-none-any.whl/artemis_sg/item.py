import logging
import re

import isbnlib


class Item:
    def __init__(self, keys, values, row_num, isbn_key):
        clean_keys = []
        for x in keys:
            if x:
                clean_keys.append(str(x).strip().upper())
        self.data = dict(zip(clean_keys, values))
        self.data_row_num = row_num
        self.isbn_key = isbn_key
        self.isbn = self.validate_isbn(self.data[isbn_key])
        self.isbn10 = isbnlib.to_isbn10(self.isbn)
        self.image_urls = []
        if "DESCRIPTION" not in self.data:
            self.data["DESCRIPTION"] = ""
        self._sort_data()

    def _sort_data(self):
        namespace = f"{type(self).__name__}.{self._sort_data.__name__}"

        def sort_order(e):
            # TODO: (#163) move to CFG
            defined_order = [
                "TITLE",
                "SUBTITLE",
                "AUTHOR",
                "PUBLISHER",
                "PUB DATE",
                "PUBLISHERDATE",
                "FORMAT",
            ]
            if e in defined_order:
                return defined_order.index(e)
            return 99

        sorted_keys = list(self.data.keys())
        # sort by defined order
        sorted_keys.sort(key=sort_order)
        # move ISBN and DESCRIPTION to end of list
        sorted_keys.sort(key=self.isbn_key.__eq__)
        sorted_keys.sort(key="DESCRIPTION".__eq__)
        logging.debug(f"{namespace}: Sorted keys: {sorted_keys}")

        sorted_data = {key: self.data[key] for key in sorted_keys}
        self.data = sorted_data

    def validate_isbn(self, isbn):
        namespace = f"{type(self).__name__}.{self.validate_isbn.__name__}"
        valid_isbn = ""
        if isinstance(isbn, str):
            m = re.search('="(.*)"', isbn)
            if m:
                isbn = m.group(1)
        try:
            valid_isbn = str(int(isbn)).strip()
        except Exception as e:
            logging.error(f"{namespace}: Err reading isbn '{isbn}', err: '{e}'")
            valid_isbn = ""
        return valid_isbn
