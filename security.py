# Parse the security tag
import logging
import utils

logger = logging.getLogger()

class Security:
    def __init__(self, lines=None):
        self.name = None
        self.symbol = None
        self.type = None
        self.pricelist = []
        if lines:
            self.parse_qif(lines)

    def add_price(self, price):
        self.pricelist.append(price)

    def parse_qif(self, lines):
        for line in lines:
            field,value = utils.parse_field_and_value(line)
            if field is None:
                continue

            if field == 'N':
                self.name = value
            elif field == 'S':
                self.symbol = value
            elif field == 'T':
                self.type = value
            else:
                #ignore other commands
                logger.warning("Unknown parameter in security: {}".format(line))
                continue

    def __str__(self):
        return self.to_readable()

    def to_readable(self):
        return 'Name:{} Symbol:{} Type:{} Prices:{}'.format(self.name, self.symbol, self.type, len(self.pricelist))

    def to_qif(self):
        qifstr = 'N{}\n'.format(self.name)
        if self.symbol:
            qifstr += 'S{}\n'.format(self.symbol)
        qifstr += 'T{}\n'.format(self.type)
        qifstr += '^\n'
        return qifstr

    def to_dict(self):
        retdict = {}
        retdict['name'] = self.name
        if self.symbol:
            retdict['symbol'] = self.symbol
        retdict['type'] = self.type
        return retdict

    def validate(self):
        if self.symbol is None:
            raise Exception("No symbol available for security {}".format(self.name))

