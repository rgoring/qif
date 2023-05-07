# Parse the Cat tag

import logging
import utils

logger = logging.getLogger()

class Category:
    def __init__(self, lines=None):
        self.name = None
        self.description = None
        self.type = 'Expense' # Assume expense if omitted
        self.budgetamt = None
        self.taxrelated = False
        self.taxschedule = None
        if lines:
            self.parse_qif(lines)

    def parse_qif(self, lines):
        for line in lines:
            field,value = utils.parse_field_and_value(line)
            if field is None:
                continue

            if field == 'N':
                self.name = value
            elif field == 'D':
                self.description = value
            elif field == 'B':
                self.budgetamt = value
            elif field == 'E':
                self.type = 'Expense'
            elif field == 'I':
                self.type = 'Income'
            elif field == 'T':
                self.taxrelated = True
            elif field == 'R':
                self.taxschedule = value
            else:
                #ignore other commands
                logger.warning("Unknown parameter in category: {}".format(line))
                continue

    def __str__(self):
        return self.to_readable()

    def to_readable(self):
        return 'Name:{} Description:{}'.format(self.name, self.description)

    def to_qif(self):
        qifstr = 'N{}\n'.format(self.name)
        if self.budgetamt:
            qifstr += 'B{}\n'.format(self.budgetamt)
        if self.description:
            qifstr += 'D{}\n'.format(self.description)
        if self.taxrelated:
            qifstr += 'T\n'
        if self.taxschedule:
            qifstr += 'R{}\n'.format(self.taxschedule)
        if self.type == 'Income':
            qifstr += 'I\n'
        else:
            qifstr += 'E\n'
        qifstr += '^\n'
        return qifstr

    def to_dict(self):
        retdict = {}
        retdict['name'] = self.name
        if self.budgetamt:
            retdict['budgetamt'] = self.budgetamt
        if self.description:
            retdict['description'] = self.description
        if self.taxrelated:
            retdict['taxrelated'] = True
        if self.taxschedule:
            retdict['taxschedule'] = self.taxschedule
        if self.type == 'Income':
            retdict['income'] = True
        else:
            retdict['expense'] = True
        return retdict

    def validate(self):
        pass
