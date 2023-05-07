import sys

def parse_date(datestr):
    datestr = datestr.replace(' ', '0')
    datestr = datestr.replace("'", '/')

    #XX0XX0XXXX
    if len(datestr) == 8 and datestr[2] == '0' and datestr[5] == '0':
        datestr = datestr[:2] + '/' + datestr[3:]
        datestr = datestr[:5] + '/' + datestr[6:]
    return datestr

def date_to_qif(datestr):
    datestr = datestr.replace('/0', '/ ')

    # year separator replaced with a quote, unless year < 2000
    idx = datestr.rfind('/')
    year = int(datestr[idx+1:])
    if year < 50:
        datestr = datestr[:idx] + "'" + datestr[idx+1:]

    #leading 0 is replaced with a space:
    if datestr[0] == '0':
        datestr = ' ' + datestr[1:]
    return datestr

def read_price(pricestr):
    pricestr = pricestr.replace(' 1/4', '.25')
    pricestr = pricestr.replace(' 1/2', '.50')
    pricestr = pricestr.replace(' 3/4', '.75')

    if pricestr.find('.') == -1:
        pricestr = pricestr + '.00'

    return pricestr

def parse_field_and_value(line):
    if len(line) > 0:
        field = line[0]
    else:
        field = None

    if field == '':
        field = None

    if len(line) > 1:
        value = line[1:]
    else:
        value = None

    return field, value

class OutputWriter:
    def __init__(self, stream='='):
        self.output = None

        if stream == '-':
            self.output = sys.stdout
        else:
            self.output = open(stream, 'w')

    def write(self, *args):
        self.output.write(*args)