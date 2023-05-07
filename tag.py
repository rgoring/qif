# Parse the tag tag
import logging
import  utils

logger = logging.getLogger()

class Tag:
    def __init__(self, lines=None):
        self.name = None
        if lines:
            self.parse_qif(lines)

    def parse_qif(self, lines):
        for line in lines:
            field,value = utils.parse_field_and_value(line)
            if field is None:
                continue

            if field == 'N':
                self.name = value
            else:
                #ignore other commands
                logger.warning("Unknown parameter in tag: {}".format(line))
                continue

    def __str__(self):
        return self.to_readable()

    def to_readable(self):
        return "Name:{}".format(self.name)

    def to_qif(self):
        return 'N{}\n^\n'.format(self.name)

    def to_dict(self):
        retdict = {}
        retdict['name'] = self.name
        return retdict

    def validate(self):
        pass
