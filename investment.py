# Parse the investment tag
import utils
import logging

logger = logging.getLogger()

class Investment:
    def __init__(self, lines=None):
        # common fields
        self.date = None
        self.amount = None
        self.memo = None
        self.status = None

        # investment specific
        self.payee = None
        self.action = None # same as check_num
        self.security = None
        self.price = None
        self.quantity = None
        self.commission = None
        self.txamount = None
        self.category = None
        self.u_val = None
        
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
                # same as 'T'
                self.u_val = value
            elif field == 'L':
                self.category = value
            elif field == 'N':
                self.action = value
            elif field == 'M':
                self.memo = value
            elif field == 'Y':
                self.security = value
            elif field == 'I':
                self.price = value
            elif field == 'Q':
                self.quantity = value
            elif field == 'O':
                self.commission = value
            elif field == '$':
                self.txamount = value
            elif field == 'C':
                self.status = value
            else:
                #ignore other commands
                logger.warning("Unknown parameter in {}: {}".format(self.__class__.__name__, line))
                continue

        # add the last split
        if cursplit:
            self.splits.append(cursplit)

    def __str__(self):
        return self.to_readable()

    def to_readable(self):
        retstr = 'Date:{} Payee:{} Category:{} Action:{} Memo:{}\n'.format(self.date, self.payee, self.category, self.action, self.memo)
        retstr += '\tQuantity:{} Price:{} Amount:{}\n'.format(self.quantity, self.price, self.amount)
        retstr += '\tCommission:{} Security:{} Status:{}'.format(self.commission, self.security, self.status)
        return retstr

    def to_qif(self):
        qifstr = 'D{}\n'.format(utils.date_to_qif(self.date))
        qifstr += 'N{}\n'.format(self.action)
        if self.payee:
            qifstr += 'P{}\n'.format(self.payee)
        if self.security:
            qifstr += 'Y{}\n'.format(self.security)
        if self.price:
            qifstr += 'I{}\n'.format(self.price)
        if self.quantity:
            qifstr += 'Q{}\n'.format(self.quantity)
        if self.status:
            qifstr += 'C{}\n'.format(self.status)
        if self.amount:
            qifstr += 'U{}\n'.format(self.amount)
            qifstr += 'T{}\n'.format(self.amount)
        if self.memo:
            qifstr += 'M{}\n'.format(self.memo)
        if self.commission:
            qifstr += 'O{}\n'.format(self.commission)
        if self.category:
            qifstr += 'L{}\n'.format(self.category)
        if self.txamount:
            qifstr += '${}\n'.format(self.txamount)
        qifstr += '^\n'
        return qifstr

    def to_dict(self):
        retdict = {}
        retdict['date'] = self.date
        retdict['action'] = self.action

        if self.payee:
            retdict['payee'] = self.payee
        if self.security:
            retdict['security'] = self.security
        if self.price:
            retdict['price'] = self.price
        if self.quantity:
            retdict['quantity'] = self.quantity
        if self.status:
            retdict['status'] = self.status
        if self.amount:
            retdict['amount'] = self.amount
        if self.memo:
            retdict['memo'] = self.memo
        if self.commission:
            retdict['commission'] = self.commission
        if self.category:
            retdict['category'] = self.category
        if self.txamount:
            retdict['txamount'] = self.txamount
        return retdict

    def validate(self):
        pass
