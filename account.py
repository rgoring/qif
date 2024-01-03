#Parse the Account tag
import logging
import utils

logger = logging.getLogger()

class Account:
    def __init__(self, lines=None):
        self.name = None
        self.type = None
        self.description = None
        self.transactions = []
        self.credit_limit = None
        self.statement_date = None
        self.statement_bal = None
        if lines:
            self.parse_qif(lines)

    def parse_qif(self, lines):
        for line in lines:
            match utils.parse_field_and_value(line):
                case None: continue
                case ('N', value): self.name           = value
                case ('T', value): self.type           = value
                case ('D', value): self.description    = value
                case ('L', value): self.credit_limit   = value
                case ('/', value): self.statement_date = value
                case ('$', value): self.statement_bal  = value
                case _:
                    # ignore other commands
                    logger.warning(f'Unknown parameter in account: {line}')
                    continue

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def get_type(self):
        if self.type == 'Port' or self.type == '401(k)/403(b)':
            return 'Invst'
        return self.type

    def __str__(self):
        return self.to_readable()

    def to_readable(self):
        return 'Name:{} Type:{} Tx:{}'.format(self.name, self.type, len(self.transactions))

    def to_qif(self, short=True):
        qifstr = 'N{}\n'.format(self.name)
        if not short:
            qifstr += 'T{}\n'.format(self.type)
        else:
            # print the standardized name
            qifstr += 'T{}\n'.format(self.get_type())
        if (not short) and self.credit_limit:
            qifstr += 'L{}\n'.format(self.credit_limit)
        qifstr += '^\n'
        return qifstr

    def to_dict(self):
        retdict = {}
        retdict['name'] = self.name
        retdict['type'] = self.get_type()
        if self.credit_limit:
            retdict['credit_limit'] = self.credit_limit
        return retdict

    def validate(self):
        pass
