# Parse the price tag
import utils

import logging
logger = logging.getLogger()

class Price:
    def __init__(self, lines=None):
        self.symbol = None
        self.price = None
        self.date = None
        if lines:
            self.parse_qif(lines)

    def parse_qif(self, lines):
        if len(lines) > 1:
            raise Exception("Price with more than one value found")

        chunks = lines[0].split(',')

        self.symbol = chunks[0].strip('"')
        self.price = utils.read_price(chunks[1])
        self.date = utils.parse_date(chunks[2].strip('"'))

    def __str__(self):
        return self.to_readable()

    def to_readable(self):
        return 'Symbol:{} Date:{} Price:{}'.format(self.symbol, self.date, self.price)

    def to_qif(self):
        return '"{}",{},"{}"\n^\n'.format(self.symbol, self.price, utils.date_to_qif(self.date))

    def to_dict(self):
        retdict = {}
        retdict['date'] = self.date
        retdict['price'] = self.price
        retdict['symbol'] = self.symbol
        return retdict

    def validate(self):
        pass
