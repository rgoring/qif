#!/usr/bin/env python
from account import Account
from tag import Tag
from category import Category
from memorized import MemorizedPayee
from security import Security
from price import Price
from transaction import Transaction
from investment import Investment

import qiflog
import utils
logger = qiflog.init_log()

class Qif:
    def __init__(self):
        self.accounts = []
        self.categories = []
        self.tags = []
        self.memorizedpayees = []
        self.securities = []

    def get_account_by_name(self, name):
        for a in self.accounts:
            if a.name == name:
                return a
        return None

    def get_security(self, symbol):
        for s in self.securities:
            if s.symbol == symbol:
                return s
        return None

    def print_all(self, fmt='txt', file='-'):
        ow = utils.OutputWriter(file)
        if fmt == 'txt':
            self.print_readable(ow)
        elif fmt == 'qif':
            self.print_qif(ow)
        elif fmt == 'dict':
            self.print_dict(ow)
        else:
            raise Exception("Unknown format: {}".format(fmt))

    def print_qif(self, ow):
        # tag list
        ow.write('!Type:Tag\n')
        for t in self.tags:
            ow.write(t.to_qif())

        # category list
        ow.write('!Type:Cat\n')
        for c in self.categories:
            ow.write(c.to_qif())

        # account list
        ow.write('!Account\n')
        for a in self.accounts:
            ow.write(a.to_qif(False))

        # securities
        for s in self.securities:
            ow.write('!Type:Security\n')
            ow.write(s.to_qif())

        # account with transactions
        for a in self.accounts:
            ow.write('!Account\n')
            ow.write(a.to_qif(True))
            ow.write('!Type:{}\n'.format(a.get_type()))
            for t in a.transactions:
                ow.write(t.to_qif())

        # memorized payees
        ow.write('!Type:Memorized\n')
        for m in self.memorizedpayees:
            ow.write(m.to_qif())

        # prices
        for s in self.securities:
            for p in s.pricelist:
                ow.write('!Type:Prices\n')
                ow.write(p.to_qif())

    def print_dict(self, ow):
        # tag list
        ow.write("Tags\n")
        for t in self.tags:
            ow.write(str(t.to_dict()) +'\n')

        # category list
        ow.write("\nCategories\n")
        for c in self.categories:
            ow.write(str(c.to_dict()) +'\n')

        # short account list
        ow.write("\nAccount List\n")
        for a in self.accounts:
            ow.write(str(a.to_dict()) +'\n')

        # securities
        ow.write("\nSecurities\n")
        for s in self.securities:
            ow.write(str(s.to_dict()) +'\n')

        # account with transactions
        ow.write("\nAccount Transactions\n")
        for a in self.accounts:
            ow.write(str(a.to_dict()) +'\n')
            for t in a.transactions:
                ow.write(str(t.to_dict()) +'\n')

        # memorized payees
        ow.write("\nMemorized Payees\n")
        for m in self.memorizedpayees:
            ow.write(str(m.to_dict()) +'\n')

        # prices
        ow.write("\nSecurity Prices\n")
        for s in self.securities:
            ow.write(str(s.to_dict()) +'\n')
            for p in s.pricelist:
                ow.write(str(p.to_dict()) +'\n')


    def print_readable(self, ow):
        # tag list
        ow.write("Tags\n")
        for t in self.tags:
            ow.write(str(t) +'\n')

        # category list
        ow.write("\nCategories\n")
        for c in self.categories:
            ow.write(str(c) +'\n')

        # short account list
        ow.write("\nAccount List\n")
        for a in self.accounts:
            ow.write(str(a) +'\n')

        # securities
        ow.write("\nSecurities\n")
        for s in self.securities:
            ow.write(str(s) +'\n')

        # account with transactions
        ow.write("\nAccount Transactions\n")
        for a in self.accounts:
            ow.write(str(a) +'\n')
            for t in a.transactions:
                ow.write(str(t) +'\n')

        # memorized payees
        ow.write("\nMemorized Payees\n")
        for m in self.memorizedpayees:
            ow.write(str(m) +'\n')

        # prices
        ow.write("\nSecurity Prices\n")
        for s in self.securities:
            ow.write(str(s) +'\n')
            for p in s.pricelist:
                ow.write(str(p) +'\n')

    @classmethod
    def parse_file(cls, file):
        q = cls()

        with open(file) as f:
            recordlines = []
            curaccount = None
            linecount = 0
            for line in f:
                linecount += 1
                line = line.strip()
                if line == "":
                    continue

                #look for a command starting with !
                if line[0] == '!':
                    recordtype = ""
                    recordtypevalue = ""
                    line = line[1:]
                    cmdparts = line.split(':')
                    recordtype = cmdparts[0]
                    if len(cmdparts) > 1:
                        recordtypevalue = cmdparts[1]

                    continue

                #look for  the end of a record with ^
                elif line == '^':
                    #process lines read in current record
                    if recordtype == "Account":
                        #create a new account
                        acc = Account(recordlines)
                        #find an existing account with the same name
                        a = q.get_account_by_name(acc.name)
                        if a is None:
                            q.accounts.append(acc)
                        else:
                            acc = a
                        #set current account to the latest account
                        curaccount = acc
                    elif recordtype == "Type":
                        if recordtypevalue in ["Bank", 'Cash', 'CCard', 'Oth A', 'Oth L', 'Invoice']:
                            tx = Transaction(recordlines)
                            curaccount.add_transaction(tx)
                        elif recordtypevalue == 'Invst':
                            tx = Investment(recordlines)
                            curaccount.add_transaction(tx)
                        elif recordtypevalue == "Cat":
                            cat = Category(recordlines)
                            q.categories.append(cat)
                        elif recordtypevalue == "Memorized":
                            mp = MemorizedPayee(recordlines)
                            q.memorizedpayees.append(mp)
                        elif recordtypevalue == "Prices":
                            pr = Price(recordlines)
                            sec = q.get_security(pr.symbol)
                            if sec is None:
                                raise Exception("Found price without security: {}".format(pr))
                            sec.add_price(pr)
                        elif recordtypevalue == "Security":
                            sec = Security(recordlines)
                            q.securities.append(sec)
                        elif recordtypevalue == "Tag":
                            tag = Tag(recordlines)
                            q.tags.append(tag)
                    elif recordtype == "Option" or recordtype == "Clear":
                        pass
                    else:
                        raise Exception("Reached end of record without type set at {}".format(linecount))

                    #reset the record
                    recordlines = []

                else:
                    #no command.. add it to current record
                    recordlines.append(line)

        return q
