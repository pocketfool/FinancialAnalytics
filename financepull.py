#!/usr/bin/env python

import json
import pprint
import urllib2


def get_stock_quote(ticker_symbol):   
    url = 'http://finance.google.com/finance/info?q=%s' % ticker_symbol
    lines = urllib2.urlopen(url).read().splitlines()
    return json.loads(''.join([x for x in lines if x not in ('// [', ']')]))


if __name__ == '__main__':
    quote = get_stock_quote('IBM')
    print 'ticker: %s' % quote['t']
    print 'current price: %s' % quote['l_cur']
    print 'last trade: %s' % quote['lt']
    print 'full quote:'
    pprint.pprint(quote)