# Parse transactions and splits

import utils
import logging
logger = logging.getLogger()

class Split:
    def __init__(self, lines=None):
        # common fields
        self.date = None
        self.amount = None
        self.memo = None
        self.status = None

        # split specific
        self.check_num = None
        self.address = None
        self.category = None
        self.memo = None
        self.amount = None
        self.percent = False
        
        if lines:
            self.parse_qif(lines)

    def parse_qif(self, lines):
        for line in lines:
            field,value = utils.parse_field_and_value(line)
            if field == 'S':
                self.category = value
            elif field == 'E':
                if (self.memo):
                    raise Exception("Found duplicate memo. Suspect missing split.")
                self.memo = value
            elif field == '$':
                if (self.amount):
                    raise Exception("Found duplicate amount. Suspect missing split.")
                self.amount = value
            elif field == '%':
                if (self.amount):
                    raise Exception("Found duplicate amount. Suspect missing split.")
                self.amount = value
                self.percent = True

    def __str__(self) -> str:
        return 'Category:{} Amount:{} Memo:{}'.format(self.category, self.amount, self.memo)

    def to_qif(self):
        if self.category:
            qifstr = 'S{}\n'.format(self.category)
        else:
            qifstr = 'S\n'
        if self.memo:
            qifstr += 'E{}\n'.format(self.memo)
        qifstr += '${}\n'.format(self.amount)
        return qifstr

    def to_dict(self):
        retdict = {}
        if self.category:
            retdict['category'] = self.category
        else:
            retdict['category'] = ''
        if self.memo:
            retdict['memo'] = self.memo
        retdict['amount'] = self.amount
        return retdict


class Transaction:
    def __init__(self, lines=None):
        # common fields
        self.date = None
        self.amount = None
        self.memo = None
        self.status = None

        # banking specific
        self.check_num = None
        self.payee = None
        self.address = []
        self.category = None
        self.reimbursable = False

        self.u_val = None

        self.splits = []
        if lines:
            self.parse_qif(lines)

    def parse_qif(self, lines):
        cursplit = None
        for line in lines:
            field,value = utils.parse_field_and_value(line)
            if field is None:
                continue

            if field == 'D':
                self.date = utils.parse_date(value)
            elif field == 'P':
                self.payee = value
            elif field == 'T':
                self.amount = value
            elif field == 'U':
                # Same as 'T' value
                self.u_val = value
            elif field == 'L':
                self.category = value
            elif field == 'N':
                self.check_num = value
            elif field == 'M':
                self.memo = value
            elif field == 'C':
                self.status = value
            elif field == 'F':
                self.reimbursable = True
            elif field == 'A':
                if value is None:
                    value = ''
                self.address.append(value)
            elif field not in ['S', 'E', '$', '%']:
                #ignore other commands
                logger.warning("Unknown parameter in {}: {}".format(self.__class__.__name__, line))
                continue

            # some assumptions about splits:
            # Every split starts with an 'S' field; it does not come in the middle of a split
            # Splits only contain S/E/$. If a different field is encountered, we're no longer in a split
            if field in ['S', 'E', '$', '%']:
                if field == 'S':
                    if cursplit:
                        self.splits.append(cursplit)
                    cursplit = Split()
                cursplit.parse_qif([line])
            elif cursplit:
                self.splits.append(cursplit)
                cursplit = None

        # add the last split
        if cursplit:
            self.splits.append(cursplit)

    def __str__(self):
        return self.to_readable()

    def to_readable(self):
        retstr = 'Date:{} Payee:{} Category:{} Amount:{}\n'.format(self.date, self.payee, self.category, self.amount)
        retstr += '\tStatus:{} Check:{} Memo:{}'.format(self.status, self.check_num, self.memo)
        for s in self.splits:
            retstr += '\n\t' + str(s)
        return retstr

    def to_qif(self):
        qifstr = ''
        if self.date:
            qifstr = 'D{}\n'.format(utils.date_to_qif(self.date))
        if self.amount:
            qifstr += 'U{}\n'.format(self.amount)
            qifstr += 'T{}\n'.format(self.amount)
        if self.status:
            qifstr += 'C{}\n'.format(self.status)
        if self.check_num:
            qifstr += 'N{}\n'.format(self.check_num)
        if self.payee:
            qifstr += 'P{}\n'.format(self.payee)
        if self.memo:
            qifstr += 'M{}\n'.format(self.memo)
        if self.category:
            qifstr += 'L{}\n'.format(self.category)
        if len(self.address) > 0:
            for a in self.address:
                qifstr += 'A{}\n'.format(a)
        for s in self.splits:
            qifstr += s.to_qif()
        qifstr += '^\n'
        return qifstr

    def to_dict(self):
        retdict = {}
        if self.date:
            retdict['date'] = self.date
        if self.amount:
            retdict['amount'] = self.amount
        if self.status:
            retdict['status'] = self.status
        if self.check_num:
            retdict['check_num'] = self.check_num
        if self.payee:
            retdict['payee'] = self.payee
        if self.memo:
            retdict['memo'] = self.memo
        if self.category:
            retdict['category'] = self.category
        if len(self.address) > 0:
            addrlines = ''
            for a in self.address:
                addrlines += '{}\n'.format(a)
            retdict['address'] = addrlines
        if len(self.splits) > 0:
            retdict['splits'] = []
            for s in self.splits:
                retdict['splits'].append(s.to_dict())
        return retdict

    def validate(self):
        if len(self.splits) > 0:
            # check that the total amount of splits matches this transaction amount
            totalsplits = 0
            