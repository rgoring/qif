# Parse the memorized tag

from transaction import Transaction
import utils

import logging
logger = logging.getLogger()

class MemorizedPayee(Transaction):

    def __init__(self, lines=None):
        super(MemorizedPayee, self).__init__()

        self.transaction_type = None

        if lines:
            self.parse_qif(lines)

    def parse_qif(self, lines):
        cursplit = None
        transactionlines = []
        for line in lines:
            field,value = utils.parse_field_and_value(line)
            if field is None:
                continue

            if field == 'K':
                self.transaction_type = value
            else:
                transactionlines.append(line)

        super(MemorizedPayee, self).parse_qif(transactionlines)

    def __str__(self):
        return self.to_readable()

    def to_readable(self):
        retstr = 'TransactionType: {}\n'.format(self.transaction_type)
        retstr += super(MemorizedPayee, self).to_readable()
        return retstr

    def to_qif(self):
        qifstr = 'K{}\n'.format(self.transaction_type)
        qifstr += super(MemorizedPayee, self).to_qif()
        return qifstr

    def to_dict(self):
        retdict = super(MemorizedPayee, self).to_dict()
        retdict['transaction_type'] = self.transaction_type
        return retdict

    def validate(self):
        pass
